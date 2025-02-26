import os
import time
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
import wikipedia
import httpx
import requests
import googlemaps
from serpapi import GoogleSearch
from agentifyme import task  

# ---------------------------
# Helper Functions
# ---------------------------
@task(name="get-current-date", description="Returns the current date in YYYY-MM-DD format.")
def get_current_date() -> str:
    """
    Returns the current date in YYYY-MM-DD format.

    Args:
        None

    Returns:
        str: The current date as a string in YYYY-MM-DD format.
    """
    return datetime.now().strftime('%Y-%m-%d')

# ---------------------------
# Wikipedia Functions
# ---------------------------
@task(name="search-wikipedia", description="Fetches Wikipedia content for a given query.")
def search_wikipedia(query: str) -> dict:
    """
    Fetches Wikipedia content for a given query.

    Args:
        query (str): The search term for Wikipedia.

    Returns:
        dict: A dictionary containing 'title', 'content', and 'url'. If no results are found, returns empty values.
    """
    try:
        page = wikipedia.page(query)
        return {
            "title": page.title,
            "content": page.content[:500] + ("..." if len(page.content) > 500 else ""),
            "url": page.url,
        }
    except Exception:
        return {"title": "", "content": "No results found", "url": ""}

# ---------------------------
# Flight Functions
# ---------------------------
@task(name="fetch-flight-results", description="Fetches flight results from SerpAPI based on provided parameters.")
def fetch_flight_results(departure_id: str, arrival_id: str, outbound_date: str, return_date: str) -> dict:
    """
    Fetches flight results from SerpAPI based on provided parameters.

    Args:
        departure_id (str): IATA code for the departure airport.
        arrival_id (str): IATA code for the arrival airport.
        outbound_date (str): Outbound flight date in YYYY-MM-DD format.
        return_date (str): Return flight date in YYYY-MM-DD format, or an empty string for one-way flights.

    Returns:
        dict: A dictionary containing flight search results.
    """
    flight_type = 2 if return_date == "" else 1
    params = {
        "engine": "google_flights",
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": outbound_date,
        "return_date": return_date,
        "currency": "USD",
        "hl": "en",
        "type": flight_type,
        "api_key": os.getenv('SERPAPI_API_KEY')
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results

@task(name="fetch-inbound-flights", description="Fetches inbound flight results using the provided departure token.")
def fetch_inbound_flights(departure_id: str, arrival_id: str, outbound_date: str, return_date: str, departure_token: str) -> dict:
    """
    Fetches inbound flight results using the provided departure token.

    Args:
        departure_id (str): IATA code for the departure airport.
        arrival_id (str): IATA code for the arrival airport.
        outbound_date (str): Outbound flight date (YYYY-MM-DD).
        return_date (str): Return flight date (YYYY-MM-DD).
        departure_token (str): Token required to fetch inbound flights.

    Returns:
        dict: A dictionary containing inbound flight results.
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
        "api_key": os.getenv('SERPAPI_API_KEY')
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results

@task(name="extract-flight-details", description="Extracts flight details from SerpAPI results.")
def extract_flight_details(results: dict) -> List[dict]:
    """
    Extracts flight details from SerpAPI results.

    Args:
        results (dict): The JSON dictionary returned by SerpAPI.

    Returns:
        List[dict]: A list of dictionaries, each containing details of a flight option.
    """
    flight_data = []
    best_flights = results.get("best_flights", [])
    other_flights = results.get("other_flights", [])
    all_flights = best_flights + other_flights

    for flight in all_flights:
        details = flight["flights"][0]
        flight_details = {
            "departure": f'{details["departure_airport"]["name"]} ({details["departure_airport"]["id"]})',
            "arrival": f'{details["arrival_airport"]["name"]} ({details["arrival_airport"]["id"]})',
            "departure_time": details["departure_airport"]["time"],
            "arrival_time": details["arrival_airport"]["time"],
            "duration(mins)": details["duration"],
            "airplane": details.get("airplane", "Unknown Aircraft"),
            "airline": details["airline"],
            "travel_class": details["travel_class"],
            "flight_number": details["flight_number"],
            "legroom": details.get("legroom", "N/A"),
            "price": flight.get("price", "N/A"),
            "departure_token": flight.get("departure_token"),
        }
        flight_data.append(flight_details)
    return flight_data

@task(name="get-flight-deals", description="Fetches flight deals based on origin/destination and travel dates.")
def get_flight_deals(origin_iata: str, destination_iata: str,
                     start_date: datetime, end_date: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Fetches flight deals based on origin/destination IATA codes and travel dates.

    Args:
        origin_iata (str): IATA code for the origin.
        destination_iata (str): IATA code for the destination.
        start_date (datetime): The start date for travel.
        end_date (Optional[datetime]): The end date for travel; if None or same as start_date, treated as one-way.

    Returns:
        Dict[str, Any]: A dictionary with keys "outbound" and "inbound" containing flight options.
    """
    outbound_date = start_date.strftime('%Y-%m-%d')
    if end_date is None or end_date.strftime('%Y-%m-%d') == outbound_date:
        outbound_results = fetch_flight_results(origin_iata, destination_iata, outbound_date, "")
        outbound_flights = extract_flight_details(outbound_results)
        return {"outbound": outbound_flights, "inbound": []}
    
    return_date = end_date.strftime('%Y-%m-%d')
    outbound_results = fetch_flight_results(origin_iata, destination_iata, outbound_date, return_date)
    outbound_flights = extract_flight_details(outbound_results)
    
    inbound_flights = []
    if outbound_flights and outbound_flights[0].get("departure_token"):
        departure_token = outbound_flights[0]["departure_token"]
        inbound_results = fetch_inbound_flights(origin_iata, destination_iata, outbound_date, return_date, departure_token)
        inbound_flights = extract_flight_details(inbound_results)
    
    return {"outbound": outbound_flights, "inbound": inbound_flights}

@task(name="format-flight-deals", description="Formats the flight deals into a human-readable string.")
def format_flight_deals(deals: Dict[str, Any], origin: str, destination: str, outbound_date: str, return_date: str) -> str:
    """
    Formats flight deals into a human-readable string.

    Args:
        deals (Dict[str, Any]): The dictionary containing flight deal data.
        origin (str): The origin (IATA code or city name).
        destination (str): The destination (IATA code or city name).
        outbound_date (str): The outbound flight date.
        return_date (str): The return flight date.

    Returns:
        str: A formatted string describing the flight options.
    """
    outbound_flights = deals.get("outbound", [])
    inbound_flights = deals.get("inbound", [])
    
    response_text = (
        f"Here are some flight options for your trip from {origin} to {destination} on {outbound_date}"
    )
    if return_date and return_date != outbound_date:
        response_text += f", returning on {return_date}:\n\n### Outbound Flight Options\n"
    else:
        response_text += " (One-way):\n\n### Outbound Flight Options\n"
    
    if not outbound_flights:
        response_text += "No outbound flights found.\n"
    else:
        for idx, flight in enumerate(outbound_flights, 1):
            airline = flight.get("airline", flight.get("airplane", "Airline"))
            response_text += (
                f"{idx}. **{airline}**\n"
                f"   - **Aircraft:** {flight.get('airplane', 'Unknown Aircraft')}\n"
                f"   - **Departure:** {flight.get('departure')} at {flight.get('departure_time')}\n"
                f"   - **Arrival:** {flight.get('arrival')} at {flight.get('arrival_time')}\n"
                f"   - **Duration:** {flight.get('duration(mins)')} mins\n"
                f"   - **Flight Number:** {flight.get('flight_number')}\n"
                f"   - **Price:** {flight.get('price')}\n"
                f"   - **Legroom:** {flight.get('legroom')}\n\n"
            )
    
    if inbound_flights:
        response_text += "### Inbound Flight Options\n"
        for idx, flight in enumerate(inbound_flights, 1):
            airline = flight.get("airline", flight.get("airplane", "Airline"))
            response_text += (
                f"{idx}. **{airline}**\n"
                f"   - **Aircraft:** {flight.get('airplane', 'Unknown Aircraft')}\n"
                f"   - **Departure:** {flight.get('departure')} at {flight.get('departure_time')}\n"
                f"   - **Arrival:** {flight.get('arrival')} at {flight.get('arrival_time')}\n"
                f"   - **Duration:** {flight.get('duration(mins)')} mins\n"
                f"   - **Flight Number:** {flight.get('flight_number')}\n"
                f"   - **Price:** {flight.get('price')}\n"
                f"   - **Legroom:** {flight.get('legroom')}\n\n"
            )
    else:
        if return_date and return_date != outbound_date:
            response_text += "No inbound flights found.\n"
    
    return response_text

# ---------------------------
# Hotel Functions
# ---------------------------
@task(name="fetch-hotels", description="Fetches hotel results from SerpAPI based on destination and dates.")
def fetch_hotels(destination: str, check_in_date: str, check_out_date: str, adults: int = 2, children: int = 0) -> dict:
    """
    Fetches hotel results from SerpAPI based on destination and check-in/out dates.

    Args:
        destination (str): The destination city or location.
        check_in_date (str): Check-in date in YYYY-MM-DD format.
        check_out_date (str): Check-out date in YYYY-MM-DD format.
        adults (int): Number of adults (default is 2).
        children (int): Number of children (default is 0).

    Returns:
        dict: A dictionary containing hotel property information.
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
        'api_key': os.getenv('SERPAPI_API_KEY')
    }
    url = 'https://serpapi.com/search'
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        return {"properties": []}
    return data

@task(name="extract-top-5-hotels", description="Extracts the top 5 hotels from the fetched hotel data.")
def extract_top_5_hotels(response: dict) -> List[dict]:
    """
    Extracts the top 5 hotels from the hotel data response.

    Args:
        response (dict): The JSON response from the hotel search.

    Returns:
        List[dict]: A list of dictionaries, each containing hotel details.
    """
    hotels = []
    properties = response.get("properties", [])
    if not properties:
        return hotels

    for hotel in properties[:5]:
        hotel_info = {
            "name": hotel.get("name", "Not Available"),
            "type": hotel.get("type", "Not Available"),
            "check_in_time": hotel.get("check_in_time", "Not Available"),
            "check_out_time": hotel.get("check_out_time", "Not Available"),
            "rate_per_night": hotel.get("rate_per_night", {}).get("lowest", "Not Available"),
            "overall_rating": hotel.get("overall_rating", "Not Available"),
            "amenities": ", ".join(hotel.get("amenities", [])) or "Not Available",
            "address": hotel.get("address", "Not Available")
        }
        hotels.append(hotel_info)
    return hotels

@task(name="get-hotel-deals", description="Retrieves hotel deals by fetching and extracting hotel information.")
def get_hotel_deals(destination: str, start_date: datetime, end_date: datetime,
                    budget: Optional[float] = None,
                    accommodation_prefs: Optional[Any] = None) -> List[dict]:
    """
    Retrieves hotel deals by fetching hotel data and extracting the top hotels.

    Args:
        destination (str): The destination city or location.
        start_date (datetime): The check-in date.
        end_date (datetime): The check-out date.
        budget (Optional[float]): An optional budget constraint.
        accommodation_prefs (Optional[Any]): Additional preferences.

    Returns:
        List[dict]: A list of hotel detail dictionaries.
    """
    data = fetch_hotels(destination, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    top_hotels = extract_top_5_hotels(data)
    return top_hotels

@task(name="format-hotel-deals", description="Formats the hotel deals into a human-readable string.")
def format_hotel_deals(hotels: List[dict], destination: str, check_in_date: str, check_out_date: str) -> str:
    """
    Formats hotel deals into a human-readable string.

    Args:
        hotels (List[dict]): A list of hotel details.
        destination (str): The destination city.
        check_in_date (str): Check-in date.
        check_out_date (str): Check-out date.

    Returns:
        str: A formatted string describing the hotel options.
    """
    response_text = (
        f"Here are the top hotel options in {destination} from {check_in_date} to {check_out_date}:\n\n"
    )
    if not hotels:
        response_text += "No hotels found.\n"
        return response_text
    for idx, hotel in enumerate(hotels, 1):
        response_text += (
            f"{idx}. **{hotel.get('name', 'Hotel Name')}**\n"
            f"   - **Type:** {hotel.get('type')}\n"
            f"   - **Check-in Time:** {hotel.get('check_in_time')}\n"
            f"   - **Check-out Time:** {hotel.get('check_out_time')}\n"
            f"   - **Rate per Night:** {hotel.get('rate_per_night')}\n"
            f"   - **Overall Rating:** {hotel.get('overall_rating')}\n"
            f"   - **Amenities:** {hotel.get('amenities')}\n"
            f"   - **Address:** {hotel.get('address')}\n\n"
        )
    return response_text

# ---------------------------
# Geo Coordinates Functions
# ---------------------------
@task(name="get-geo-coordinates", description="Retrieves geocoordinates for a destination, with an optional fallback city.")
def get_geo_coordinates(destination: str, fallback_city: Optional[str] = None) -> Tuple[Optional[float], Optional[float]]:
    """
    Retrieves geocoordinates (latitude and longitude) for a destination. If the destination is not available,
    an optional fallback city is used.

    Args:
        destination (str): The primary destination.
        fallback_city (Optional[str]): An optional fallback city if the primary destination is invalid.

    Returns:
        Tuple[Optional[float], Optional[float]]: A tuple containing the latitude and longitude or (None, None) if not found.
    """
    gmaps = googlemaps.Client(key=os.getenv('GOOGLE_API_KEY'))
    if not destination or destination.lower() == "not available":
        if fallback_city:
            geocode_result = gmaps.geocode(fallback_city)
            if geocode_result:
                location = geocode_result[0]["geometry"]["location"]
                return (location["lat"], location["lng"])
            else:
                return (None, None)
        else:
            return (None, None)
    geocode_result = gmaps.geocode(destination)
    if geocode_result:
        location = geocode_result[0]["geometry"]["location"]
        return (location["lat"], location["lng"])
    else:
        if fallback_city:
            geocode_result = gmaps.geocode(fallback_city)
            if geocode_result:
                location = geocode_result[0]["geometry"]["location"]
                return (location["lat"], location["lng"])
            else:
                return (None, None)
        return (None, None)

# ---------------------------
# Weather Functions
# ---------------------------
@task(name="map-weather-code", description="Maps a weather code to its corresponding textual description.")
def map_weather_code_to_description(code: int) -> str:
    """
    Maps a weather code to its corresponding description.

    Args:
        code (int): The numeric weather code.

    Returns:
        str: A textual description of the weather corresponding to the code.
    """
    mapping = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow fall",
        73: "Moderate snow fall",
        75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    return mapping.get(code, "Unknown")

@task(name="get-weather-forecast-sync", description="Fetches and processes weather forecast or historical data synchronously.")
def get_weather_forecast_sync(lat: float, lon: float, start_date: datetime, end_date: datetime) -> Tuple[str, Dict[str, Any]]:
    """
    Fetches weather forecast or historical data synchronously for the given coordinates and date range.

    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
        start_date (datetime): The start date for the forecast.
        end_date (datetime): The end date for the forecast.

    Returns:
        Tuple[str, Dict[str, Any]]: A tuple where the first element is a formatted forecast string and the second is a detailed weather info dictionary.
    """
    today = datetime.now(timezone.utc).date()
    with httpx.Client() as client_http:
        if end_date.date() < today:
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
        response = client_http.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    
    if "daily" in data and "weathercode" in data['daily']:
        forecast_info = "Weather Forecast:\n"
        weather_info = {}
        for i in range(len(data['daily']['time'])):
            date_str = data['daily']['time'][i]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            day_of_week = date_obj.strftime('%A')
            temp_max = data['daily']['temperature_2m_max'][i]
            temp_min = data['daily']['temperature_2m_min'][i]
            weather_code = data['daily']['weathercode'][i]
            description = map_weather_code_to_description(weather_code)
            forecast_info += f"- **{day_of_week}, {date_obj.strftime('%B %d')}**:\n"
            forecast_info += f"  - Description: {description}\n"
            forecast_info += f"  - Temperature: {temp_min}°C (Min) / {temp_max}°C (Max)\n\n"
            weather_info[date_str] = {
                'description': description,
                'temp_day': temp_max,
                'temp_night': temp_min
            }
        return forecast_info, weather_info
    elif "hourly" in data and "weathercode" in data['hourly']:
        forecast_info = "Historical Weather Data:\n"
        weather_info = {}
        daily_temp_max = {}
        daily_temp_min = {}
        daily_codes = {}
        for i, time_str in enumerate(data['hourly']['time']):
            date_obj = datetime.strptime(time_str, "%Y-%m-%dT%H:%M").date()
            temp = data['hourly']['temperature_2m'][i]
            code = data['hourly']['weathercode'][i]
            if date_obj not in daily_temp_max or temp > daily_temp_max[date_obj]:
                daily_temp_max[date_obj] = temp
            if date_obj not in daily_temp_min or temp < daily_temp_min[date_obj]:
                daily_temp_min[date_obj] = temp
            daily_codes[date_obj] = code
        for date_obj in sorted(daily_temp_max.keys()):
            day = date_obj.strftime('%A')
            temp_max = daily_temp_max[date_obj]
            temp_min = daily_temp_min[date_obj]
            code = daily_codes[date_obj]
            description = map_weather_code_to_description(code)
            forecast_info += f"- **{day}, {date_obj.strftime('%B %d')}**:\n"
            forecast_info += f"  - Description: {description}\n"
            forecast_info += f"  - Temperature: {temp_min}°C (Min) / {temp_max}°C (Max)\n\n"
            weather_info[date_obj.strftime('%Y-%m-%d')] = {
                'description': description,
                'temp_day': temp_max,
                'temp_night': temp_min
            }
        return forecast_info, weather_info
    else:
        return "Weather data is currently unavailable.", {}

@task(name="fetch-weather", description="Fetches weather forecast or historical weather data for a destination and date range.")
def fetch_weather(destination: str, start_date: str = None, end_date: str = None, fallback: Optional[str] = None) -> str:
    """
    Fetches weather forecast or historical weather data for a given destination and date range.

    Args:
        destination (str): The destination city or address.
        start_date (str, optional): Start date in YYYY-MM-DD format. Defaults to today if not provided.
        end_date (str, optional): End date in YYYY-MM-DD format. Defaults to today if not provided.
        fallback (Optional[str]): An optional fallback city name if geocoding fails.

    Returns:
        str: A formatted weather report string.
    """
    today = get_current_date()
    if not start_date:
        start_date = today
    if not end_date:
        end_date = today
    lat, lon = get_geo_coordinates(destination, fallback)
    if lat is None or lon is None:
        return "Weather data is currently unavailable."
    sd = datetime.strptime(start_date, '%Y-%m-%d')
    ed = datetime.strptime(end_date, '%Y-%m-%d')
    forecast_text, _ = get_weather_forecast_sync(lat, lon, sd, ed)
    return forecast_text

# ---------------------------
# Distance & Duration Function
# ---------------------------
@task(name="get-distance-duration", description="Fetches distance and travel duration between two locations using the Google Distance Matrix API.")
def get_distance_duration(origin: str, destination: str, mode: str = "driving") -> Optional[dict]:
    """
    Fetches the distance and travel duration between two locations using the Google Distance Matrix API.

    Args:
        origin (str): The starting location (address, city, or place name).
        destination (str): The destination location.
        mode (str): The mode of travel (default is "driving").

    Returns:
        Optional[dict]: A dictionary with distance and duration details, or None if the API call fails.
    """
    gmaps = googlemaps.Client(key=os.getenv('GOOGLE_API_KEY'))
    result = gmaps.distance_matrix(
        origins=[origin],
        destinations=[destination],
        mode=mode,
        units="metric"
    )
    if result['status'] != 'OK':
        return None

    element = result['rows'][0]['elements'][0]
    if element['status'] != 'OK':
        return None

    distance = element['distance']
    duration = element['duration']
    return {
        'distance_text': distance['text'],
        'distance_value': distance['value'],
        'duration_text': duration['text'],
        'duration_value': duration['value']
    }

# ---------------------------
# Nearby Places Functions
# ---------------------------
@task(name="find-nearby-places", description="Finds nearby places of a specific type within a given radius.")
def find_nearby_places(latitude: float, longitude: float, radius: int = 100000, place_type: str = "tourist_attraction") -> List[dict]:
    """
    Finds nearby places of a specific type within a given radius.

    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.
        radius (int): Search radius in meters (default is 100000).
        place_type (str): Type of place (e.g., "tourist_attraction", "restaurant").

    Returns:
        List[dict]: A list of dictionaries, each representing a nearby place.
    """
    gmaps = googlemaps.Client(key=os.getenv('GOOGLE_API_KEY'))
    response = gmaps.places_nearby(
        location=(latitude, longitude),
        radius=radius,
        type=place_type
    )
    places = response.get('results', [])
    return places

@task(name="format-nearby-places", description="Formats the list of nearby places into a human-readable string.")
def format_nearby_places(places: List[dict]) -> str:
    """
    Formats a list of nearby places into a human-readable string.

    Args:
        places (List[dict]): A list of nearby place dictionaries.

    Returns:
        str: A formatted string listing the nearby places.
    """
    if not places:
        return "No nearby places found."
    response_text = "Nearby Places:\n"
    for idx, place in enumerate(places[:30], 1):
        name = place.get("name", "Unknown")
        rating = place.get("rating", "No rating")
        address = place.get("vicinity", "No address")
        response_text += f"{idx}. {name} - Rating: {rating}, Address: {address}\n"
    return response_text

# ---------------------------
# Reddit Functions (Synchronous Versions)
# ---------------------------
@task(name="get-reddit-comments", description="Fetches top comments from a Reddit post using its permalink.")
def get_reddit_comments(permalink: str, limit=5):
    """
    Fetches the top comments (up to the specified limit) from a Reddit post using its permalink.

    Args:
        permalink (str): The permalink of the Reddit post.
        limit (int): Maximum number of comments to retrieve.

    Returns:
        List[str]: A list of comment texts.
    """
    headers = {'User-Agent': 'travel-planner-app/0.1'}
    url = f"https://www.reddit.com{permalink}.json"
    params = {'limit': limit, 'depth': 1}
    try:
        with httpx.Client() as client:
            response = client.get(url, headers=headers, params=params)
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
        return []

@task(name="get-reddit-posts", description="Fetches recent Reddit posts related to a destination from a specified subreddit.")
def get_reddit_posts(destination: str, subreddit='travel', limit=5):
    """
    Fetches recent Reddit posts related to the given destination from a specified subreddit.

    Args:
        destination (str): The destination or query term for Reddit posts.
        subreddit (str): The subreddit to search (default is 'travel').
        limit (int): The number of posts to retrieve (default is 5).

    Returns:
        Tuple[List[dict], dict]: A tuple containing a list of post details and the raw JSON response.
    """
    headers = {'User-Agent': 'travel-planner-app/0.1'}
    url = f"https://www.reddit.com/r/{subreddit}/search.json"
    params = {
        'q': destination,
        'sort': 'new',
        'limit': limit,
        'restrict_sr': True
    }
    with httpx.Client() as client:
        response = client.get(url, headers=headers, params=params)
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
            post_info['external_content'] = f"Content from {post_data.get('url')}"
        comments = get_reddit_comments(post_info['permalink'], limit=3)
        post_info['comments'] = comments
        post_list.append(post_info)
    return post_list, data
