# Travel Planner Application

Welcome to the Multi-City Travel Planner! This application helps you plan comprehensive, multi-city trips by finding flight deals, hotel accommodations, and providing detailed travel itineraries. Additionally, the app integrates weather information, calculates distances, and suggests nearby places to explore.

## Features

- **Flight & Hotel Deals**: Get flight and accommodation deals for multiple destinations, using APIs for flight and hotel searches.
- **Travel Itinerary Generation**: Automatically generate a day-by-day travel itinerary using OpenAI's GPT model, including activities and attractions near your accommodation.
- **Weather Forecast**: Fetch weather forecasts for the trip duration using the OpenWeather API.
- **Budget Management**: Manage your travel budget, including flights, accommodations, and remaining budget for daily expenses.
- **Distance Calculations**: Calculate distances and durations between locations using Google Distance Matrix and Haversine formulas.

## Installation & Setup

### Prerequisites
- Python 3.8+
- Pip (Python package manager)
- An API key for OpenAI, Google Maps, and OpenWeather.

### Steps

1. **Create a Virtual Environment (Optional but Recommended)**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
2. 2. **Install Dependencies**:
   Install all necessary dependencies using the following command:
   ```bash
   pip install -r requirements.txt
   ```   
3. **Open Terminal or Command Prompt:**
   - Navigate to your project directory where `main_google_api.py` is located.

