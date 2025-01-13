from datetime import datetime
from datetime import datetime, timedelta, timezone
import httpx
from agentifyme import task
from loguru import logger
from openai import OpenAI
import os
import json
from utils import fetch_external_url_content, map_weather_code_to_description
MODEL = "gpt-4o-mini"

@task(name="extract-trip-details", description="Extract trip details from a user query using OpenAI.")
def extract_trip_details_task(query: str) -> dict:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant that extracts travel planning details from a user's query. "
                "Extract the destination, number of days, weekend flag, start_date, and end_date if provided. "
                "Return exactly a JSON object like "
                "{'destination': 'Phoenix', 'days': 6, 'weekend': false, 'start_date': '2024-01-20', 'end_date': '2024-01-25'} "
                "without any additional text."
            )
        },
        {"role": "user", "content": f"Extract details from this query: {query}"}
    ]
    try:
        response = client.chat.completions.create(model=MODEL, messages=messages)
        result_text = response.choices[0].message.content.strip()
        details = json.loads(result_text.replace("'", "\""))
        return details
    except Exception as e:
        logger.error(f"Error parsing trip details: {e}")
        return {}


@task(name="get-upcoming-weekend-dates", description="Compute the dates for upcoming Saturday and Sunday.")
async def get_upcoming_weekend_dates() -> list[str]:
    today = datetime.now().date()
    days_until_saturday = (5 - today.weekday()) % 7
    saturday = today + timedelta(days=days_until_saturday)
    sunday = saturday + timedelta(days=1)
    return [saturday.strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d")]

@task(name="get-wikipedia-sections", description="Fetches the list of sections from a Wikipedia page for the given destination.")
async def get_wikipedia_sections(destination: str) -> list[dict]:
    """
    Fetches the list of sections from a Wikipedia page for the given destination.

    :param destination: The name of the destination (e.g., 'Delhi')
    :return: A list of dictionaries, each containing section information.
    """
    try:
        url = "https://en.wikipedia.org/w/api.php"
        params = {"action": "parse", "page": destination, "format": "json", "prop": "sections"}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers={"User-Agent": "travel-planner-app/0.1"})
            response.raise_for_status()
            data = response.json()
            sections = data["parse"]["sections"]
            return sections
    except httpx.RequestError as e:
        logger.error(f"Error fetching Wikipedia sections: {e}")
        return []
    except KeyError:
        logger.error("Unexpected response structure from Wikipedia API when fetching sections.")
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

@task(
    name="get-reddit-posts",
    description="Fetches recent posts from a subreddit related to the destination without authentication. Includes only the post's content (selftext) if available. For link posts, optionally fetches content from the URL. Also retrieves the permalink for each post to fetch comments later.",
)
async def get_reddit_posts(destination: str, subreddit: str = "travel", limit: int = 5) -> tuple[list[dict], dict]:
    """
    Fetches recent posts from a subreddit related to the destination without authentication.
    Includes only the post's content (selftext) if available. For link posts, optionally fetches content from the URL.
    Also retrieves the permalink for each post to fetch comments later.
    """
    try:
        headers = {"User-Agent": "travel-planner-app/0.1"}
        # Using search to find posts related to the destination
        url = f"https://www.reddit.com/r/{subreddit}/search.json"
        params = {
            "q": destination,
            "sort": "new",
            "limit": limit,
            "restrict_sr": True,  # Restrict search to the specified subreddit
        }
        response = httpx.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        posts = data["data"]["children"]
        post_list = []
        for post in posts:
            post_data = post["data"]
            post_info = {"content": post_data.get("selftext", ""), "external_content": "", "permalink": post_data.get("permalink", "")}

            # If the post is a link post (i.e., has no selftext), attempt to fetch external content
            if not post_info["content"] and post_info.get("url"):
                external_content = fetch_external_url_content(post_info["url"])
                post_info["external_content"] = external_content

            post_list.append(post_info)
        return post_list, data  # Return both the post list and raw data
    except httpx.RequestError as e:
        logger.error(f"Error fetching Reddit posts: {e}")
        return [], None
    except Exception as e:
        logger.error(f"Unexpected error fetching Reddit posts: {e}")
        return [], None


