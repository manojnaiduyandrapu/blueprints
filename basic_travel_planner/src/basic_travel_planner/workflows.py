import asyncio
import os
import nest_asyncio
nest_asyncio.apply()
from datetime import datetime, timedelta
from agentifyme import workflow
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from loguru import logger
from openai import OpenAI
from tasks import (
    extract_trip_details_task,
    get_geo_coordinates,
    get_reddit_comments,
    get_reddit_posts,
    get_upcoming_weekend_dates,
    get_weather_forecast,
    get_wikipedia_info,
)
load_dotenv()

MODEL = "gpt-4o-mini"

def generate_itinerary(wiki_info, reddit_posts, weather_info, destination, days):
    try:
        prompt = (
            f"Based on the following detailed information from Wikipedia, recent Reddit discussions and comments, "
            f"and a weather forecast, create a comprehensive {days}-day travel itinerary for {destination}."
        )
        for section, content in wiki_info.items():
            prompt += f"--- {section} ---\n"
            soup = BeautifulSoup(content, "html.parser")
            text = soup.get_text()
            prompt += f"{text}\n\n"

        prompt += f"3-Day Weather Forecast:\n{weather_info}\n\n"
        prompt += "Recent Reddit Discussions and Comments:\n"
        for idx, post in enumerate(reddit_posts, 1):
            content = post.get("content") or post.get("external_content") or "[No content available]"
            if len(content) > 200:
                content = content[:197] + "..."
            comments = post.get("comments", [])
            comments_text = ""
            if comments:
                comments_text = "\n".join([f"   - {comment}" for comment in comments[:3]])
            prompt += f"{idx}. {content}\n"
            if comments_text:
                prompt += f"   Comments:\n{comments_text}\n"
            else:
                prompt += f"   Comments: [No comments available]\n"

        prompt += (
            "\nPlease provide a detailed itinerary, including activities, places to visit, dining recommendations, weather forecast for each day"
            "suggestions on what to pack according to the weather, and safety measures based on the Reddit discussions and comments."
        )

        messages = [
            {"role": "system", "content": "You are an assistant that creates detailed and personalized travel itineraries based on provided information."},
            {"role": "user", "content": prompt},
        ]

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )

        itinerary = response.choices[0].message.content.strip()
        return itinerary
    except Exception as e:
        logger.error(f"Error generating itinerary: {e}")
        return None

@workflow(name="generate-travel-plan-from-query", description="Generate a travel plan based on a natural language query")
async def generate_travel_plan_from_query(query: str) -> dict:
    logger.info(f"Processing query: {query}")
    
    details = extract_trip_details_task(query)
    if not details:
        logger.error("Failed to extract trip details.")
        return {}
    
    destination = details.get("destination")
    days = details.get("days") or 3
    weekend = details.get("weekend", False)
    start_date_str = details.get("start_date")
    end_date_str = details.get("end_date")
    
    if weekend and not start_date_str and not end_date_str:
        weekend_dates = get_upcoming_weekend_dates()
        start_date_str, end_date_str = weekend_dates[0], weekend_dates[-1]
    
    if start_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    else:
        start_date = datetime.now()
    if end_date_str:
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    else:
        end_date = start_date + timedelta(days=days-1)
    
    logger.info(f"Extracted details: destination={destination}, days={days}, weekend={weekend}, start_date={start_date}, end_date={end_date}")
    
    wiki_info, _ = get_wikipedia_info(destination)
    if not wiki_info:
        logger.error("Could not retrieve Wikipedia information.")
        return {}
    
    lat, lon = get_geo_coordinates(destination)
    if not lat or not lon:
        logger.error("Could not retrieve geographical coordinates.")
        return {}
    
    weather_info, _ = get_weather_forecast(lat, lon, days)
    
    reddit_posts, _ = get_reddit_posts(destination, subreddit="travel", limit=5)
    if reddit_posts:
        for idx, post in enumerate(reddit_posts, 1):
            permalink = post.get("permalink", "")
            if permalink:
                comments = get_reddit_comments(permalink, limit=3)
                post["comments"] = comments
            else:
                post["comments"] = []
    
    itinerary = generate_itinerary(wiki_info, reddit_posts, weather_info, destination, days)
    if not itinerary:
        logger.error("Itinerary generation failed.")
        return {}
    
    return {
        "destination": destination,
        "days": days,
        "itinerary": itinerary,
    }

def main():
    result = asyncio.run(generate_travel_plan_from_query("Plan a weekend trip to los angeles"))
    if result and "itinerary" in result:
        print(result["itinerary"])
    else:
        print("No itinerary generated.")

if __name__ == "__main__":
    main()