# main.py
import nest_asyncio
nest_asyncio.apply()
import os
import sys
import json
import re
import asyncio
from loguru import logger
from typing import Optional, List
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import googlemaps
from agentifyme import workflow
from bs4 import BeautifulSoup
from pydantic import ValidationError
from models import TravelQuery
from openai import OpenAI
from utils import generate_json_schema
from travel_document import TripItinerary  # Importing TripItinerary model

from tasks import (
    get_flight_deals,
    get_hotel_deals,
    get_geo_coordinates,
    get_nights,
    find_nearby_places,
    get_distance_duration,
    get_reddit_posts,
    get_wikipedia_info,
    get_flight_distance,
    fetch_inbound_flights,
    extract_flight_details
)

# Load environment variables from .env file
load_dotenv()

# Configure loguru
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time} - {level} - {message}")
logger.add("travel_planner.log", level="INFO", format="{time} - {level} - {message}")

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

async def generate_itinerary(
    origin: str,
    destination: str,
    start_date: datetime,
    end_date: datetime,
    remaining_budget: float,
    selected_hotel: dict,
    selected_flight: dict,
    inbound_flight: Optional[dict] = None,
    weather_info: Optional[dict] = None
) -> TripItinerary:
    """
    Generate a detailed daily travel itinerary for the specified trip, including flight details,
    and parse the response into a TripItinerary Pydantic model.
    """
    hotel_lat = selected_hotel.get('latitude')
    hotel_lng = selected_hotel.get('longitude')
    hotel_location = (hotel_lat, hotel_lng)

    if hotel_lat is None or hotel_lng is None:
        logger.warning("Hotel coordinates not found (None). Skipping find_nearby_places.")
        nearby_places = []
    else:
        nearby_places = find_nearby_places(hotel_location)

    attractions_info = []
    for place in nearby_places[:10]:
        place_name = place['name']
        place_loc = place['geometry']['location']
        distance_duration = get_distance_duration(
            origin=f"{hotel_lat},{hotel_lng}",
            destination=f"{place_loc['lat']},{place_loc['lng']}",
            mode="walking"
        )
        if distance_duration:
            attractions_info.append({
                'name': place_name,
                'distance': distance_duration['distance_text'],
                'duration': distance_duration['duration_text']
            })

    # Generate JSON schema for TripItinerary
    schema = generate_json_schema(TripItinerary)

    prompt = (
        f"Create a detailed daily travel itinerary for a trip from {origin} to {destination} "
        f"from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}. "
        f"You will be staying at {selected_hotel.get('name')} which costs "
        f"${selected_hotel.get('rate_per_night')} per night. "
        f"The remaining budget for daily expenses is ${remaining_budget:.2f}. "
        "Ensure the final output matches the JSON schema provided.\n\n"
        "JSON Schema:\n"
        f"{schema}\n\n"
        "Itinerary Details:\n"
    )

    for a in attractions_info:
        prompt += f"- {a['name']} ({a['distance']} away, ~{a['duration']} walk)\n"

    if weather_info:
        prompt += "\nWeather information:\n"
        for date_str, info in weather_info.items():
            prompt += (
                f"- {date_str}: {info['description']}, "
                f"Day Temp: {info['temp_day']}°C, Night Temp: {info['temp_night']}°C\n"
            )

    prompt += "\nFlight Details:\n"
    prompt += (
        f"Outbound: Flight {selected_flight.get('flight_number', 'N/A')} by {selected_flight.get('airplane', 'N/A')} at "
        f"${selected_flight.get('price', 'N/A')}, Duration: {selected_flight.get('duration(mins)', 'N/A')} minutes.\n"
    )
    if inbound_flight:
        prompt += (
            f"Inbound: Flight {inbound_flight.get('flight_number', 'N/A')} by {inbound_flight.get('airplane', 'N/A')} at "
            f"${inbound_flight.get('price', 'N/A')}, Duration: {inbound_flight.get('duration(mins)', 'N/A')} minutes.\n"
        )

    # Append Reddit posts section
    reddit_posts, _ = get_reddit_posts(destination, subreddit='travel', limit=5)
    if reddit_posts:
        prompt += "\nRecent Reddit Discussions:\n"
        for idx, post in enumerate(reddit_posts, 1):
            content = post.get('content') or post.get('external_content') or "[No content]"
            if len(content) > 200:
                content = content[:197] + "..."
            comments = post.get('comments', [])
            prompt += f"{idx}. {content}\n"
            if comments:
                for cidx, cmt in enumerate(comments, 1):
                    if cidx > 3:
                        break
                    prompt += f"   Comment: {cmt}\n"
            else:
                prompt += "   [No comments available]\n"
    else:
        prompt += "\nNo recent Reddit discussions found.\n"

    # Append Wikipedia info section
    wiki_info, _ = get_wikipedia_info(destination)
    if wiki_info:
        prompt += "\nWikipedia Info:\n"
        for section, html_content in wiki_info.items():
            soup = BeautifulSoup(html_content, 'html.parser')
            text_content = soup.get_text()
            if len(text_content) > 400:
                text_content = text_content[:397] + "..."
            prompt += f"--- {section} ---\n{text_content}\n\n"
    else:
        prompt += "\nNo Wikipedia information found.\n"

    prompt += (
    "Plan out each day with these attractions, ensure it fits in the budget, and summarize daily costs.\n"
    "For each day, include at least 4 distinct nearby attractions or activities.\n"
    "Suggestions on what to pack according to the weather, and safety measures based on the Reddit discussions and comments.\n"
    "Do not output any arithmetic expressions; compute all arithmetic and return numeric values only.\n"
    "Please output the itinerary in JSON format that adheres exactly to the provided JSON schema."
    )


    logger.info("Generating itinerary with OpenAI using JSON schema guidance.")
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful travel planner that outputs itineraries in valid JSON format matching the provided schema."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="gpt-4o-mini"
        )

        if response and response.choices and len(response.choices) > 0:
            itinerary_text = response.choices[0].message.content.strip()
            logger.info("Itinerary generated successfully.")
        else:
            logger.error("No response from OpenAI.")
            raise ValueError("Could not generate itinerary at this time.")

        # Attempt to extract JSON from code fences if present
        json_match = re.search(r'```json\s*(.*?)\s*```', itinerary_text, re.DOTALL)
        if json_match:
            itinerary_text = json_match.group(1).strip()

        # Debug logging in case of parsing issues
        try:
            itinerary_json = json.loads(itinerary_text)
        except json.JSONDecodeError as jde:
            logger.error(f"JSON decoding failed. Response text: {itinerary_text}")
            raise

        trip_itinerary = TripItinerary.parse_obj(itinerary_json)
        return trip_itinerary

    except Exception as e:
        logger.error(f"Error generating or parsing itinerary with OpenAI: {e}")
        raise

