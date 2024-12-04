# main.py

import os
from typing import Optional, List
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
import openai
import requests
import logging
from weather1 import (
    get_weather_forecast,
    filter_forecast_by_date,
    display_weather,
    validate_date
)
from models import TravelQuery, AccommodationPreferences  # Ensure models.py is correctly defined
from pydantic import ValidationError
import json
import re

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Validate that the OpenAI API key is available
if not OPENAI_API_KEY:
    logging.error("OPENAI_API_KEY not found. Please set it in your .env file.")
    sys.exit(1)

# Initialize OpenAI API
openai.api_key = OPENAI_API_KEY

# Mock API URLs (Replace with your actual Postman mock server URLs)
MOCK_SERVER_BASE_URL = 'https://12036995-4de7-4870-ae4e-f8b22ccb2c09.mock.pstmn.io'  # Replace with your Mock Server Base URL
HOTEL_API_URL = f'{MOCK_SERVER_BASE_URL}/hotels'
FLIGHT_API_URL = f'{MOCK_SERVER_BASE_URL}/flights'

# Predefined list of popular cities within regions
POPULAR_CITIES = {
    "california": ["Los Angeles", "San Francisco", "San Diego", "Sacramento", "San Jose", "Fresno", "Long Beach", "Oakland", "Bakersfield", "Anaheim"]
    # Add more regions and their popular cities as needed
}

def get_nights(start_date: datetime, end_date: datetime) -> int:
    """
    Calculates the number of nights between start_date and end_date.
    """
    delta = end_date - start_date
    return delta.days

def get_travel_details(query: str) -> TravelQuery:
    """
    Uses OpenAI to parse the natural language query and extract travel details along with constraints.
    """
    try:
        # Construct the prompt with explicit current date context
        prompt = (
            "Assume today's date is 2024-11-21. Extract the travel details and constraints from the following sentence and provide the output in JSON format with the following fields: "
            "origin (string), destinations (list of strings), start_date (YYYY-MM-DD), end_date (YYYY-MM-DD), "
            "budget (number, optional), accommodation_preferences (object, optional with fields: entire_room (boolean), pet_friendly (boolean)). "
            "If the user specifies a region or state instead of specific cities, automatically include a predefined list of popular cities within that region. "
            "Ensure that the extracted dates are in the future relative to the current date.\n\n"
            f"Input: \"{query}\"\n\nOutput:"
        )

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an assistant that extracts travel details and constraints from user queries."},
                {"role": "user", "content": prompt}
            ],
        )

        # Extract the assistant's reply
        assistant_reply = response.choices[0].message['content'].strip()
        logging.info(f"OpenAI response: {assistant_reply}")

        # Attempt to parse JSON from the assistant's reply
        json_match = re.search(r'\{.*\}', assistant_reply, re.DOTALL)
        if json_match:
            travel_data = json.loads(json_match.group())
            logging.info(f"Extracted travel data: {travel_data}")
        else:
            # If no JSON is found, raise an error
            raise ValueError("No JSON data found in the assistant's response.")

        # If destinations include a region, expand it into specific cities
        if 'destinations' in travel_data:
            expanded_destinations = []
            for dest in travel_data['destinations']:
                dest_lower = dest.lower()
                if dest_lower in POPULAR_CITIES:
                    expanded_destinations.extend(POPULAR_CITIES[dest_lower])
                else:
                    expanded_destinations.append(dest)
            travel_data['destinations'] = expanded_destinations

        # Validate and parse the data using Pydantic
        travel_details = TravelQuery(**travel_data)
        return travel_details

    except (openai.OpenAIError, json.JSONDecodeError, ValueError) as e:
        logging.error(f"Error parsing travel details: {e}")
        sys.exit(1)
    except ValidationError as ve:
        logging.error(f"Validation error: {ve}")
        sys.exit(1)