4. **Set the Directory:**
   If you are not already in the project directory, use the `cd` (change directory) command:
   ```bash
   cd path/to/cd travel_planner/src/travel_planner
   
5. **Environment Variables**:
   Create a `.env` file in the project root directory and add your API keys:
   ```env
   OPENAI_API_KEY=<Your_OpenAI_API_Key>
   GOOGLE_API_KEY=<Your_Google_API_Key>
   OPENWEATHER_API_KEY=<Your_OpenWeather_API_Key>
   ```
6. **Prepare Weather Data**:
   Ensure that `weather_data.csv` is present in the root directory. This CSV file should include historical or forecasted weather data.

### Running the Application

### Example 1:
To start the application, run the following command:
```bash
python main.py
```
The program will prompt you to enter your travel plans in natural language, including origin, destinations, dates, and preferences. Example input:
```
I want to travel from New York to Los Angeles, starting on 2024-12-23 and ending on 2024-12-28, with a budget of $4500.
```
### output:
(.venv) (base) manojnaiduyandrapu@Manojs-MacBook-Pro travel_planner % python3 main_google_api.py
2024-12-04 11:20:55,762 - INFO - API queries_quota: 60
2024-12-04 11:20:55,784 - INFO - Weather data loaded successfully from CSV.
Welcome to the Multi-City Travel Planner!
Enter your travel plans (e.g., 'I want to travel from New York to Los Angeles, starting on 2024-12-23 and ending on 2024-12-28, with a budget of $4500, preferring entire rooms and pet-friendly accommodations'): I want to travel from New York to Los Angeles, starting on 2024-12-23 and ending on 2024-12-28, with a budget of $4500.
2024-12-04 11:21:08,139 - INFO - OpenAI response: ```json
{
  "origin": "New York",
  "destinations": ["Los Angeles"],
  "start_date": "2024-12-23",
  "end_date": "2024-12-28",
  "budget": 4500
}
```
2024-12-04 11:21:08,139 - INFO - Extracted travel data: {'origin': 'New York', 'destinations': ['Los Angeles'], 'start_date': '2024-12-23', 'end_date': '2024-12-28', 'budget': 4500}
2024-12-04 11:21:08,146 - INFO - Processing trip from New York to Los Angeles from 2024-12-23 00:00:00 to 2024-12-28 00:00:00

Fetching deals for: New York to Los Angeles
2024-12-04 11:21:08,683 - INFO - Found 5 flight deals.
Selected Flight: Southwest Airlines at $320, Duration: 6h 40m
2024-12-04 11:21:08,979 - INFO - Straight-line distance between New York and Los Angeles: 3935.54 km
2024-12-04 11:21:09,776 - INFO - Found 5 hotel deals.
Selected Hotel: City Lights Motel at $130 per night, Rating: 3.9

Total Flight Cost: $320.00
Total Hotel Cost: $650.00
Remaining Budget for Daily Expenses and Activities: $3530.00

Weather Forecast for Los Angeles:
Date         City            Temp (C)   Humidity (%)    Precipitation (mm)   Wind Speed (km/h)   
--------------------------------------------------------------------------------
2024-12-23   Los Angeles     13.6       64.5            2.0                  6.9                 
2024-12-24   Los Angeles     22.0       53.6            7.6                  9.2                 
2024-12-25   Los Angeles     22.8       53.9            3.5                  6.2                 
2024-12-26   Los Angeles     17.1       55.3            2.4                  21.3                
2024-12-27   Los Angeles     19.8       78.3            0.0                  16.2                
2024-12-28   Los Angeles     10.6       73.7            0.6                  23.9                
2024-12-04 11:21:09,949 - INFO - Processed weather data for itinerary.
2024-12-04 11:21:09,949 - INFO - Searching for nearby places around (34.0443197, -118.2641283) within 5000 meters.
2024-12-04 11:21:10,243 - INFO - Found 20 nearby places.
2024-12-04 11:21:10,244 - INFO - Fetching distance and duration from 34.0443197,-118.2641283 to 34.0553454,-118.249845 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:21:10,411 - INFO - Distance: 2.2 km, Duration: 34 mins
2024-12-04 11:21:10,411 - INFO - Fetching distance and duration from 34.0443197,-118.2641283 to 34.0159905,-118.2861447 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:21:10,583 - INFO - Distance: 4.4 km, Duration: 1 hour 1 min
2024-12-04 11:21:10,583 - INFO - Fetching distance and duration from 34.0443197,-118.2641283 to 34.0637293,-118.223954 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:21:10,757 - INFO - Distance: 5.8 km, Duration: 1 hour 24 mins
2024-12-04 11:21:10,757 - INFO - Fetching distance and duration from 34.0443197,-118.2641283 to 34.0171448,-118.2886635 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:21:10,934 - INFO - Distance: 4.3 km, Duration: 1 hour 1 min
2024-12-04 11:21:10,934 - INFO - Fetching distance and duration from 34.0443197,-118.2641283 to 34.0682286,-118.2318135 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:21:11,093 - INFO - Distance: 4.7 km, Duration: 1 hour 8 mins
2024-12-04 11:21:11,093 - INFO - Generating itinerary with OpenAI.
2024-12-04 11:21:26,467 - INFO - Itinerary generated successfully.

Your Comprehensive Multi-City Itinerary:

---

**Leg: New York to Los Angeles**
Distance: 3935.54 km, Flight Duration: 6h 40m

Here’s a detailed travel itinerary for your trip from New York to Los Angeles from December 23 to December 28, 2024. You will be staying at City Lights Motel, costing $130 per night. This itinerary takes into account nearby attractions, estimated travel times, distances, and remains within your budget of $3530 for daily expenses, activities, dining, and transportation.

### **Trip Budget Overview**
- **Accommodation Cost**: 5 nights × $130 = **$650**
- **Remaining Budget for Daily Expenses**: **$3530 - $650 = $2880**

### **Day 1: December 23, 2024 (Monday)**
- **Arrival in Los Angeles**
- **Check-in at City Lights Motel**: $130
- **Lunch at The Pie Hole** (nearby bakery): Estimated cost: $20
- **After Lunch**:
    - **Visit: Walt Disney Concert Hall**
        - Distance from motel: 2.2 km (Approx. 34 mins walk)
        - Duration: 1.5 hours (including walking)
        - **Cost**: Free
- **Dinner at Bestia** (Italian restaurant): Estimated cost: $75
- **Evening Activity**: Stroll around the LA Live area.
  
**Daily Cost Summary**: $130 (hotel) + $20 (lunch) + $75 (dinner) = **$225**

--- 

### **Day 2: December 24, 2024 (Tuesday)**
- **Breakfast at motel or nearby cafe**: Estimated cost: $15
- **Visit: California Science Center**
    - Distance from motel: 4.4 km (Approx. 1 hour 1 min walk or $5 transit)
    - Duration: 3 hours
    - **Cost**: Free
- **Lunch at the Science Center Café**: Estimated cost: $25
- **Visit: Natural History Museum of Los Angeles County**
    - Distance from California Science Center: 1.9 km (Approx. 25 mins walk)
    - Duration: 2 hours
    - **Cost**: $15 (adult ticket)
- **Dinner at In-N-Out Burger**: Estimated cost: $25
- **Return to Motel**: Using public transit or walk back.

**Daily Cost Summary**: $130 (hotel) + $15 (breakfast) + $5 (transit) + $25 (lunch) + $15 (museum ticket) + $25 (dinner) = **$215**

---

### **Day 3: December 25, 2024 (Wednesday)**
- **Breakfast at motel**: Estimated cost: $15
- **Visit: Los Angeles State Historic Park**
    - Distance from motel: 4.7 km (Approx. 1 hour 8 mins walk)
    - Duration: 1.5 hours
    - **Cost**: Free
- **Lunch at a nearby deli**: Estimated cost: $20
- **Free Time**: Explore local shops and sights near the park.
- **Dinner at Grand Central Market**: Estimated cost: $40
- **Return to motel**: Walk back or take transit.

**Daily Cost Summary**: $130 (hotel) + $15 (breakfast) + $20 (lunch) + $40 (dinner) = **$205**

---

### **Day 4: December 26, 2024 (Thursday)**
- **Breakfast at motel**: Estimated cost: $15
- **Day Trip to San Antonio Winery**
    - Distance from motel: 5.8 km (Approx. 1 hour 24 mins walk or $7 transit)
    - Duration: 2 hours (tasting)
    - **Cost**: $15 (wine tasting + cheese pairing)
- **Lunch at the Winery**: Estimated cost: $25
- **Visit: Griffith Park (Hiking Trails)**
    - Distance from winery: 10 km (approx. 20 mins drive; consider Uber/Lyft $20 round trip).
    - Duration: 2 hours of hiking.
    - **Cost**: Free
- **Dinner at nearby restaurant**: Estimated cost: $30

**Daily Cost Summary**: $130 (hotel) + $15 (breakfast) + $7 (transit) + $15 (tasting) + $25 (lunch) + $20 (Uber) + $30 (dinner) = **$212**

---

### **Day 5: December 27, 2024 (Friday)**
- **Breakfast at motel**: Estimated cost: $15
- **Visit: Los Angeles County Museum of Art (LACMA)**
    - Distance from motel: 6.5 km (approx. 15 mins transit; $5)
    - Duration: 2.5 hours
    - **Cost**: $20 (adult ticket)
- **Lunch at LACMA Café**: Estimated cost: $25
- **Afternoon Free for shopping at The Grove**
    - Distance from LACMA: 1.5 km (15 min walk)
- **Dinner at The Grove**: Estimated cost: $30

**Daily Cost Summary**: $130 (hotel) + $15 (breakfast) + $5 (transit) + $20 (ticket) + $25 (lunch) + $30 (dinner) = **$225**

---

### **Day 6: December 28, 2024 (Saturday)**
- **Breakfast at motel**: Estimated cost: $15
- **Check out and Shopping/Exploring Local Neighborhood**
- **Lunch at a local cafe**: Estimated cost $25
- **Depart for Airport**

**Daily Cost Summary**: $130 (hotel) + $15 (breakfast) + $25 (lunch) = **$170**

---

### **Final Summary of Total Costs**
- **Total for Accommodation**: $650
- **Total Daily Expenses**: $225 (Day 1) + $215 (Day 2) + $205 (Day 3) + $212 (Day 4) + $225 (Day 5) + $170 (Day 6) = **$1297**
- **Total Trip Cost**: $650 (accommodation) + $1297 (daily expenses) = **$1947**
- **Remaining Budget**: $3530 - $1947 = **$1583**

### **Conclusion**
This itinerary maximizes your experience in Los Angeles while staying within your budget. Enjoy your trip!
```

### Example 2: Mutli-city

To start the application, run the following command:
```bash
python main.py
```
The program will prompt you to enter your travel plans in natural language, including origin, destinations, dates, and preferences. Example input:
```
I want to travel from New York to california on 23rd december and return on 31st december under a budget of 6000$.  
```
### output:

