import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from openai import OpenAI  
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key and instantiate the client
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),  
)

# Specify the model to use:
MODEL = "gpt-4o-mini"  # Ensure this is the correct model name

def get_wikipedia_sections(destination):
    """
    Fetches the list of sections from a Wikipedia page for the given destination.
    """
    try:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            'action': 'parse',
            'page': destination,
            'format': 'json',
            'prop': 'sections'
        }
        response = requests.get(url, params=params, headers={'User-Agent': 'travel-planner-app/0.1'})
        response.raise_for_status()
        data = response.json()
        sections = data['parse']['sections']
        return sections
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Wikipedia sections: {e}")
        return []
    except KeyError:
        print("Unexpected response structure from Wikipedia API when fetching sections.")
        return []

def get_wikipedia_info(destination, desired_sections=None):
    """
    Fetches detailed information about the destination from Wikipedia by extracting specified sections.
    :param destination: The name of the destination (e.g., 'Delhi')
    :param desired_sections: A list of section titles to extract. If None, fetches all sections.
    :return: A dictionary with section titles as keys and their extracts as values, along with raw data.
    """
    if desired_sections is None:
        desired_sections = ['Culture', 'Economy', 'Demographics', 'Tourism']

    try:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            'action': 'parse',
            'page': destination,
            'format': 'json',
            'prop': 'text',
            'section': 0  # Fetch the lead section (summary)
        }
        response = requests.get(url, params=params, headers={'User-Agent': 'travel-planner-app/0.1'})
        response.raise_for_status()
        data = response.json()

        # Initialize dictionary to hold section data
        wiki_data = {}

        # Fetch the summary
        if 'parse' in data and 'text' in data['parse']:
            summary = data['parse']['text']['*']
            wiki_data['Summary'] = summary
        else:
            print("No summary available for this destination on Wikipedia.")

        # Fetch each desired section
        for section_title in desired_sections:
            sections = get_wikipedia_sections(destination)
            section_number = None
            for section in sections:
                if section['line'].lower() == section_title.lower():
                    section_number = section['index']
                    break
            if section_number:
                # Fetch the specific section
                section_params = {
                    'action': 'parse',
                    'page': destination,
                    'format': 'json',
                    'prop': 'text',
                    'section': section_number
                }
                section_response = requests.get(url, params=section_params, headers={'User-Agent': 'travel-planner-app/0.1'})
                section_response.raise_for_status()
                section_data = section_response.json()
                if 'parse' in section_data and 'text' in section_data['parse']:
                    section_text = section_data['parse']['text']['*']
                    wiki_data[section_title] = section_text
                else:
                    print(f"No data available for section: {section_title}")
            else:
                print(f"Section '{section_title}' not found in Wikipedia page for {destination}.")

        return wiki_data, data  # Return the detailed wiki data and raw data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Wikipedia data: {e}")
        return None, None
    except KeyError:
        print("Unexpected response structure from Wikipedia API.")
        return None, None

def get_reddit_posts(destination, subreddit='travel', limit=5):
    """
    Fetches recent posts from a subreddit related to the destination without authentication.
    Includes only the post's content (selftext) if available. For link posts, optionally fetches content from the URL.
    Also retrieves the permalink for each post to fetch comments later.
    """
    try:
        headers = {'User-Agent': 'travel-planner-app/0.1'}
        # Using search to find posts related to the destination
        url = f"https://www.reddit.com/r/{subreddit}/search.json"
        params = {
            'q': destination,
            'sort': 'new',
            'limit': limit,
            'restrict_sr': True  # Restrict search to the specified subreddit
        }
        response = requests.get(url, headers=headers, params=params)
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

            # If the post is a link post (i.e., has no selftext), attempt to fetch external content
            if not post_info['content'] and post_data.get('url'):
                external_content = fetch_external_url_content(post_data['url'])
                post_info['external_content'] = external_content

            post_list.append(post_info)
        return post_list, data  # Return both the post list and raw data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Reddit posts: {e}")
        return [], None