def get_hotel_deals(destination: str, start_date: datetime, end_date: datetime, budget: Optional[float] = None, accommodation_prefs: Optional[AccommodationPreferences] = None):
    """
    Fetches hotel deals from the mock API with optional budget and accommodation preferences.
    """
    params = {
        'destination': destination,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d')
    }

    if budget:
        params['budget'] = budget
    if accommodation_prefs:
        if accommodation_prefs.entire_room is not None:
            params['entire_room'] = accommodation_prefs.entire_room
        if accommodation_prefs.pet_friendly is not None:
            params['pet_friendly'] = accommodation_prefs.pet_friendly

    try:
        response = requests.get(HOTEL_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Handle case-insensitive matching
        destination_key = None
        for city in data.keys():
            if city.lower() == destination.lower():
                destination_key = city
                break

        if not destination_key:
            logging.info(f"No hotels found for destination '{destination}'. Please check the city name.")
            return []

        hotels = data.get(destination_key, {}).get('hotels', [])
        if not hotels:
            logging.info(f"No hotels available in {destination}.")
            return []

        # Apply budget filter if provided
        if budget:
            nights = get_nights(start_date, end_date)
            hotels = [hotel for hotel in hotels if hotel['price'] * nights <= budget]

        # Apply accommodation preferences
        if accommodation_prefs:
            if accommodation_prefs.entire_room is not None:
                hotels = [hotel for hotel in hotels if hotel.get('entire_room') == accommodation_prefs.entire_room]
            if accommodation_prefs.pet_friendly is not None:
                hotels = [hotel for hotel in hotels if hotel.get('pet_friendly') == accommodation_prefs.pet_friendly]

        if not hotels:
            logging.info("No hotels match the specified budget and accommodation preferences.")
            return []

        # Sort hotels by price (ascending)
        hotels_sorted = sorted(hotels, key=lambda x: x['price'])
        logging.info(f"Found {len(hotels_sorted)} hotel deals.")
        return hotels_sorted
    except requests.RequestException as e:
        logging.error(f"Error fetching hotel deals: {e}")
        return []

def get_flight_deals(origin: str, destination: str, start_date: datetime, end_date: datetime):
    """
    Fetches flight deals from the mock API.
    """
    params = {
        'origin': origin,
        'destination': destination,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d')
    }
    try:
        response = requests.get(FLIGHT_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Handle case-insensitive matching
        destination_key = None
        for city in data.keys():
            if city.lower() == destination.lower():
                destination_key = city
                break

        if not destination_key:
            logging.info(f"No flights found for destination '{destination}'. Please check the city name.")
            return []

        flights = data.get(destination_key, {}).get('flights', [])
        if not flights:
            logging.info(f"No flights available to {destination}.")
            return []

        # Sort flights by price (ascending)
        flights_sorted = sorted(flights, key=lambda x: x['price'])
        logging.info(f"Found {len(flights_sorted)} flight deals.")
        return flights_sorted
    except requests.RequestException as e:
        logging.error(f"Error fetching flight deals: {e}")
        return []

def generate_itinerary(origin: str, destination: str, start_date: datetime, end_date: datetime, remaining_budget: float, selected_hotel: dict, weather_info: Optional[dict] = None):
    """
    Generates a travel itinerary using OpenAI's GPT model, ensuring it stays within the remaining budget.
    """
    try:
        if weather_info:
            # Construct the prompt with weather information and selected hotel details
            prompt = (
                f"Create a detailed travel itinerary for a trip from {origin} to {destination} "
                f"from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}. "
                f"You will be staying at {selected_hotel['name']} which costs ${selected_hotel['price']} per night. "
                f"The remaining budget for daily expenses, activities, dining, and transportation is ${remaining_budget:.2f}. "
                f"The weather forecast is as follows:\n"
            )
            for date, info in weather_info.items():
                prompt += f"- {date}: {info['description']}, Day Temp: {info['temp_day']}°C, Night Temp: {info['temp_night']}°C\n"

            prompt += (
                "Include daily activities, places to visit, and dining suggestions suitable for the weather conditions, "
                "while ensuring that the total cost of these activities does not exceed the remaining budget. "
                "Provide a summary of daily estimated costs for each activity and meal."
            )
        else:
            # Construct a general prompt without weather information but with selected hotel and remaining budget
            prompt = (
                f"Create a detailed travel itinerary for a trip from {origin} to {destination} "
                f"from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}. "
                f"You will be staying at {selected_hotel['name']} which costs ${selected_hotel['price']} per night. "
                f"The remaining budget for daily expenses, activities, dining, and transportation is ${remaining_budget:.2f}. "
                "Include daily activities, places to visit, and dining suggestions, ensuring that the total cost does not exceed the remaining budget. "
                "Provide a summary of daily estimated costs for each activity and meal."
            )

        logging.info("Generating itinerary with OpenAI.")
        # Generate itinerary using OpenAI's GPT
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful travel planner who ensures itineraries stay within budget."},
                {"role": "user", "content": prompt}
            ],
        )

        itinerary = response.choices[0].message['content'].strip()
        logging.info("Itinerary generated successfully.")
        return itinerary
    except Exception as e:
        logging.error(f"Error generating itinerary: {e}")
        return "Could not generate itinerary at this time."

