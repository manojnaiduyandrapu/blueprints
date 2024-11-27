# weather.py

import requests
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import sys
import logging

# Load environment variables from a .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Retrieve the API key from environment variables
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')

# Validate that the API key is available
if not OPENWEATHER_API_KEY:
    logging.error("Error: OPENWEATHER_API_KEY not found. Please set it in your .env file.")
    sys.exit(1)

def validate_date(date_text):
    """
    Validates that the provided date string is in YYYY-MM-DD format.
    """
    try:
        return datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        logging.error("Incorrect date format. Please use YYYY-MM-DD.")
        sys.exit(1)

def get_weather_forecast(city, start_date, end_date):
    """
    Fetches the weather forecast for the given city and date range.
    Falls back to an empty dict if forecast data is unavailable.

    Parameters:
        city (str): Destination city.
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.

    Returns:
        dict: Parsed JSON response from OpenWeatherMap API or empty dict if unavailable.
    """
    url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        'q': city,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric'  # Use 'imperial' for Fahrenheit
    }
    logging.info(f"Fetching weather forecast for {city} from {start_date} to {end_date}")
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        logging.info("Weather data fetched successfully.")
        return data
    except requests.exceptions.HTTPError as http_err:
        logging.error(f'HTTP error occurred while fetching weather: {http_err}')
        return {}
    except requests.exceptions.ConnectionError as conn_err:
        logging.error(f'Connection error occurred while fetching weather: {conn_err}')
        return {}
    except requests.exceptions.Timeout as timeout_err:
        logging.error(f'Timeout error occurred while fetching weather: {timeout_err}')
        return {}
    except requests.exceptions.RequestException as req_err:
        logging.error(f'An error occurred while fetching weather: {req_err}')
        return {}
    except ValueError as json_err:
        logging.error(f'Error parsing JSON: {json_err}')
        return {}

def filter_forecast_by_date(forecast_data, start_date, end_date):
    """
    Filters the forecast data to include only the entries within the specified date range.

    Parameters:
        forecast_data (dict): The JSON data returned by the OpenWeatherMap API.
        start_date (datetime): Start date as a datetime object.
        end_date (datetime): End date as a datetime object.

    Returns:
        list: List of forecast entries within the date range.
    """
    filtered = []
    for entry in forecast_data.get('list', []):
        forecast_time = datetime.strptime(entry['dt_txt'], '%Y-%m-%d %H:%M:%S')
        if start_date <= forecast_time <= end_date:
            filtered.append(entry)
    logging.info(f"Filtered {len(filtered)} forecast entries.")
    return filtered

def display_weather(forecast_entries):
    """
    Displays the weather forecast in a readable format.

    Parameters:
        forecast_entries (list): List of forecast entries.
    """
    if not forecast_entries:
        print("No weather data available for the specified dates.")
        return

    print("\nWeather Forecast:")
    for entry in forecast_entries:
        dt = entry['dt_txt']
        temp = entry['main']['temp']
        description = entry['weather'][0]['description']
        print(f"{dt}: {temp}°C, {description.capitalize()}")