def display_weather(forecast_info: str):
    if not forecast_info:
        print("No weather data available.")
        return
    print(f"\n=== Weather Information ===\n{forecast_info}\n==========================\n")

async def get_travel_details(query: str) -> TravelQuery:
    prompt = (
        f"Assume today's date is {datetime.now(timezone.utc).strftime('%Y-%m-%d')}.\n\n"
        "Extract travel details from the sentence below and return JSON with these fields:\n"
        "origin (string), origin_iata (string), destination (string or list of strings), "
        "destination_iata (string or list of strings), start_date (YYYY-MM-DD), end_date (YYYY-MM-DD), "
        "budget (number, optional), accommodation_preferences (object, optional: entire_room (bool), pet_friendly (bool)).\n\n"
        f"Input: \"{query}\"\n\nOutput:"
    )

    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant extracting travel details and constraints from user queries."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="gpt-4o-mini"
        )

        assistant_reply = response.choices[0].message.content.strip()
        logger.info(f"OpenAI response: {assistant_reply}")

        json_match = re.search(r'\{.*\}', assistant_reply, re.DOTALL)
        if json_match:
            try:
                travel_data = json.loads(json_match.group())
            except json.JSONDecodeError as e:
                logger.error(f"JSON decoding error: {e}")
                raise ValueError("Invalid JSON format in the assistant's response.")
        else:
            raise ValueError("No JSON data found in the assistant's response.")

        origin = travel_data.get('origin')
        origin_iata = travel_data.get('origin_iata')

        destination = travel_data.get('destination', [])
        destination_iata = travel_data.get('destination_iata', [])

        if not isinstance(destination, list):
            destination = [destination]
        if not isinstance(destination_iata, list):
            destination_iata = [destination_iata]

        if len(destination) != len(destination_iata):
            logger.error("Mismatch between number of destinations and their IATA codes.")
            raise ValueError("Mismatch between number of destinations and their IATA codes.")

        try:
            travel_details = TravelQuery(
                origin=origin,
                origin_iata=origin_iata,
                destination=destination,
                destination_iata=destination_iata,
                start_date=travel_data.get('start_date'),
                end_date=travel_data.get('end_date'),
                budget=travel_data.get('budget'),
                accommodation_preferences=travel_data.get('accommodation_preferences')
            )
        except ValidationError as e:
            logger.error(f"Pydantic validation error: {e}")
            raise ValueError("Invalid travel details provided.")

        return travel_details

    except Exception as e:
        logger.error(f"Error parsing travel details: {e}")
        raise ValueError("Failed to parse travel details.")