def process_weather_data(forecast_entries: List[dict]) -> dict:
    """
    Processes weather forecast entries to extract daily weather information.

    Parameters:
        forecast_entries (list): List of forecast entries.

    Returns:
        dict: Dictionary containing weather information per date.
    """
    weather_info = {}
    for entry in forecast_entries:
        date = entry['dt_txt'].split(' ')[0]
        time = entry['dt_txt'].split(' ')[1]
        if date not in weather_info:
            weather_info[date] = {
                'description': entry['weather'][0]['description'],
                'temp_day': [],
                'temp_night': []
            }
        # Assuming day time is 06:00 to 18:00
        if "06:00:00" <= time <= "18:00:00":
            weather_info[date]['temp_day'].append(entry['main']['temp'])
        else:
            weather_info[date]['temp_night'].append(entry['main']['temp'])

    # Average the temperatures
    for date, info in weather_info.items():
        if info['temp_day']:
            info['temp_day'] = round(sum(info['temp_day']) / len(info['temp_day']), 1)
        else:
            info['temp_day'] = 'N/A'
        if info['temp_night']:
            info['temp_night'] = round(sum(info['temp_night']) / len(info['temp_night']), 1)
        else:
            info['temp_night'] = 'N/A'

    logging.info("Processed weather data for itinerary.")
    return weather_info

