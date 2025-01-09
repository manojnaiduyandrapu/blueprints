from loguru import logger
import httpx
from typing import Optional, List
from math import radians, cos, sin, asin, sqrt
from serpapi import GoogleSearch  
from dotenv import load_dotenv
import os
import sys
import googlemaps
from openai import OpenAI
from utils import fetch_external_url_content, map_weather_code_to_description
import re
from datetime import datetime, timedelta, timezone
from models import AccommodationPreferences
from agentifyme import task

# Load environment variables from .env file
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')

# Validate that the API keys are available
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY not found. Please set it in your .env file.")
    sys.exit(1)
if not GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY not found. Please set it in your .env file.")
    sys.exit(1)
if not SERPAPI_API_KEY:
    logger.error("SERPAPI_API_KEY not found. Please set it in your .env file.")
    sys.exit(1)

# Initialize APIs
client = OpenAI(api_key=OPENAI_API_KEY)
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

# ----------------------- Flight Functions -----------------------
@task(name="fetch-flight-results", description="Fetches flight results from SerpAPI based on provided parameters.")
async def fetch_flight_results(departure_id: str, arrival_id: str, outbound_date: str, return_date: str):
    """
    Fetches flight results from SerpAPI based on provided parameters.
    """
    params = {
        "engine": "google_flights",
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": outbound_date,
        "return_date": return_date,
        "currency": "USD",
        "hl": "en",
        "api_key": SERPAPI_API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    logger.info("Fetched flight results from SerpAPI.")
    return results

@task(name="fetch-inbound-flights", description="Fetches inbound flight results from SerpAPI using the provided departure_token along with other parameters.")
async def fetch_inbound_flights(departure_id: str, arrival_id: str, outbound_date: str, return_date: str, departure_token: str):
    """
    Fetches inbound flight results from SerpAPI using the provided departure_token along with other parameters.
    """
    params = {
        "engine": "google_flights",
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": outbound_date,
        "return_date": return_date,
        "currency": "USD",
        "hl": "en",
        "departure_token": departure_token,
        "api_key": SERPAPI_API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    logger.info("Fetched inbound flight results from SerpAPI using departure_token.")
    return results

@task(name="extract-flight-details", description="Extracts relevant flight details from SerpAPI response.")
async def extract_flight_details(results):
    """
    Extracts relevant flight details from SerpAPI response.
    """
    flight_data = []

    best_flights = results.get("best_flights", [])
    other_flights = results.get("other_flights", [])

    if not best_flights:
        logger.info("No best flights found, falling back to other flights.")
        best_flights = other_flights

    for flight in best_flights:
        details = flight["flights"][0]
        flight_details = {
            "departure": f'{details["departure_airport"]["name"]} ({details["departure_airport"]["id"]})',
            "arrival": f'{details["arrival_airport"]["name"]} ({details["arrival_airport"]["id"]})',
            "departure_time": details["departure_airport"]["time"],
            "arrival_time": details["arrival_airport"]["time"],
            "duration(mins)": details["duration"],
            "airplane": details["airplane"],
            "travel_class": details["travel_class"],
            "flight_number": details["flight_number"],
            "legroom": details.get("legroom", "N/A"),
            "price": flight.get("price", "N/A"),
            "departure_token": flight.get("departure_token"),
        }
        flight_data.append(flight_details)

    logger.info(f"Extracted {len(flight_data)} flight details.")
    return flight_data

# ----------------------- Hotel Functions -----------------------
@task(name="fetch-hotels", description="Fetches hotel results from SerpAPI based on provided parameters.")
async def fetch_hotels(destination: str, check_in_date: str, check_out_date: str, adults: int = 2, children: int = 0):
    """
    Fetches hotel results from SerpAPI based on provided parameters (destination, check-in/check-out dates, and number of guests).
    """
    params = {
        'engine': 'google_hotels',
        'q': f'{destination} Hotels',
        'gl': 'us',
        'hl': 'en',
        'currency': 'USD',
        'check_in_date': check_in_date,
        'check_out_date': check_out_date,
        'adults': adults,
        'children': children,
        'api_key': SERPAPI_API_KEY
    }
    url = 'https://serpapi.com/search'
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    logger.info("Fetched hotel results from SerpAPI.")
    return data

@task(name="extract-top-5-hotels", description="Extracts the top 5 hotel details from the SerpAPI response.")
async def extract_top_5_hotels(response):
    """
    Extracts the top 5 hotel details (like name, type, check-in/out times, rates, amenities, etc.) 
    from the SerpAPI response.
    """
    hotels = []
    properties = response.get("properties", [])
    if not properties:
        logger.warning("No properties found in SerpAPI hotel response.")
        return hotels

    for hotel in properties[:5]:
        hotel_info = {
            "name": hotel.get("name", "Not Available"),
            "type": hotel.get("type", "Not Available"),
            "check_in_time": hotel.get("check_in_time", "Not Available"),
            "check_out_time": hotel.get("check_out_time", "Not Available"),
            "rate_per_night": hotel.get("rate_per_night", {}).get("lowest", "Not Available"),
            "before_taxes_fees": hotel.get("rate_per_night", {}).get("before_taxes_fees", "Not Available"),
            "total_rate": hotel.get("total_rate", {}).get("lowest", "Not Available"),
            "prices": hotel.get("prices", [{}])[0].get("rate_per_night", {}).get("lowest", "Not Available"),
            "overall_rating": hotel.get("overall_rating", "Not Available"),
            "amenities": ", ".join(hotel.get("amenities", [])) or "Not Available",
            "nearby_places": ", ".join([place['name'] for place in hotel.get('nearby_places', [])]) or "Not Available",
            "gps_coordinates": hotel.get("gps_coordinates", "Not Available"),
            "address": hotel.get("address", "Not Available")
        }
        hotels.append(hotel_info)
    
    logger.info(f"Extracted top {len(hotels)} hotel details.")
    return hotels

# ----------------------- Wikipedia Functions -----------------------
@task(name="get-wikipedia-sections", description="Fetches the list of sections from a Wikipedia page for the given destination.")
async def get_wikipedia_sections(destination: str) -> list[dict]:
    """
    Fetches the sections available in the Wikipedia page for the given destination.
    """
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        'action': 'parse',
        'page': destination,
        'format': 'json',
        'prop': 'sections'
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers={'User-Agent': 'travel-planner-app/0.1'})
        response.raise_for_status()
        data = response.json()

    if 'parse' in data:
        return data['parse'].get('sections', [])
    else:
        logger.warning(f"No sections found for {destination} on Wikipedia.")
        return []

@task(name="get-wikipedia-info", description="Fetches specific sections and summary from a Wikipedia page for the given destination.")
async def get_wikipedia_info(destination: str, desired_sections=None):
    """
    Fetches the summary and specific sections (e.g. 'Culture', 'Tourism') from the Wikipedia page for a given destination.
    """
    if desired_sections is None:
        desired_sections = ['Culture', 'Tourism']

    url = "https://en.wikipedia.org/w/api.php"
    params = {
        'action': 'parse',
        'page': destination,
        'format': 'json',
        'prop': 'text',
        'section': 0
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers={'User-Agent': 'travel-planner-app/0.1'})
        response.raise_for_status()
        data = response.json()

    wiki_data = {}
    if 'parse' in data and 'text' in data['parse']:
        summary = data['parse']['text']['*']
        wiki_data['Summary'] = summary
    else:
        logger.warning("No summary available for this destination on Wikipedia.")

    sections = get_wikipedia_sections(destination)
    for section_title in desired_sections:
        section_number = None
        for section in sections:
            if section['line'].lower() == section_title.lower():
                section_number = section['index']
                break

        if section_number:
            section_params = {
                'action': 'parse',
                'page': destination,
                'format': 'json',
                'prop': 'text',
                'section': section_number
            }
            async with httpx.AsyncClient() as client:
                section_response = await client.get(url, params=section_params, headers={'User-Agent': 'travel-planner-app/0.1'})
                section_response.raise_for_status()
                section_data = section_response.json()

            if 'parse' in section_data and 'text' in section_data['parse']:
                section_text = section_data['parse']['text']['*']
                wiki_data[section_title] = section_text
            else:
                logger.warning(f"No data available for section: {section_title}")
        else:
            logger.warning(f"Section '{section_title}' not found in Wikipedia page for {destination}.")

    return wiki_data, data

# ----------------------- Reddit Functions -----------------------
@task(name="get-reddit-posts", description="Fetches recent posts related to the destination from a specific subreddit.")
async def get_reddit_posts(destination: str, subreddit='travel', limit=5):
    """
    Fetches recent Reddit posts related to the specified destination from a given subreddit.
    Also fetches external content (if post content is empty) and top comments for each post.
    """
    headers = {'User-Agent': 'travel-planner-app/0.1'}
    url = f"https://www.reddit.com/r/{subreddit}/search.json"
    params = {
        'q': destination,
        'sort': 'new',
        'limit': limit,
        'restrict_sr': True
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

    posts = data['data']['children']
    post_list = []

    for post in posts:
        post_data = post['data']
        post_info = {
            'content': post_data.get('selftext', ''),
            'external_content': '',
            'permalink': post_data.get('permalink', '')
        }
        if not post_info['content'] and post_data.get('url'):
            external_content = fetch_external_url_content(post_data['url'])
            post_info['external_content'] = external_content

        comments = get_reddit_comments(post_info['permalink'], limit=3)
        post_info['comments'] = comments
        post_list.append(post_info)

    return post_list, data

@task(name="get-reddit-comments", description="Fetches the top comments from a specific Reddit post.")
async def get_reddit_comments(permalink: str, limit=5):
    """
    Fetches the top comments (up to the specified limit) from a Reddit post using its permalink.
    """
    headers = {'User-Agent': 'travel-planner-app/0.1'}
    url = f"https://www.reddit.com{permalink}.json"
    params = {
        'limit': limit,
        'depth': 1
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

        comments = []
        if len(data) > 1:
            comments_data = data[1]['data']['children']
            for comment in comments_data:
                if comment['kind'] == 't1':
                    comment_body = comment['data'].get('body', '')
                    if comment_body:
                        comments.append(comment_body)
        return comments
    except Exception as e:
        logger.error(f"Error fetching comments from Reddit post {permalink}: {e}")
        return []

# ----------------------- Geocoding and IATA Functions -----------------------
@task(name="get-geo-coordinates", description="Fetches the geographical coordinates (latitude and longitude) of the given destination.")
async def get_geo_coordinates(destination: str, fallback_city: Optional[str] = None):
    """
    Fetches the geographical coordinates (latitude and longitude) using Google Maps Geocoding API for the given destination.
    If 'destination' is 'Not Available' or fails to geocode, and a fallback_city is provided, 
    it will try the fallback city name instead.
    """
    if not destination or destination.lower() == "not available":
        if fallback_city:
            logger.warning(
                f"Hotel address is '{destination}'. Falling back to city name: '{fallback_city}'"
            )
            geocode_result = gmaps.geocode(fallback_city)
            if geocode_result:
                location = geocode_result[0]["geometry"]["location"]
                return (location["lat"], location["lng"])
            else:
                logger.error(f"No geocoding results found for fallback city '{fallback_city}'.")
                return (None, None)
        else:
            logger.error("No valid destination or fallback provided.")
            return (None, None)

    geocode_result = gmaps.geocode(destination)
    if geocode_result:
        location = geocode_result[0]["geometry"]["location"]
        return (location["lat"], location["lng"])
    else:
        logger.error(f"No geocoding results found for '{destination}'.")
        if fallback_city:
            logger.warning(
                f"Could not geocode '{destination}'. Trying fallback city: '{fallback_city}'"
            )
            geocode_result = gmaps.geocode(fallback_city)
            if geocode_result:
                location = geocode_result[0]["geometry"]["location"]
                return (location["lat"], location["lng"])
            else:
                logger.error(f"No geocoding results found even for fallback city '{fallback_city}'.")
                return (None, None)
        return (None, None)

@task(name="get-iata-code-openai", description="Fetches the IATA code for the main international airport in a city using OpenAI.")
async def get_iata_code_openai(city: str) -> Optional[str]:
    """
    Uses OpenAI to determine the IATA code for the main international airport in a specified city.
    """
    prompt = f"What is the IATA code for the main international airport in {city}?"
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a knowledgeable assistant that provides accurate IATA airport codes."},
                {"role": "user", "content": prompt}
            ],
            model="gpt-4o-mini",
            temperature=0
        )
        assistant_reply = response.choices[0].message.content.strip()
        logger.info(f"OpenAI response for IATA code of {city}: {assistant_reply}")
        match = re.search(r'\b([A-Z]{3})\b', assistant_reply)
        if match:
            return match.group(1)
        else:
            logger.error(f"Could not extract IATA code from OpenAI response: {assistant_reply}")
            return None
    except Exception as e:
        logger.error(f"Error fetching IATA code from OpenAI for city '{city}': {e}")
        return None

# ----------------------- Weather Functions -----------------------
@task(name="get-weather-forecast", description="Fetches weather forecast or historical weather data for a given location and date range.")
async def get_weather_forecast(lat: float, lon: float, start_date: datetime, end_date: datetime):
    """
    Fetches weather forecast (or historical data if the dates are in the past) for a given latitude and longitude,
    and returns a textual summary along with structured weather information.
    """
    today = datetime.now(timezone.utc).date()
    if end_date.date() < today:
        logger.info("Fetching historical weather data using ERA5 API.")
        url = "https://archive-api.open-meteo.com/v1/era5"
        params = {
            'latitude': lat,
            'longitude': lon,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'hourly': 'temperature_2m,relative_humidity_2m,wind_speed_10m,weathercode',
            'timezone': 'auto'
        }
    else:
        logger.info("Fetching weather forecast data using Forecast API.")
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': lat,
            'longitude': lon,
            'current_weather': 'true',
            'hourly': 'temperature_2m,relative_humidity_2m,wind_speed_10m,weathercode',
            'daily': 'temperature_2m_max,temperature_2m_min,weathercode',
            'timezone': 'auto',
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    if "daily" in data and "weathercode" in data['daily']:
        logger.info("Processing Forecast API data.")
        forecast_info = "Weather Forecast:\n"
        weather_info = {}
        for i in range(len(data['daily']['time'])):
            date_str = data['daily']['time'][i]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            day_of_week = date_obj.strftime('%A')
            temp_max = data['daily']['temperature_2m_max'][i]
            temp_min = data['daily']['temperature_2m_min'][i]
            weather_code = data['daily']['weathercode'][i]
            weather_description = map_weather_code_to_description(weather_code)
            forecast_info += f"- **{day_of_week}, {date_obj.strftime('%B %d')}**:\n"
            forecast_info += f"  - Description: {weather_description}\n"
            forecast_info += f"  - Temperature: {temp_min}°C (Min) / {temp_max}°C (Max)\n\n"
            weather_info[date_str] = {
                'description': weather_description,
                'temp_day': temp_max,
                'temp_night': temp_min
            }
        return forecast_info, weather_info

    elif "hourly" in data and "weathercode" in data['hourly']:
        logger.info("Processing ERA5 Historical API data.")
        forecast_info = "Historical Weather Data:\n"
        weather_info = {}
        daily_temp_max = {}
        daily_temp_min = {}
        daily_weather_codes = {}
        for i, date_str in enumerate(data['hourly']['time']):
            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M").date()
            temp = data['hourly']['temperature_2m'][i]
            wcode = data['hourly']['weathercode'][i]
            if date_obj not in daily_temp_max or temp > daily_temp_max[date_obj]:
                daily_temp_max[date_obj] = temp
            if date_obj not in daily_temp_min or temp < daily_temp_min[date_obj]:
                daily_temp_min[date_obj] = temp
            daily_weather_codes[date_obj] = wcode
        for date_obj in sorted(daily_temp_max.keys()):
            day_of_week = date_obj.strftime('%A')
            temp_max = daily_temp_max[date_obj]
            temp_min = daily_temp_min[date_obj]
            weather_code = daily_weather_codes[date_obj]
            weather_description = map_weather_code_to_description(weather_code)
            forecast_info += f"- **{day_of_week}, {date_obj.strftime('%B %d')}**:\n"
            forecast_info += f"  - Description: {weather_description}\n"
            forecast_info += f"  - Temperature: {temp_min}°C (Min) / {temp_max}°C (Max)\n\n"
            weather_info[date_obj.strftime('%Y-%m-%d')] = {
                'description': weather_description,
                'temp_day': temp_max,
                'temp_night': temp_min
            }
        return forecast_info, weather_info

    else:
        logger.error("Unexpected data structure received from Weather API.")
        return "Weather data is currently unavailable.", None

# ----------------------- Distance Functions -----------------------
@task(name="calculate-haversine-distance", description="Calculates the haversine distance between two geographical coordinates.")
async def calculate_haversine_distance(coord1: tuple, coord2: tuple) -> float:
    """
    Calculates the haversine distance between two geographical coordinates (latitude and longitude) in kilometers.
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r

@task(name="get-flight-distance", description="Calculates the straight-line distance between two locations.")
async def get_flight_distance(origin: str, destination: str) -> Optional[float]:
    """
    Calculates the straight-line (haversine) distance between two locations, identified by their names/addresses.
    """
    coord1 = get_geo_coordinates(origin)
    coord2 = get_geo_coordinates(destination)
    if coord1 and coord2:
        distance = calculate_haversine_distance(coord1, coord2)
        logger.info(f"Straight-line distance between {origin} and {destination}: {distance:.2f} km")
        return distance
    else:
        logger.error(f"Could not calculate distance between {origin} and {destination}.")
        return None

@task(name="get-distance-duration", description="Fetches the distance and travel duration between two locations using Google Distance Matrix API.")
async def get_distance_duration(origin: str, destination: str, mode: str = "driving") -> Optional[dict]:
    """
    Uses Google Distance Matrix API to fetch the distance and travel duration between two locations
    in the specified mode (driving, walking, etc.).
    """
    logger.info(f"Fetching distance and duration from {origin} to {destination} (mode={mode}).")
    result = gmaps.distance_matrix(
        origins=[origin],
        destinations=[destination],
        mode=mode,
        units="metric"
    )
    if result['status'] != 'OK':
        logger.error(f"Error from Distance Matrix API: {result['status']}")
        return None

    element = result['rows'][0]['elements'][0]
    if element['status'] != 'OK':
        logger.error(f"Element status not OK: {element['status']}")
        return None

    distance = element['distance']
    duration = element['duration']
    logger.info(f"Distance: {distance['text']}, Duration: {duration['text']}")
    return {
        'distance_text': distance['text'],
        'distance_value': distance['value'],
        'duration_text': duration['text'],
        'duration_value': duration['value']
    }

# ----------------------- Hotel and Flight Deals -----------------------
@task(name="find-nearby-places", description="Finds nearby places of a specific type within a radius of the given location.")
async def find_nearby_places(location: tuple, radius: int = 10000, place_type: str = "tourist_attraction") -> List[dict]:
    """
    Finds nearby places of a given type (e.g. tourist_attraction, restaurant, etc.) within a specified radius in meters
    around the given geographical location (latitude, longitude).
    """
    logger.info(f"Searching for nearby places around {location} within {radius} meters.")
    response = gmaps.places_nearby(
        location=location,
        radius=radius,
        type=place_type
    )
    places = response.get('results', [])
    logger.info(f"Found {len(places)} nearby places.")
    return places

@task(name="get-nights", description="Calculates the number of nights between two dates.")
async def get_nights(start_date: datetime, end_date: datetime) -> int:
    """
    Calculates the number of nights between two dates.
    """
    delta = end_date - start_date
    return delta.days

@task(name="get-hotel-deals", description="Fetches top hotel deals based on destination, dates, budget, and preferences.")
async def get_hotel_deals(destination: str, start_date: datetime, end_date: datetime,
                          budget: Optional[float] = None,
                          accommodation_prefs: Optional[AccommodationPreferences] = None) -> List[dict]:
    """
    Fetches top hotel deals based on the provided destination, date range, budget, 
    and accommodation preferences, returning a list of top hotels.
    """
    data = fetch_hotels(destination, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    top_hotels = extract_top_5_hotels(data)
    return top_hotels

@task(name="get-flight-deals", description="Fetches top flight deals based on IATA codes and travel dates.")
async def get_flight_deals(origin_iata: str, destination_iata: str,
                           start_date: datetime, end_date: datetime) -> List[dict]:
    """
    Fetches top flight deals based on the provided origin and destination IATA codes,
    as well as the specified travel dates, returning a list of flight deals.
    """
    results = fetch_flight_results(
        origin_iata, destination_iata,
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )
    flight_data = extract_flight_details(results) 
    return flight_data