2024-12-04 11:33:41,880 - INFO - API queries_quota: 60
2024-12-04 11:33:41,889 - INFO - Weather data loaded successfully from CSV.
Welcome to the Multi-City Travel Planner!
Enter your travel plans (e.g., 'I want to travel from New York to Los Angeles, starting on 2024-12-23 and ending on 2024-12-28, with a budget of $4500, preferring entire rooms and pet-friendly accommodations'): I want to travel from New York to california on 23rd december and return on 31st december under a budget of 6000$.    
2024-12-04 11:34:30,148 - INFO - OpenAI response: ```json
{
  "origin": "New York",
  "destinations": ["Los Angeles", "San Francisco", "San Diego", "Sacramento", "San Jose"],
  "start_date": "2024-12-23",
  "end_date": "2024-12-31",
  "budget": 6000
}
```
2024-12-04 11:34:30,148 - INFO - Extracted travel data: {'origin': 'New York', 'destinations': ['Los Angeles', 'San Francisco', 'San Diego', 'Sacramento', 'San Jose'], 'start_date': '2024-12-23', 'end_date': '2024-12-31', 'budget': 6000}
2024-12-04 11:34:30,149 - INFO - Processing trip from New York to Los Angeles from 2024-12-23 00:00:00 to 2024-12-31 00:00:00

Fetching deals for: New York to Los Angeles
2024-12-04 11:34:30,618 - INFO - Found 5 flight deals.
Selected Flight: Southwest Airlines at $320, Duration: 6h 40m
2024-12-04 11:34:30,852 - INFO - Straight-line distance between New York and Los Angeles: 3935.54 km
2024-12-04 11:34:31,278 - INFO - Found 5 hotel deals.
Selected Hotel: City Lights Motel at $130 per night, Rating: 3.9
2024-12-04 11:34:31,354 - INFO - Processing trip from Los Angeles to San Francisco from 2024-12-23 00:00:00 to 2024-12-31 00:00:00

Fetching deals for: Los Angeles to San Francisco
2024-12-04 11:34:31,813 - INFO - Found 5 flight deals.
Selected Flight: Southwest Airlines at $340, Duration: 6h 45m
2024-12-04 11:34:31,968 - INFO - Straight-line distance between Los Angeles and San Francisco: 558.96 km
2024-12-04 11:34:32,498 - INFO - Found 5 hotel deals.
Selected Hotel: Mission District Motel at $140 per night, Rating: 3.8
2024-12-04 11:34:32,605 - INFO - Processing trip from San Francisco to San Diego from 2024-12-23 00:00:00 to 2024-12-31 00:00:00

Fetching deals for: San Francisco to San Diego
2024-12-04 11:34:33,028 - INFO - Found 5 flight deals.
Selected Flight: Southwest Airlines at $300, Duration: 6h 30m
2024-12-04 11:34:33,188 - INFO - Straight-line distance between San Francisco and San Diego: 737.61 km
2024-12-04 11:34:33,659 - INFO - Found 5 hotel deals.
Selected Hotel: Old Town Motel at $120 per night, Rating: 3.7
2024-12-04 11:34:33,729 - INFO - Processing trip from San Diego to Sacramento from 2024-12-23 00:00:00 to 2024-12-31 00:00:00

Fetching deals for: San Diego to Sacramento
2024-12-04 11:34:34,403 - INFO - Found 5 flight deals.
Selected Flight: Southwest Airlines at $310, Duration: 6h 30m
2024-12-04 11:34:34,593 - INFO - Straight-line distance between San Diego and Sacramento: 760.19 km
2024-12-04 11:34:35,026 - INFO - Found 5 hotel deals.
Selected Hotel: Natomas Motel at $110 per night, Rating: 3.6
2024-12-04 11:34:35,102 - INFO - Processing trip from Sacramento to San Jose from 2024-12-23 00:00:00 to 2024-12-31 00:00:00

Fetching deals for: Sacramento to San Jose
2024-12-04 11:34:35,523 - INFO - Found 5 flight deals.
Selected Flight: Southwest Airlines at $330, Duration: 6h 35m
2024-12-04 11:34:35,668 - INFO - Straight-line distance between Sacramento and San Jose: 142.01 km
2024-12-04 11:34:36,085 - INFO - Found 5 hotel deals.
Selected Hotel: Berryessa Motel at $130 per night, Rating: 3.9

Total Flight Cost: $1600.00
Total Hotel Cost: $1020.00
Remaining Budget for Daily Expenses and Activities: $3380.00

Weather Forecast for Los Angeles:
Date         City            Temp (C)   Humidity (%)    Precipitation (mm)   Wind Speed (km/h)   
--------------------------------------------------------------------------------
2024-12-23   Los Angeles     13.6       64.5            2.0                  6.9                 
2024-12-24   Los Angeles     22.0       53.6            7.6                  9.2                 
2024-12-25   Los Angeles     22.8       53.9            3.5                  6.2                 
2024-12-04 11:34:36,169 - INFO - Processed weather data for itinerary.

Weather Forecast for San Francisco:
Date         City            Temp (C)   Humidity (%)    Precipitation (mm)   Wind Speed (km/h)   
--------------------------------------------------------------------------------
2024-12-25   San Francisco   9.1        87.2            1.7                  24.2                
2024-12-26   San Francisco   10.7       75.0            0.9                  19.0                
2024-12-27   San Francisco   15.9       82.3            0.7                  5.1                 
2024-12-04 11:34:36,175 - INFO - Processed weather data for itinerary.

Weather Forecast for San Diego:
Date         City            Temp (C)   Humidity (%)    Precipitation (mm)   Wind Speed (km/h)   
--------------------------------------------------------------------------------
2024-12-27   San Diego       20.1       67.7            5.8                  10.1                
2024-12-28   San Diego       17.0       57.5            1.2                  16.6                
2024-12-29   San Diego       7.2        72.3            6.8                  16.6                
2024-12-04 11:34:36,181 - INFO - Processed weather data for itinerary.

Weather Forecast for Sacramento:
Date         City            Temp (C)   Humidity (%)    Precipitation (mm)   Wind Speed (km/h)   
--------------------------------------------------------------------------------
2024-12-29   Sacramento      16.4       57.5            1.2                  14.8                
2024-12-30   Sacramento      12.0       60.6            0.9                  19.5                
2024-12-04 11:34:36,187 - INFO - Processed weather data for itinerary.