def main():
    print("Welcome to the Multi-City Travel Planner!")

    # User Input as a semantic query
    query = input("Enter your travel plans (e.g., 'I want to travel from New York to Los Angeles, starting on 2024-12-23 and ending on 2024-12-28, with a budget of $4500, preferring entire rooms and pet-friendly accommodations'): ").strip()

    # Parse the query to extract travel details and constraints
    travel_details = get_travel_details(query)

    origin = travel_details.origin
    destinations = travel_details.destinations  # List of destinations
    start_date = travel_details.start_date      # Start date of the trip (datetime)
    end_date = travel_details.end_date          # End date of the trip (datetime)
    budget = travel_details.budget
    accommodation_prefs = travel_details.accommodation_preferences

    # Validate that end_date is within the forecast range (next 5 days)
    today = datetime.today()
    max_forecast_date = today + timedelta(days=5)

    if end_date > max_forecast_date:
        print("Warning: Weather forecast is only available for the next 5 days. Proceeding without complete weather information.")
        weather_available = False
    else:
        weather_available = True

    # Construct the full trip sequence
    trip_sequence = [origin] + destinations

    # Initialize total fixed costs
    total_flight_cost = 0
    total_hotel_cost = 0

    # Initialize remaining budget
    remaining_budget = budget if budget else 0

    # Initialize a list to store itinerary segments
    itinerary_segments = []

    # Calculate total trip duration in nights
    total_nights = get_nights(start_date, end_date)

    # Calculate nights per leg
    num_legs = len(trip_sequence) - 1
    nights_per_leg = total_nights // num_legs
    extra_nights = total_nights % num_legs

    # Iterate through each leg of the trip
    for i in range(num_legs):
        current_origin = trip_sequence[i]
        current_destination = trip_sequence[i + 1]

        print(f"\nFetching deals for: {current_origin} to {current_destination}")

        # Calculate start and end dates for the current leg
        leg_start_date = start_date + timedelta(days=i * nights_per_leg + min(i, extra_nights))
        leg_end_date = leg_start_date + timedelta(days=nights_per_leg)
        if i < extra_nights:
            leg_end_date += timedelta(days=1)

        # Ensure the last leg ends on the trip's end date
        if i == num_legs - 1:
            leg_end_date = end_date

        # Fetch hotel deals at the current destination for the duration of stay
        hotels = get_hotel_deals(
            destination=current_destination,
            start_date=leg_start_date,
            end_date=leg_end_date,
            budget=remaining_budget,
            accommodation_prefs=accommodation_prefs
        )

        if hotels:
            # Automatically select the cheapest hotel
            selected_hotel = hotels[0]
            print(f"Selected Hotel: {selected_hotel['name']} at ${selected_hotel['price']} per night, Rating: {selected_hotel['rating']}")
        else:
            print("\nNo hotel deals found matching your preferences and budget.")
            # Automatically relax accommodation preferences and fetch hotels again
            logging.info("Attempting to fetch hotels without accommodation preferences...")
            hotels = get_hotel_deals(
                destination=current_destination,
                start_date=leg_start_date,
                end_date=leg_end_date,
                budget=remaining_budget,
                accommodation_prefs=None
            )
            if hotels:
                # Automatically select the cheapest hotel from the relaxed list
                selected_hotel = hotels[0]
                print(f"Selected Hotel (Relaxed Preferences): {selected_hotel['name']} at ${selected_hotel['price']} per night, Rating: {selected_hotel['rating']}")
            else:
                print("\nNo hotel deals found even after relaxing preferences.")
                sys.exit(1)

        # Calculate hotel cost for this leg
        nights = get_nights(leg_start_date, leg_end_date)
        hotel_cost = selected_hotel['price'] * nights
        total_hotel_cost += hotel_cost
        remaining_budget -= hotel_cost

        # Fetch flight deals for this leg
        flights = get_flight_deals(
            origin=current_origin,
            destination=current_destination,
            start_date=leg_start_date,
            end_date=leg_end_date
        )

        if flights:
            # Automatically select the cheapest flight
            selected_flight = flights[0]
            print(f"Selected Flight: {selected_flight['airline']} at ${selected_flight['price']}, Duration: {selected_flight['duration']}")
        else:
            print("\nNo flight deals found.")
            print("Cannot proceed without flight deals. Exiting.")
            sys.exit(1)

        # Calculate flight cost for this leg
        flight_cost = selected_flight['price']
        total_flight_cost += flight_cost
        remaining_budget -= flight_cost

        # Append segment details to itinerary_segments
        itinerary_segments.append({
            'origin': current_origin,
            'destination': current_destination,
            'flight': selected_flight,
            'hotel': selected_hotel,
            'start_date': leg_start_date,
            'end_date': leg_end_date,
            'hotel_cost': hotel_cost,
            'flight_cost': flight_cost
        })

    # Check if total costs exceed budget
    if budget is not None and remaining_budget < 0:
        print(f"\nThe total cost of flights (${total_flight_cost}) and hotels (${total_hotel_cost}) exceeds your budget of ${budget}.")
        print("Please adjust your budget or travel dates.")
        sys.exit(1)
    else:
        print(f"\nTotal Flight Cost: ${total_flight_cost:.2f}")
        print(f"Total Hotel Cost: ${total_hotel_cost:.2f}")
        print(f"Remaining Budget for Daily Expenses and Activities: ${remaining_budget:.2f}")

    # Fetch weather forecast for each destination
    weather_info = {}
    if weather_available:
        for segment in itinerary_segments:
            dest = segment['destination']
            leg_start = segment['start_date']
            leg_end = segment['end_date']
            forecast_data = get_weather_forecast(dest, leg_start, leg_end)
            if forecast_data:
                try:
                    segment_weather = filter_forecast_by_date(
                        forecast_data,
                        segment['start_date'],
                        segment['end_date'] + timedelta(days=1)
                    )
                    print(f"\nWeather Forecast for {dest}:")
                    display_weather(segment_weather)
                    processed_weather = process_weather_data(segment_weather)
                    weather_info[dest] = processed_weather
                except ValueError as ve:
                    logging.error(f"Error parsing dates for weather forecast filtering: {ve}")
                    weather_info[dest] = None
            else:
                logging.warning(f"No weather data retrieved for {dest}.")
                weather_info[dest] = None
    else:
        logging.warning("Weather forecast is not available for the entire trip duration.")
        # Optionally, handle partial weather data if some dates are within the forecast range
        # For simplicity, we'll skip weather data in this example

    # Generate itinerary for each segment
    full_itinerary = ""
    for segment in itinerary_segments:
        origin = segment['origin']
        destination = segment['destination']
        start_date = segment['start_date']
        end_date = segment['end_date']
        remaining_budget_segment = remaining_budget  # Pass the remaining budget at this point
        selected_hotel = segment['hotel']
        dest_weather_info = weather_info.get(destination, None)

        itinerary = generate_itinerary(
            origin,
            destination,
            start_date,
            end_date,
            remaining_budget_segment,
            selected_hotel,
            dest_weather_info
        )

        full_itinerary += f"\n\n---\n\n**Leg: {origin} to {destination}**\n\n{itinerary}"

    print("\nYour Comprehensive Multi-City Itinerary:")
    print(full_itinerary)


if __name__ == "__main__":
    main()