@workflow(name="generate_travel_plan", description="Generate a travel plan for a given location, budget, and dates")
async def generate_travel_plan(query: str) -> str:
    try:
        travel_details = await get_travel_details(query)
    except ValueError as ve:
        logger.error(f"Error parsing travel details: {ve}")
        return "Error parsing travel details. Please ensure your input is clear."

    origin = travel_details.origin
    origin_iata = travel_details.origin_iata
    destinations = travel_details.destination
    destinations_iata = travel_details.destination_iata
    start_date = travel_details.start_date
    end_date = travel_details.end_date
    budget = travel_details.budget
    accommodation_prefs = travel_details.accommodation_preferences

    trip_sequence = [origin] + destinations
    trip_iata_sequence = [origin_iata] + destinations_iata
    total_flight_cost = 0.0
    total_hotel_cost = 0.0
    remaining_budget = budget if budget else 0.0

    total_nights = get_nights(start_date, end_date)
    num_legs = len(trip_sequence) - 1
    if num_legs == 0:
        return "No valid destinations detected after origin."

    nights_per_leg = total_nights // num_legs
    extra_nights = total_nights % num_legs

    itinerary_segments: List[dict] = []

    for i in range(num_legs):
        current_origin = trip_sequence[i]
        current_origin_iata = trip_iata_sequence[i]
        current_destination = trip_sequence[i + 1]
        current_destination_iata = trip_iata_sequence[i + 1]

        leg_start_date = start_date + timedelta(days=i * nights_per_leg + min(i, extra_nights))
        leg_end_date = leg_start_date + timedelta(days=nights_per_leg)
        if i < extra_nights:
            leg_end_date += timedelta(days=1)
        if i == num_legs - 1:
            leg_end_date = end_date

        # Flights retrieval and selection (unchanged)...
        flights = get_flight_deals(current_origin_iata, current_destination_iata, leg_start_date, leg_end_date)
        if not flights:
            return f"No flight deals found for {current_origin} to {current_destination}."
        selected_flight = flights[0]
        print(f"Selected Outbound Flight: {selected_flight['flight_number']} by {selected_flight['airplane']} at ${selected_flight['price']}, Duration: {selected_flight.get('duration(mins)', 'N/A')} minutes")

        inbound_cost = 0
        inbound_flight = None
        departure_token = selected_flight.get('departure_token')
        if departure_token:
            inbound_results = fetch_inbound_flights(
                departure_id=current_origin_iata,
                arrival_id=current_destination_iata,
                outbound_date=leg_start_date.strftime('%Y-%m-%d'),
                return_date=leg_end_date.strftime('%Y-%m-%d'),
                departure_token=departure_token
            )
            inbound_flights = extract_flight_details(inbound_results)
            if inbound_flights:
                selected_inbound = inbound_flights[0]
                print(f"Selected Inbound Flight: {selected_inbound['flight_number']} by {selected_inbound['airplane']} at ${selected_inbound['price']}, Duration: {selected_inbound['duration(mins)']} minutes")
                inbound_cost = selected_inbound['price'] if isinstance(selected_inbound['price'], (int, float)) else 0
                inbound_flight = selected_inbound

        outbound_cost = selected_flight['price'] if isinstance(selected_flight['price'], (int, float)) else 0
        total_flight_cost += outbound_cost + inbound_cost
        remaining_budget -= (outbound_cost + inbound_cost)

        flight_distance = get_flight_distance(current_origin, current_destination)
        distance_text = f"{flight_distance:.2f} km" if flight_distance else "N/A"
        flight_duration = selected_flight.get('duration(mins)', "N/A")

        hotels = get_hotel_deals(
            current_destination,
            leg_start_date,
            leg_end_date,
            remaining_budget,
            accommodation_prefs
        )
        if not hotels:
            print("No matching hotel deals. Trying to relax preferences...")
            hotels = get_hotel_deals(current_destination, leg_start_date, leg_end_date, remaining_budget, None)
            if not hotels:
                print("No hotel deals found even after relaxing preferences. Exiting.")
                sys.exit(1)
            else:
                print("Selected with relaxed preferences.")

        selected_hotel = hotels[0]
        print(f"Selected Hotel: {selected_hotel['name']} at ${selected_hotel['rate_per_night']} per night, Rating: {selected_hotel['overall_rating']}")

        # Parse GPS coordinates if available
        gps_coords = selected_hotel.get("gps_coordinates")
        hotel_lat = None
        hotel_lng = None
        if gps_coords and gps_coords != "Not Available":
            if isinstance(gps_coords, dict):
                hotel_lat = gps_coords.get('latitude')
                hotel_lng = gps_coords.get('longitude')
            elif isinstance(gps_coords, str):
                try:
                    lat_str, lon_str = gps_coords.split(',')
                    hotel_lat = float(lat_str.strip())
                    hotel_lng = float(lon_str.strip())
                except Exception as e:
                    logger.warning(f"Failed parsing GPS coordinates: {gps_coords}. Error: {e}")
                    hotel_lat, hotel_lng = get_geo_coordinates(selected_hotel.get('address', current_destination))
            else:
                logger.warning(f"Unexpected gps_coordinates format: {gps_coords}")
        else:
            logger.warning("GPS coordinates not available. Using alternative geocoding.")
            hotel_lat, hotel_lng = get_geo_coordinates(selected_hotel.get('address', current_destination))

        selected_hotel['latitude'] = hotel_lat
        selected_hotel['longitude'] = hotel_lng

        # Use these coordinates for nearby places search if valid
        if hotel_lat is not None and hotel_lng is not None:
            nearby_places = find_nearby_places((hotel_lat, hotel_lng))
        else:
            logger.warning("Valid hotel coordinates not available for nearby place search.")
            nearby_places = []

        try:
            price_per_night = float(selected_hotel['rate_per_night'].replace('$', '').replace(',', ''))
        except (ValueError, AttributeError):
            price_per_night = 0.0

        nights_this_leg = get_nights(leg_start_date, leg_end_date)
        hotel_cost = price_per_night * nights_this_leg
        total_hotel_cost += hotel_cost
        remaining_budget -= hotel_cost

        itinerary_segments.append({
            'origin': current_origin,
            'origin_iata': current_origin_iata,
            'destination': current_destination,
            'destination_iata': current_destination_iata,
            'flight': selected_flight,
            'inbound_flight': inbound_flight,
            'hotel': selected_hotel,
            'start_date': leg_start_date,
            'end_date': leg_end_date,
            'hotel_cost': hotel_cost,
            'flight_cost': outbound_cost + inbound_cost,
            'distance': distance_text,
            'duration': flight_duration
        })

    if budget is not None and remaining_budget < 0:
        print(f"\nTotal flight cost (${total_flight_cost}) + hotel cost (${total_hotel_cost}) exceed your budget (${budget}).")
        sys.exit(1)
    else:
        print(f"\nTotal Flight Cost: ${total_flight_cost:.2f}")
        print(f"Total Hotel Cost: ${total_hotel_cost:.2f}")
        print(f"Remaining Budget: ${remaining_budget:.2f}")

    full_itinerary = []
    for segment in itinerary_segments:
        itinerary_obj = await generate_itinerary(
            origin=segment['origin'],
            destination=segment['destination'],
            start_date=segment['start_date'],
            end_date=segment['end_date'],
            remaining_budget=remaining_budget,
            selected_hotel=segment['hotel'],
            selected_flight=segment['flight'],
            inbound_flight=segment.get('inbound_flight')
        )
        full_itinerary.append(itinerary_obj)

    itineraries_json = json.dumps(
        [json.loads(it.json()) for it in full_itinerary],
        indent=2
    )
    return itineraries_json


async def main_async():
    query = "i want to travel from Phoenix to boston on 25th january and return on 28th january under 3000$.."
    itinerary = await generate_travel_plan(query)
    print(itinerary)

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()