Weather Forecast for San Jose:
Date         City            Temp (C)   Humidity (%)    Precipitation (mm)   Wind Speed (km/h)   
--------------------------------------------------------------------------------
2024-12-30   San Jose        17.3       43.9            5.9                  6.7                 
2024-12-31   San Jose        22.8       64.0            0.2                  5.7                 
2024-12-04 11:34:36,192 - INFO - Processed weather data for itinerary.
2024-12-04 11:34:36,193 - INFO - Searching for nearby places around (34.0443197, -118.2641283) within 5000 meters.
2024-12-04 11:34:36,483 - INFO - Found 20 nearby places.
2024-12-04 11:34:36,483 - INFO - Fetching distance and duration from 34.0443197,-118.2641283 to 34.0553454,-118.249845 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:34:36,586 - INFO - Distance: 2.2 km, Duration: 34 mins
2024-12-04 11:34:36,586 - INFO - Fetching distance and duration from 34.0443197,-118.2641283 to 34.0159905,-118.2861447 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:34:36,687 - INFO - Distance: 4.4 km, Duration: 1 hour 1 min
2024-12-04 11:34:36,687 - INFO - Fetching distance and duration from 34.0443197,-118.2641283 to 34.0637293,-118.223954 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:34:36,794 - INFO - Distance: 5.8 km, Duration: 1 hour 24 mins
2024-12-04 11:34:36,794 - INFO - Fetching distance and duration from 34.0443197,-118.2641283 to 34.0171448,-118.2886635 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:34:36,895 - INFO - Distance: 4.3 km, Duration: 1 hour 1 min
2024-12-04 11:34:36,895 - INFO - Fetching distance and duration from 34.0443197,-118.2641283 to 34.0682286,-118.2318135 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:34:36,994 - INFO - Distance: 4.7 km, Duration: 1 hour 8 mins
2024-12-04 11:34:36,994 - INFO - Generating itinerary with OpenAI.
2024-12-04 11:34:48,580 - INFO - Itinerary generated successfully.
2024-12-04 11:34:48,580 - INFO - Searching for nearby places around (37.7554482, -122.4187695) within 5000 meters.
2024-12-04 11:34:48,732 - INFO - Found 20 nearby places.
2024-12-04 11:34:48,732 - INFO - Fetching distance and duration from 37.7554482,-122.4187695 to 37.7762528,-122.4327556 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:34:48,835 - INFO - Distance: 3.3 km, Duration: 50 mins
2024-12-04 11:34:48,835 - INFO - Fetching distance and duration from 37.7554482,-122.4187695 to 37.7784136,-122.3892168 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:34:48,948 - INFO - Distance: 4.6 km, Duration: 1 hour 4 mins
2024-12-04 11:34:48,948 - INFO - Fetching distance and duration from 37.7554482,-122.4187695 to 37.7608223,-122.4266135 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:34:49,046 - INFO - Distance: 1.3 km, Duration: 18 mins
2024-12-04 11:34:49,046 - INFO - Fetching distance and duration from 37.7554482,-122.4187695 to 37.7856437,-122.4021904 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:34:49,151 - INFO - Distance: 4.1 km, Duration: 58 mins
2024-12-04 11:34:49,151 - INFO - Fetching distance and duration from 37.7554482,-122.4187695 to 37.7857182,-122.4010508 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:34:49,250 - INFO - Distance: 4.2 km, Duration: 58 mins
2024-12-04 11:34:49,250 - INFO - Generating itinerary with OpenAI.
2024-12-04 11:35:09,981 - INFO - Itinerary generated successfully.
2024-12-04 11:35:09,981 - INFO - Searching for nearby places around (32.7514589, -117.2007541) within 5000 meters.
2024-12-04 11:35:10,289 - INFO - Found 20 nearby places.
2024-12-04 11:35:10,289 - INFO - Fetching distance and duration from 32.7514589,-117.2007541 to 32.7642958,-117.2264396 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:35:10,430 - INFO - Distance: 4.2 km, Duration: 58 mins
2024-12-04 11:35:10,431 - INFO - Fetching distance and duration from 32.7514589,-117.2007541 to 32.7549063,-117.1976407 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:35:10,585 - INFO - Distance: 0.7 km, Duration: 10 mins
2024-12-04 11:35:10,585 - INFO - Fetching distance and duration from 32.7514589,-117.2007541 to 32.7713078,-117.2159781 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:35:10,686 - INFO - Distance: 3.4 km, Duration: 47 mins
2024-12-04 11:35:10,686 - INFO - Fetching distance and duration from 32.7514589,-117.2007541 to 32.7529044,-117.1945102 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:35:10,828 - INFO - Distance: 1.0 km, Duration: 15 mins
2024-12-04 11:35:10,828 - INFO - Fetching distance and duration from 32.7514589,-117.2007541 to 32.7535127,-117.1958723 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:35:10,983 - INFO - Distance: 0.8 km, Duration: 12 mins
2024-12-04 11:35:10,983 - INFO - Generating itinerary with OpenAI.
2024-12-04 11:35:26,468 - INFO - Itinerary generated successfully.
2024-12-04 11:35:26,468 - INFO - Searching for nearby places around (38.6375037, -121.4764671) within 5000 meters.
2024-12-04 11:35:26,703 - INFO - Found 20 nearby places.
2024-12-04 11:35:26,703 - INFO - Fetching distance and duration from 38.6375037,-121.4764671 to 38.63219199999999,-121.5112126 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:35:26,849 - INFO - Distance: 5.3 km, Duration: 1 hour 13 mins
2024-12-04 11:35:26,849 - INFO - Fetching distance and duration from 38.6375037,-121.4764671 to 38.6300781,-121.4890199 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:35:26,992 - INFO - Distance: 2.2 km, Duration: 30 mins
2024-12-04 11:35:26,992 - INFO - Fetching distance and duration from 38.6375037,-121.4764671 to 38.642671,-121.4905793 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:35:27,131 - INFO - Distance: 2.6 km, Duration: 36 mins
2024-12-04 11:35:27,131 - INFO - Fetching distance and duration from 38.6375037,-121.4764671 to 38.6301599,-121.4549011 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:35:27,278 - INFO - Distance: 2.7 km, Duration: 38 mins
2024-12-04 11:35:27,278 - INFO - Fetching distance and duration from 38.6375037,-121.4764671 to 38.6651216,-121.4713265 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:35:27,416 - INFO - Distance: 8.2 km, Duration: 1 hour 52 mins
2024-12-04 11:35:27,416 - INFO - Generating itinerary with OpenAI.
2024-12-04 11:35:36,915 - INFO - Itinerary generated successfully.
2024-12-04 11:35:36,915 - INFO - Searching for nearby places around (37.3783397, -121.8957313) within 5000 meters.
2024-12-04 11:35:37,134 - INFO - Found 20 nearby places.
2024-12-04 11:35:37,134 - INFO - Fetching distance and duration from 37.3783397,-121.8957313 to 37.3712423,-121.919397 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:35:37,276 - INFO - Distance: 3.3 km, Duration: 47 mins
2024-12-04 11:35:37,276 - INFO - Fetching distance and duration from 37.3783397,-121.8957313 to 37.3696404,-121.9133539 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:35:37,375 - INFO - Distance: 3.5 km, Duration: 50 mins
2024-12-04 11:35:37,375 - INFO - Fetching distance and duration from 37.3783397,-121.8957313 to 37.3595633,-121.875433 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:35:37,537 - INFO - Distance: 3.9 km, Duration: 55 mins
2024-12-04 11:35:37,537 - INFO - Fetching distance and duration from 37.3783397,-121.8957313 to 37.3337262,-121.8899245 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:35:37,701 - INFO - Distance: 6.0 km, Duration: 1 hour 25 mins
2024-12-04 11:35:37,701 - INFO - Fetching distance and duration from 37.3783397,-121.8957313 to 37.3433081,-121.9034378 using Google Distance Matrix API with mode 'walking'.
2024-12-04 11:35:37,868 - INFO - Distance: 5.2 km, Duration: 1 hour 14 mins
2024-12-04 11:35:37,868 - INFO - Generating itinerary with OpenAI.
2024-12-04 11:35:48,566 - INFO - Itinerary generated successfully.