def fetch_external_url_content(url):
    """
    Fetches and extracts meaningful content from an external URL.
    """
    try:
        response = requests.get(url, headers={'User-Agent': 'travel-planner-app/0.1'}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract text from <p> tags as a simple method
        paragraphs = soup.find_all('p')
        content = '\n'.join([para.get_text() for para in paragraphs[:5]])  # Limit to first 5 paragraphs
        return content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching external URL content from {url}: {e}")
        return "[Could not retrieve external content]"
    except Exception as e:
        print(f"Error processing external URL content from {url}: {e}")
        return "[Error processing external content]"

def get_reddit_comments(permalink, limit=5):
    """
    Fetches comments for a given Reddit post using its permalink.
    :param permalink: The permalink URL of the Reddit post.
    :param limit: The number of top-level comments to fetch.
    :return: A list of comment texts.
    """
    try:
        headers = {'User-Agent': 'travel-planner-app/0.1'}
        # Reddit's API for comments returns a list with two elements; the second contains the comments
        url = f"https://www.reddit.com{permalink}.json"
        params = {
            'limit': limit,  # Limit the number of comments fetched
            'depth': 1  # Fetch only top-level comments
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        comments = []
        if len(data) > 1:
            comments_data = data[1]['data']['children']
            for comment in comments_data:
                if comment['kind'] == 't1':  # Ensure it's a comment
                    comment_body = comment['data'].get('body', '')
                    if comment_body:
                        comments.append(comment_body)
        return comments
    except requests.exceptions.RequestException as e:
        print(f"Error fetching comments from Reddit: {e}")
        return []
    except KeyError:
        print("Unexpected response structure from Reddit API when fetching comments.")
        return []

def get_geo_coordinates(destination):
    """
    Fetches the geographical coordinates (latitude and longitude) for the given destination using OpenStreetMap's Nominatim API.
    :param destination: The name of the destination (e.g., 'Delhi')
    :return: A tuple of (latitude, longitude) as floats. Returns (None, None) if not found.
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': destination,
            'format': 'json',
            'limit': 1
        }
        headers = {'User-Agent': 'travel-planner-app/0.1'}
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            return lat, lon
        else:
            print(f"No geocoding results found for '{destination}'.")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching geocoding data: {e}")
        return None, None
    except (KeyError, ValueError) as e:
        print(f"Error processing geocoding data: {e}")
        return None, None

def get_weather_forecast(lat, lon, days=3):
    """
    Fetches a weather forecast for the next 'days' days for the given coordinates using Open-Meteo API.
    :param lat: Latitude of the location.
    :param lon: Longitude of the location.
    :param days: Number of days to fetch the forecast for.
    :return: A formatted string containing the weather forecast.
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': lat,
            'longitude': lon,
            'daily': 'temperature_2m_max,temperature_2m_min,weathercode',
            'current_weather': 'true',
            'timezone': 'auto'
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Check if daily data is available
        if 'daily' not in data:
            print("No daily weather data available from Open-Meteo.")
            return "Weather forecast is currently unavailable.", None

        # Process daily forecast data
        forecast_info = f"3-Day Weather Forecast:\n"
        for i in range(min(days, len(data['daily']['time']))):
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

        return forecast_info, data  # Return both the formatted forecast and raw data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data from Open-Meteo: {e}")
        return "Weather forecast is currently unavailable.", None
    except KeyError as e:
        print(f"Unexpected response structure from Open-Meteo API: {e}")
        return "Weather forecast is currently unavailable.", None

def map_weather_code_to_description(code):
    """
    Maps Open-Meteo weather codes to human-readable descriptions.
    Reference: https://open-meteo.com/en/docs#weathercode
    """
    weather_codes = {
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
    return weather_codes.get(code, "Unknown weather condition")

def generate_itinerary(wiki_info, reddit_posts, weather_info, destination):
    """
    Uses OpenAI's Chat Completion API to generate a travel itinerary based on Wikipedia info, Reddit posts, comments, and weather data.
    """
    try:
        prompt = (
            f"Based on the following detailed information from Wikipedia, recent Reddit discussions and comments, and a 3-day weather forecast, "
            f"create a comprehensive 3-day travel itinerary for {destination}.\n\n"
            f"Wikipedia Information:\n"
        )
        for section, content in wiki_info.items():
            prompt += f"--- {section} ---\n"
            # Use BeautifulSoup to parse HTML content to plain text
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text()
            prompt += f"{text}\n\n"

        prompt += f"3-Day Weather Forecast:\n{weather_info}\n\n"
        prompt += "Recent Reddit Discussions and Comments:\n"
        for idx, post in enumerate(reddit_posts, 1):
            # Retrieve content or external_content
            content = post.get('content') or post.get('external_content') or "[No content available]"

            # Truncate content for brevity if necessary
            if len(content) > 200:
                content = content[:197] + "..."

            # Retrieve comments
            comments = post.get('comments', [])
            comments_text = ""
            if comments:
                comments_text = "\n".join([f"   - {comment}" for comment in comments[:3]])  # Limit to first 3 comments

            # Add to prompt
            prompt += f"{idx}. {content}\n"
            if comments_text:
                prompt += f"   Comments:\n{comments_text}\n"
            else:
                prompt += f"   Comments: [No comments available]\n"

        prompt += (
            "\nPlease provide a detailed 3-day itinerary, including activities, places to visit, dining recommendations, "
            "suggestions on what to pack according to the weather, and safety measures based on the Reddit discussions and comments."
        )

        # Create messages for ChatCompletion API using the latest OpenAI client
        messages = [
            {
                "role": "system",
                "content": "You are an assistant that creates detailed and personalized travel itineraries based on provided information."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        # Call OpenAI's ChatCompletion API using the client
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=MODEL,
        )

        # Extract the itinerary from the response
        itinerary = chat_completion.choices[0].message.content.strip()
        return itinerary
    except Exception as e:
        print(f"Error generating itinerary: {e}")
        return None

def main():
    print("===================================")
    print("         Welcome to Travel Planner         ")
    print("===================================\n")

    destination = input("Enter your travel destination: ").strip()
    if not destination:
        print("No destination entered. Exiting.")
        return

    # Fetch Wikipedia Information
    print("\nFetching detailed information from Wikipedia...")
    wiki_info, wiki_raw = get_wikipedia_info(destination)
    if not wiki_info:
        print("Could not retrieve Wikipedia information. Exiting.")
        return
    print("Wikipedia Information Retrieved.\n")

    # Print Wikipedia Response
    print("=== Wikipedia Response ===")
    for section, content in wiki_info.items():
        print(f"--- {section} ---")
        # Convert HTML to plain text
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text()
        print(text)
        print("\n")
    print("==========================\n")

    # Geocoding: Get Latitude and Longitude
    print(f"Fetching geographical coordinates for '{destination}'...")
    lat, lon = get_geo_coordinates(destination)
    if lat is None or lon is None:
        print("Could not retrieve geographical coordinates. Exiting.")
        return
    print(f"Coordinates Retrieved: Latitude = {lat}, Longitude = {lon}\n")

    # Fetch Weather Forecast Information
    print(f"Fetching 3-day weather forecast for '{destination}'...")
    weather_info, weather_raw = get_weather_forecast(lat, lon, days=3)
    if not weather_info:
        weather_info = "Weather forecast is currently unavailable."
    print("Weather Forecast Retrieved.\n")

    # Print Weather Forecast Response
    print("=== Weather Forecast Response ===")
    print(weather_info)
    print("===============================\n")

    # Fetch Reddit Posts
    print(f"Fetching recent Reddit discussions from r/travel related to '{destination}'...")
    reddit_posts, reddit_raw = get_reddit_posts(destination, subreddit='travel', limit=5)
    if not reddit_posts:
        print("Could not retrieve Reddit posts. Proceeding without Reddit data.\n")
    else:
        print(f"Retrieved {len(reddit_posts)} Reddit posts.\n")

    # Fetch Comments for Each Reddit Post
    if reddit_posts:
        print("Fetching comments for each Reddit post...\n")
        for idx, post in enumerate(reddit_posts, 1):
            permalink = post.get('permalink', '')
            if permalink:
                comments = get_reddit_comments(permalink, limit=3)  # Fetch top 3 comments
                post['comments'] = comments
            else:
                post['comments'] = []
        print("Comments Retrieved.\n")

    # Print Reddit Response
    if reddit_posts:
        print("=== Reddit Response ===")
        for idx, post in enumerate(reddit_posts, 1):
            # Retrieve content or external_content
            content = post.get('content') or post.get('external_content') or "[No content available]"

            # Truncate content for brevity if necessary
            if len(content) > 200:
                content = content[:197] + "..."

            # Retrieve comments
            comments = post.get('comments', [])
            comments_text = ""
            if comments:
                comments_text = "\n".join([f"   - {comment}" for comment in comments])

            # Print content and comments
            print(f"{idx}. {content}\n")
            if comments_text:
                print(f"   Comments:\n{comments_text}\n")
            else:
                print(f"   Comments: [No comments available]\n")
        print("========================\n")

    # Generate Itinerary
    print("Generating your travel itinerary using OpenAI...")
    itinerary = generate_itinerary(wiki_info, reddit_posts, weather_info, destination)
    if itinerary:
        print("\n===================================")
        print("       Your 3-Day Travel Itinerary      ")
        print("===================================\n")
        print(itinerary)
    else:
        print("Could not generate itinerary.")

if __name__ == "__main__":
    main()
