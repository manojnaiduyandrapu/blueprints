import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Define the list of cities
cities = [
    "Los Angeles", "San Francisco", "San Diego", "Sacramento",
    "San Jose", "Fresno", "Long Beach", "Oakland",
    "Bakersfield", "Anaheim"
]

# Define the date range
start_date = datetime(2024, 12, 1)
end_date = datetime(2025, 12, 31)
delta = end_date - start_date

# Initialize list to hold data
data = []

# Function to generate synthetic weather data
def generate_weather(city, date):
    # Example synthetic patterns; you can adjust these based on real climate data
    month = date.month
    # Temperature in Celsius
    if city in ["San Francisco", "Oakland"]:
        temp_mean = 15 + 10 * np.sin((month-1) / 12 * 2 * np.pi)
    elif city in ["Los Angeles", "San Diego", "Long Beach", "Anaheim"]:
        temp_mean = 20 + 8 * np.sin((month-1) / 12 * 2 * np.pi)
    elif city in ["Sacramento", "Fresno", "Bakersfield", "San Jose"]:
        temp_mean = 18 + 12 * np.sin((month-1) / 12 * 2 * np.pi)
    else:
        temp_mean = 20  # Default

    temperature = np.random.normal(temp_mean, 5)

    # Humidity in %
    if city in ["San Francisco", "Oakland"]:
        humidity = np.random.uniform(60, 90)
    elif city in ["Los Angeles", "San Diego", "Long Beach", "Anaheim"]:
        humidity = np.random.uniform(50, 80)
    else:
        humidity = np.random.uniform(40, 70)

    # Precipitation in mm
    if month in [12, 1, 2, 11, 3]:
        precipitation = np.random.exponential(scale=2.0)  # Wetter months
    else:
        precipitation = np.random.exponential(scale=0.5)  # Drier months

    # Wind speed in km/h
    wind_speed = np.random.uniform(5, 25)

    return {
        "Date": date.strftime("%Y-%m-%d"),
        "City": city,
        "Temperature_C": round(temperature, 1),
        "Humidity_%": round(humidity, 1),
        "Precipitation_mm": round(precipitation, 1),
        "Wind_Speed_km_h": round(wind_speed, 1)
    }

# Generate data for each day and each city
for i in range(delta.days + 1):
    current_date = start_date + timedelta(days=i)
    for city in cities:
        weather = generate_weather(city, current_date)
        data.append(weather)

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv("weather_data.csv", index=False)

print("Synthetic weather data has been generated and saved to 'weather_data.csv'.")