Your Comprehensive Multi-City Itinerary:

---

**Leg: New York to Los Angeles**
Distance: 3935.54 km, Flight Duration: 6h 40m

### Travel Itinerary: New York to Los Angeles
**Trip Duration:** December 23–25, 2024  
**Accommodation:** City Lights Motel, $130/night  
**Total Budget for Daily Expenses:** $3380.00  
**Accommodation Total Cost (2 nights):** $260.00  
**Remaining Budget for Activities/Dining/Transportation:** $3120.00

---

### **Day 1: December 23, 2024**
**Arrival in Los Angeles**  
- **Accommodation Check-in:** City Lights Motel  
- **Cost:** $130.00

**Afternoon**  
- **Lunch at a nearby diner or café:** Approx. $20/person × 2 = $40.00  
- **Visit Walt Disney Concert Hall**  
  - **Distance:** 2.2 km  
  - **Estimated Walking Time:** 34 minutes  
  - **Estimated Admission Cost:** Free (depends on availability of guided tours; budget $20 just in case)  
- **Explore the concert hall exterior and surrounding park area.**

**Evening**  
- **Dinner at nearby restaurant:** Approx. $25/person × 2 = $50.00  
- **Return to Motel:** Walk back (2.2 km)  
- **Total Costs for Day 1:**  
  - Accommodation: $130.00  
  - Lunch: $40.00  
  - Admission: $20.00  
  - Dinner: $50.00  
  - **Total:** $240.00

---

### **Day 2: December 24, 2024**  
**Morning**  
- **Breakfast at a local café:** Approx. $15/person × 2 = $30.00  
- **Visit California Science Center**  
  - **Distance:** 4.4 km  
  - **Estimated Walking Time:** 1 hour 1 minute  
  - **Admission Cost:** $15/person × 2 = $30.00  

**Afternoon**  
- **Exploration Time at Science Center:** Approx. 2 hours (10:00 AM - 12:00 PM)
- **Lunch at the Science Center Café:** Approx. $20/person × 2 = $40.00  
- **Visit Natural History Museum of Los Angeles County**  
  - **Distance:** 0.6 km (approx. 10-minute walk from the Science Center)  
  - **Admission Cost:** $15/person × 2 = $30.00  

**Evening**  
- **Return walk to City Lights Motel:** 4.3 km (approx. 1 hour 1-minute walk)  
- **Dinner near the motel:** Approx. $25/person × 2 = $50.00  
- **Total Costs for Day 2:**  
  - Accommodation: $130.00 (already paid)  
  - Breakfast: $30.00  
  - Science Center Admission: $30.00  
  - Lunch: $40.00  
  - Museum Admission: $30.00  
  - Dinner: $50.00  
  - **Total:** $310.00

---

### **Day 3: December 25, 2024**  
**Morning**    
- **Breakfast at a local café:** Approx. $15/person × 2 = $30.00  
- **Visit Los Angeles State Historic Park**  
  - **Distance:** 4.7 km  
  - **Estimated Walking Time:** 1 hour 8 minutes  
  - **Admission Cost:** Free (park is open to the public)  

**Afternoon**  
- **Lunch at a nearby restaurant:** Approx. $25/person × 2 = $50.00  
- **Relaxing at the park, taking in the views and nature:** Approx. 1 hour  
- **Explore the nearby San Antonio Winery**  
  - **Distance:** 5.8 km (1 hour 24 minutes walking)  
  - **Tasting Experience Cost:** Approx. $15/person × 2 = $30.00  

**Evening**  
- **Return walk to motel:** 5.8 km (about 1 hour 24 minutes)  
- **Dinner near the motel:** Approx. $25/person × 2 = $50.00  
- **Total Costs for Day 3:**  
  - Accommodation: $130.00 (already paid)  
  - Breakfast: $30.00  
  - Lunch: $50.00  
  - Winery Tasting: $30.00  
  - Dinner: $50.00  
  - **Total:** $260.00 

---

### **Summary of Totals**  
- **Day 1 Total:** $240.00  
- **Day 2 Total:** $310.00  
- **Day 3 Total:** $260.00  
- **Total Trip Expense:** $810.00  
- **Remaining Budget:** $3120.00 - $810.00 = **$2310.00**  