@task(name="get-reddit-comments", description="Fetches comments for a given Reddit post using its permalink.")
async def get_reddit_comments(permalink: str, limit: int = 5) -> list[str]:
    """
    Fetches comments for a given Reddit post using its permalink.
    :param permalink: The permalink URL of the Reddit post.
    :param limit: The number of top-level comments to fetch.
    :return: A list of comment texts.
    """
    try:
        headers = {"User-Agent": "travel-planner-app/0.1"}
        # Reddit's API for comments returns a list with two elements; the second contains the comments
        url = f"https://www.reddit.com{permalink}.json"
        params = {
            "limit": limit,  # Limit the number of comments fetched
            "depth": 1,  # Fetch only top-level comments
        }
        response = httpx.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        comments = []
        if len(data) > 1:
            comments_data = data[1]["data"]["children"]
            for comment in comments_data:
                if comment["kind"] == "t1":  # Ensure it's a comment
                    comment_body = comment["data"].get("body", "")
                    if comment_body:
                        comments.append(comment_body)
        return comments
    except httpx.RequestError as e:
        logger.error(f"Error fetching comments from Reddit: {e}")
        return []
    except KeyError:
        logger.error("Unexpected response structure from Reddit API when fetching comments.")
        return []


@task(name="get-geo-coordinates", description="Fetches the geographical coordinates (latitude and longitude) for the given destination using OpenStreetMap's Nominatim API.")
async def get_geo_coordinates(destination: str) -> tuple[float, float]:
    """
    Fetches the geographical coordinates (latitude and longitude) for the given destination using OpenStreetMap's Nominatim API.
    :param destination: The name of the destination (e.g., 'Delhi')
    :return: A tuple of (latitude, longitude) as floats. Returns (None, None) if not found.
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": destination, "format": "json", "limit": 1}
        headers = {"User-Agent": "travel-planner-app/0.1"}
        response = httpx.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon
        else:
            logger.error(f"No geocoding results found for '{destination}'.")
            return None, None
    except httpx.RequestError as e:
        logger.error(f"Error fetching geocoding data: {e}")
        return None, None
    except (KeyError, ValueError) as e:
        logger.error(f"Error processing geocoding data: {e}")
        return None, None


@task(
    name="get-weather-forecast",
    description="Fetches weather forecast data using advanced logic for given coordinates and date range."
)
async def get_weather_forecast(lat: float, lon: float, days: int = 3) -> tuple[str, dict]:
    try:
        today = datetime.now(timezone.utc).date()
        start_date = datetime.combine(today, datetime.min.time())
        end_date = start_date + timedelta(days=days - 1)

        logger.info("Fetching weather forecast data using Forecast API.")
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": "true",
            "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,weathercode",
            "daily": "temperature_2m_max,temperature_2m_min,weathercode",
            "timezone": "auto",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        if "daily" in data and "weathercode" in data["daily"]:
            logger.info("Processing Forecast API data.")
            forecast_info = "Weather Forecast:\n"
            weather_info = {}
            for i in range(len(data["daily"]["time"])):
                date_str = data["daily"]["time"][i]
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                day_of_week = date_obj.strftime("%A")
                temp_max = data["daily"]["temperature_2m_max"][i]
                temp_min = data["daily"]["temperature_2m_min"][i]
                weather_code = data["daily"]["weathercode"][i]
                weather_description = map_weather_code_to_description(weather_code)

                forecast_info += f"- **{day_of_week}, {date_obj.strftime('%B %d')}**:\n"
                forecast_info += f"  - Description: {weather_description}\n"
                forecast_info += f"  - Temperature: {temp_min}°C (Min) / {temp_max}°C (Max)\n\n"
                weather_info[date_str] = {
                    "description": weather_description,
                    "temp_day": temp_max,
                    "temp_night": temp_min
                }
            return forecast_info, weather_info
        else:
            logger.error("Unexpected data structure received from Weather API.")
            return "Weather data is currently unavailable.", None

    except httpx.RequestError as e:
        logger.error(f"Error fetching weather data from Open-Meteo: {e}")
        return "Weather forecast is currently unavailable.", None
    except KeyError as e:
        logger.error(f"Unexpected response structure from Open-Meteo API: {e}")
        return "Weather forecast is currently unavailable.", None