**This budget allows for additional activities, shopping, or bidding farewell to LA with a special meal! Enjoy your trip!**

---

**Leg: Los Angeles to San Francisco**
Distance: 558.96 km, Flight Duration: 6h 45m

Here's a detailed daily travel itinerary for your trip from Los Angeles to San Francisco, including activities, estimated times and distances, along with a budget breakdown for each day.

### Travel Itinerary: Los Angeles to San Francisco
**Dates: December 25, 2024 - December 27, 2024**  
**Accommodation: Mission District Motel ($140/night)**

---

### Day 1: December 25, 2024 (Wednesday)
**Check-in at Mission District Motel**  
- **Time:** 3:00 PM
- **Cost:** $140 (paid)  

#### Evening Activities 
1. **Dinner at La Taqueria (Mission District)**
   - **Distance:** 1 km from motel
   - **Duration:** 15 mins walk
   - **Cost:** $20 per person (approx. $40 for two)

2. **Visit Mission Dolores Park**
   - **Distance:** 1.3 km from La Taqueria
   - **Duration:** 18 mins walk
   - **Activities:** Stroll in the park and enjoy the view of the city.
   - **Cost:** Free

**Summary of Day 1 Estimated Costs:**  
- **Accommodation:** $140  
- **Dinner:** $40  
- **Total:** $180

---

### Day 2: December 26, 2024 (Thursday)
**Breakfast Included at Motel**

#### Morning Activities
1. **Visit the Painted Ladies**
   - **Distance:** 3.3 km from motel
   - **Duration:** 50 mins walk
   - **Cost:** Free

2. **Explore Alamo Square Park**
   - **Distance:** 0.2 km from Painted Ladies
   - **Duration:** 5 mins walk
   - **Cost:** Free

#### Lunch 
- **California Diner**
  - **Distance:** 0.5 km from Alamo Square
  - **Duration:** 8 mins walk
  - **Cost:** $25 per person (approx. $50 for two)

#### Afternoon Activities
3. **Visit the San Francisco Museum of Modern Art (SFMOMA)**
   - **Distance:** 4.2 km from California Diner
   - **Duration:** 20 mins ride (Uber/Lyft or public transport)
   - **Cost:** $25 per person (approx. $50 for two) 

4. **Yerba Buena Center for the Arts**
   - **Distance:** 0.5 km from SFMOMA
   - **Duration:** 7 mins walk
   - **Cost:** Free

#### Evening Activities
- **Dinner at The American Grilled Cheese Kitchen**
  - **Distance:** 0.8 km from Yerba Buena
  - **Duration:** 10 mins walk
  - **Cost:** $25 per person (approx. $50 for two)

**Summary of Day 2 Estimated Costs:**  
- **Breakfast:** Included  
- **Lunch:** $50  
- **SFMOMA Tickets:** $50  
- **Dinner:** $50  
- **Total:** $150

---

### Day 3: December 27, 2024 (Friday)
**Breakfast Included at Motel**

#### Morning Activities
1. **Visit Oracle Park**
   - **Distance:** 4.6 km from motel
   - **Duration:** 1 hour 4 mins walk
   - **Cost:** Free

#### Late Morning
- **Explore Embarcadero and Pier 39**
  - **Distance:** 1.2 km from Oracle Park
  - **Duration:** 15 mins walk
  - **Cost:** Free

#### Lunch
- **Eat at Boudin Bakery Cafe at the Wharf**
  - **Distance:** 0.5 km from Pier 39
  - **Duration:** 8 mins walk
  - **Cost:** $30 per person (approx. $60 for two)

#### Afternoon Activities
2. **Explore Fisherman’s Wharf**
   - **Walking around, shops, street performers**
   - **Cost:** Free

3. **Optional: Bay Cruise**
   - **Duration:** 1 hour
   - **Cost:** $40 per person (approx. $80 for two)

#### Evening Activities 
- **Dinner at Fog Harbor Fish House**
  - **Distance:** 1.0 km from Fisherman’s Wharf
  - **Duration:** 15 mins walk
  - **Cost:** $40 per person (approx. $80 for two)

**Summary of Day 3 Estimated Costs:**  
- **Breakfast:** Included  
- **Lunch:** $60  
- **Bay Cruise:** $80  
- **Dinner:** $80  
- **Total:** $220

---

### Budget Overview
- **Accommodation (2 nights):** $280  
- **Day 1 Total:** $180  
- **Day 2 Total:** $150  
- **Day 3 Total:** $220  
- **Total Trip Cost:** $830  
- **Remaining Budget:** $3380.00 - $830 = $2550.00

### Additional Notes
- This itinerary allows flexibility for weather changes. Carry an umbrella for Day 1 and Day 2 due to expected rain.
- Distances and durations are based on walking; consider Uber or public transport if the weather is unfavorable or if you prefer not to walk those distances.
- Be sure to check for any special events or seasonal activities in San Francisco during your stay. 

Enjoy your trip!

---

**Leg: San Francisco to San Diego**
Distance: 737.61 km, Flight Duration: 6h 30m

### **San Francisco to San Diego Travel Itinerary (December 27-29, 2024)**

**Accommodation:**
- Old Town Motel: $120 per night
- Total for 2 nights: $240

**Budget Overview:**
- Total budget for daily expenses, activities, dining, and transportation: $3380
- Accommodation cost: $240
- Remaining budget for activities, dining, and transport: $3140

---

### **Day 1: December 27, 2024 (Friday)**
**Morning:**
- **Arrival in San Diego**
  - Drive from San Francisco to San Diego (approx. 7.5 hours, 500 miles)
  - Departure at 7:00 AM; Arrival at 2:30 PM.
  
**Check-in:**
- **Old Town Motel** (check-in at 3:00 PM)

**Afternoon:**
- **Lunch at Old Town Mexican Cafe** 
  - Estimated cost: $25 per person
  - Duration: 1 hour
  - Distance: 0.5 km (10 mins walk)
  
- **Visit Old Town San Diego State Historic Park**
  - Distance: 0.7 km (10 mins walk from lunch)
  - Duration: 2 hours (Explore historic buildings and shops)
  - Estimated entry cost: Free

**Evening:**
- **Dinner at Casa Guadalajara**
  - Estimated cost: $30 per person
  - Duration: 1.5 hours
  - Distance: 1 km (15 mins walk from the park)

**Summary of Day 1 Costs:**
- Lunch: $50
- Dinner: $60
- **Total Day 1 Estimated Cost: $110**
  
---

### **Day 2: December 28, 2024 (Saturday)**
**Morning:**
- **Breakfast at The Cottage Restaurant**
  - Estimated cost: $15 per person
  - Duration: 1 hour
  - Distance: 1 km (12 mins walk from the motel)
  
- **Old Town Trolley Tours**
  - Estimated cost: $40 per person (includes a narrated tour of key attractions)
  - Duration: 2 hours
  - Distance: 0.8 km (12 mins walk to the trolley stop)

**Afternoon:**
- **Lunch at a local deli near Balboa Park** 
  - Estimated cost: $20 per person
  - Duration: 1 hour
- **Visit Balboa Park and San Diego Zoo**
  - Estimated entrance cost: $70 (optional: if choosing only Balboa Park, it's free)
  - Duration: 3 hours exploring the park's gardens and free attractions (Zoo cost can be optional if not fitting within budget)
  - Distance: 3 km (10 mins by trolley; consider using rideshare for a quick trip)

**Evening:**
- **Dinner at The Prado in Balboa Park**
  - Estimated cost: $40 per person
  - Duration: 1.5 hours
  
**Summary of Day 2 Costs:**
- Breakfast: $30
- Trolley Tour: $80
- Lunch: $40
- Zoo (optional): $70
- Dinner: $80
- **Total Day 2 Estimated Cost (with zoo): $300 or without zoo: $230**

---

### **Day 3: December 29, 2024 (Sunday)**
**Morning:**
- **Breakfast at the motel**
  - Estimated cost: $10 per person
  - Duration: 1 hour
  
- **Visit Whaley House Museum**
  - Entry Fee: $15 per person
  - Distance: 1.0 km (15 mins walk)
  - Duration: 1 hour
  
**Afternoon:**
- **Explore Fiesta Island**
  - Distance: 3.4 km (short rideshare recommended, approx. $20) 
  - Duration: 2 hours
  
- **Lunch picnic on Fiesta Island**
  - Packed lunch from local deli: $15 per person
  - Duration: 1.5 hours

**Afternoon:**
- **Return to motel and check-out**
  - Departure at 3:00 PM.

**Summary of Day 3 Costs:**
- Breakfast: $20
- Whaley House: $30
- Picnic Lunch: $30
- Rideshare: $20
- **Total Day 3 Estimated Cost: $100**

---

### **Overall Summary of Total Estimated Costs:**
- **Day 1:** $110
- **Day 2 (with zoo):** $300 or (without zoo): $230
- **Day 3:** $100
- **Accommodation:** $240
- **Total Estimated Cost with zoo:** $740 or without zoo: $670

**Final Budget Overview:**
- Total with zoo (including activities, meals, and accommodation): $740
- Total without zoo (including activities, meals, and accommodation): $670
- Remaining budget: $2390 or $2410, providing ample funds for transportation and additional discretionary spending.

This itinerary provides a well-rounded experience in San Diego, balancing cultural exploration, dining, and relaxation within budget. Enjoy your trip!

---

**Leg: San Diego to Sacramento**
Distance: 760.19 km, Flight Duration: 6h 30m

### Travel Itinerary: San Diego to Sacramento
**Dates:** December 29 - December 30, 2024  
**Accommodation:** Natomas Motel - $110/night  
**Remaining Budget for Daily Expenses:** $3380.00  

---

### Day 1: December 29, 2024
**Weather:** 16.4°C, Humidity: 57.5%, Precipitation: 1.2mm  

#### Morning
- **Arrival in Sacramento**  
  - **Travel Distance:** Approximately 500 miles from San Diego  
  - **Estimated Driving Time:** 8 hours  
- **Check-In at Natomas Motel**  
  - **Time:** 3:00 PM  
  - **Cost:** $110  

#### Afternoon
- **Visit Don & June Salvatori California Pharmacy Museum**  
  - **Distance from Motel:** 2.6 km  
  - **Walking Time:** 36 minutes  
  - **Visit Duration:** 1 hour  
  - **Museum Entry Fee:** $10/person  
  - **Total Cost:** $10  

- **Walk to Chuckwagon Park R113**  
  - **Distance:** 2.2 km  
  - **Walking Time:** 30 minutes  
  - **Duration at Park:** 1 hour  

#### Evening
- **Dinner at a Local Restaurant**  
  - **Est. Dinner Cost:** $30/person x 2 = $60  

- **Return to Natomas Motel**  
  - **Walking Distance from Chuckwagon Park back to Motel:** 2.5 km (approx. 30 minutes)  

#### Summary of Day 1 Costs:
- Accommodation: $110  
- Museum Entry Fee: $10  
- Dinner: $60  
- **Total Estimated Cost for Day 1:** $180  
- **Remaining Budget:** $3380 - $180 = $3200  

---

### Day 2: December 30, 2024
**Weather:** 12.0°C, Humidity: 60.6%, Precipitation: 0.9mm  

#### Morning
- **Breakfast**  
  - **Cost:** $15/person x 2 = $30  

- **Visit Tanzanite Community Park**  
  - **Walking Distance from Motel:** 5.3 km  
  - **Walking Time:** 1 hour 13 minutes  
  - **Duration at Park:** 1.5 hours 

#### Afternoon
- **Visit Robert Brookins Park**  
  - **Walking Distance from Tanzanite Community Park:** 2.7 km  
  - **Walking Time:** 38 minutes  
  - **Duration at Park:** 1 hour  

- **Lunch near the Park**  
  - **Cost:** $20/person x 2 = $40  

#### Evening
- **Visit Hansen Ranch Park Site**  
  - **Walking Distance from Robert Brookins Park:** 8.2 km  
  - **Walking Time:** 1 hour 52 minutes  
  - **Duration at Park:** 1 hour  

- **Dinner and Departure**  
  - **Dinner Cost:** $30/person x 2 = $60  

#### Return Drive to San Diego  
- **Estimated Travel Time:** 8 hours  

#### Summary of Day 2 Costs:
- Breakfast: $30  
- Lunch: $40  
- Dinner: $60  
- **Total Estimated Cost for Day 2:** $130  
- **Remaining Budget After Day 2:** $3200 - $130 = $3070  

---

### Final Summary
- **Total Accommodation Cost:** $110  
- **Total Day 1 Costs:** $180  
- **Total Day 2 Costs:** $130  
- **Total Trip Expenses:** $420  
- **Total Remaining Budget:** $3380 - $420 = $2960  

---

### Additional Notes
- Ensure comfortable walking shoes for the planned activities.
- Be prepared for possible rain on Day 1 and dress accordingly.
- Review local dining options in advance to ensure they align with your budget.

---

**Leg: Sacramento to San Jose**
Distance: 142.01 km, Flight Duration: 6h 35m

Here's a detailed travel itinerary for your trip from Sacramento to San Jose on December 30-31, 2024, while staying within your budget of $3380. The itinerary includes nearby attractions, transportation details, activities, dining options, and a summary of daily costs.

### **Day 1: December 30, 2024 (Monday)**

**Morning: Travel from Sacramento to San Jose**  
- **Departure:** 8:00 AM  
- **Duration:** Approximately 1 hour 30 minutes by car (115 miles)  
- **Transportation:** $30 in gas (round trip)

**Accommodation**  
- **Hotel:** Berryessa Motel  
- **Cost:** $130 per night  
- **Check-in:** 10:00 AM

**Late Morning: Brunch**  
- **Location:** The Breakfast Table (3.5 km from the motel)  
- **Cost:** $60 for two  
- **Distance from Motel:** 3.5 km (10 mins by car)

**Afternoon: Casino M8trix**  
- **Activity:** Enjoy some time at Casino M8trix  
- **Duration:** 2 hours  
- **Distance from Brunch:** 3.3 km (6 mins by car)  
- **Cost:** Free entry (set a budget for gaming, say $100)

**Evening: Dinner**  
- **Location:** La Mediterranee (approximately 4.5 km from Casino M8trix)  
- **Cost:** $80 for two  
- **Distance:** 4.5 km (10 mins by car)

**Night: Relax at Hotel**  
- **Return to Motel**  
- **Distance:** 5 km (12 mins by car)

**Daily Summary**  
- **Transportation (gas):** $30  
- **Hotel:** $130  
- **Brunch:** $60  
- **Casino Budget:** $100  
- **Dinner:** $80  
- **Total:** $400  

---

### **Day 2: December 31, 2024 (Tuesday)**

**Morning: Breakfast at Hotel**  
- **Cost:** Included with motel stay

**Late Morning: Visit San Jose Museum of Art**  
- **Activity:** Explore art exhibits  
- **Duration:** 2 hours  
- **Distance from Motel:** 6 km (15 mins by car)  
- **Cost:** $20 per person (Total: $40)

**Afternoon: Lunch at a nearby Café**  
- **Location:** Café Stritch (close to the museum)  
- **Cost:** $70 for two  
- **Duration:** 1 hour  
- **Distance from Museum:** 1 km (5 mins walk)

**Late Afternoon: Relax in Guadalupe River Park**  
- **Activity:** Take a leisurely walk and enjoy the outdoors  
- **Duration:** 1.5 hours  
- **Distance from Café:** 1 km (15 mins walk)

**Evening: Fireworks Show (New Year's Eve)**  
- **Activity:** Head to a popular spot to view fireworks  
- **Location:** San Jose Downtown (12 km away from the park)  
- **Transportation:** $20 for ride-sharing to downtown  
- **Duration:** 2 hours (approx. 8:00 PM - 10:00 PM)   
- **Estimated Cost for Drinks/Snacks:** $60

**Night: Return to Motel**  
- **Distance:** 12 km (20 mins drive)  
  
**Daily Summary**  
- **Transportation (gas plus rideshare):** $50  
- **Hotel:** $130 (already paid for both nights)  
- **Museum Entry:** $40  
- **Lunch:** $70  
- **Dinner/Snacks:** $60  
- **Total:** $350  

### **Overall Budget Summary**  
- **Total for Day 1:** $400  
- **Total for Day 2:** $350  
- **Total for Trip:** $750  
- **Remaining Budget:** $2630 (from initial $3380)

### **Tips & Recommendations:**
- Check for any events or festivals happening on New Year’s Eve in San Jose for extended enjoyment.
- Consider exploring nearby attractions if time allows, such as the Bay 101 or Watson Park.

Enjoy your trip to San Jose!
```
---
## Modules Overview

### 1. **main.py**
The main module that orchestrates the travel planning process. It interacts with external APIs, extracts travel details using OpenAI, finds flight and hotel deals, calculates distances, and generates itineraries.

### 2. **models.py**
Contains the data models used throughout the application, defined using Pydantic. It includes:
- `AccommodationPreferences`
- `TravelQuery`
- `Activity`
- `DailyItinerary`
- `Itinerary`

### 3. **weather.py**
Fetches weather forecast data for specified cities and date ranges using the OpenWeatherMap API. It also provides functionality to filter and display weather information.

## API Integrations

### 1. **OpenAI GPT**
Used to generate detailed itineraries based on user input and the trip plan.

### 2. **Google Maps API**
- **Geocoding**: To convert city names into geographical coordinates.
- **Distance Matrix**: To calculate travel distances and durations between locations.
- **Places API**: To find nearby places of interest for the itinerary.

### 3. **OpenWeatherMap API**
Provides weather forecasts for destinations during the travel dates.

### 4. **Mock APIs for Flights and Hotels**
Uses Postman mock servers to simulate API responses for flight and hotel deals.

## Logging
The application logs detailed information to assist with debugging and tracking application progress. Logs include API responses, budget calculations, and itinerary details.

## Error Handling
- **API Key Missing**: The application checks for missing API keys and exits gracefully if any are missing.
- **API Errors**: Handles errors from external API calls (e.g., request failures, JSON parsing issues).
- **Validation Errors**: Uses Pydantic to validate user inputs and extracted data.

## Usage
The travel planner application is interactive. When run, it will prompt users to input their travel plans in natural language. The system will guide the user step-by-step through the flight, hotel selection, and budget management process, eventually generating a comprehensive itinerary.

## Sample Commands
```bashsh
python main_google_api.py
```
After running the command, provide the desired trip details, and the planner will generate your travel itinerary.



