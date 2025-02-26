import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv
import openai
import googlemaps
from loguru import logger
from agentifyme import workflow  # Assumes you have a workflow decorator available

# Import functions and tool registrations
from functions import (
    get_current_date,
    search_wikipedia,
    get_flight_deals,
    format_flight_deals,
    get_hotel_deals,
    format_hotel_deals,
    fetch_weather,
    get_distance_duration,
    find_nearby_places,
    format_nearby_places,
    get_reddit_posts,
)
from tool_registrations import (
    wikipedia_tool,
    flight_tool,
    hotels_tool,
    weather_tool,
    nearby_places_tool,
    current_date_tool,
    distance_duration_tool,
    reddit_posts_tool,
    schema,
)

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')
if not SERPAPI_API_KEY:
    raise ValueError("SERPAPI_API_KEY environment variable is not set.")

GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_MAPS_API_KEY:
    raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set.")


# ---------------------------
# Workflow: Interactive Assistant Chat
# ---------------------------
@workflow(name="Interactive_Travel_Assistant", 
          description="Initializes the assistant and enters an interactive chat loop that handles tool calls and returns the assistant messages as a string.")
def interactive_travel_assistant() -> str:
    """
    Interactive assistant workflow that initializes the assistant and enters an interactive chat loop.

    Args:
        None

    Returns:
        str: A single string containing the  assistant message.
    """
    # Initialize clients
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

    # ---------------------------
    # Assistant and Thread Creation
    # ---------------------------
    assistant = client.beta.assistants.create(
    name="Assistant",
    instructions=(
        "You are a helpful assistant. For factual queries, use the Wikipedia tool. "
        "For flight queries, extract the origin and destination IATA codes and travel dates, and use the flight tool. "
        "When handling flights within itinerary planning, use the extracted IATA codes for the flight tool; "
        "however, before making geocoding or weather queries, convert these IATA codes to full city names (e.g., 'BOS' becomes 'Boston, MA', 'PHX' becomes 'Phoenix, AZ').\n\n"
        "For hotel queries, extract the destination and check-in/out dates, and use the hotels tool. "
        "For weather queries, extract the destination and date range. If no date is provided, **immediately call the get_current_date tool** to retrieve today's date and then use the weather tool. "
        "For attraction queries, extract location details and use the nearby places tool. "
        "For distance queries, extract the origin and destination and use the distance tool. "
        "For travel-related Reddit posts, extract the destination and subreddit, and use the Reddit posts tool. "
        "Always use the current date tool to fetch today's date and stay up-to-date. "
        "Be interactive, engaging, and behave like a human while responding.\n\n"
        "***Important for Itinerary Planning:***\n"
        "When planning an itinerary, perform the following steps one by one:\n"
        "  1. **Flights:** Extract the origin and destination IATA codes from the user input and use these for flight queries. Then, convert them to full city names before performing geocoding or weather queries. "
        "      - If both an outbound date and a return date are provided, fetch both outbound and inbound flights using these dates.\n"
        "      - If the flight tool call returns no results or an empty response, recall the flight tool with the same parameters until valid flight data is obtained.\n"
        "      - If only one travel date is provided, treat it as a one-way flight request and fetch only outbound flights.\n\n"
        "  2. **Hotels:** Use the destination (converted from its IATA code to a full city name) to fetch hotel options for the specified check-in and check-out dates. "
        "      - If the hotels tool returns no results or an empty response, recall it with the same parameters until valid hotel data is obtained.\n\n"
        "  3. **Weather:** Convert the destination IATA code to a full city name and use that for geocoding and weather queries. "
        "      - If no date is provided, **immediately call the get_current_date tool** to retrieve today's date and then use the weather tool. "
        "      - If the weather tool fails or returns empty data, include a default message (e.g., 'Weather data is currently unavailable.').\n\n"
        "  4. **Nearby Attractions & Restaurants:** Use the full city name to obtain geocoordinates, keep the radius default to 100000, then fetch and format the following:\n"
        "      - **Attractions:** Call the nearby places tool to fetch the top 10 attractions (based on rating or relevance).\n"
        "      - **Additional Attractions:** If more attractions are available, include these as 'remaining attractions'.\n"
        "      - **Restaurants:** Call the nearby places tool again specifically to fetch restaurant recommendations for breakfast, lunch, and dinner.\n\n"
        "  5. **Reddit Travel Tips:** Use the full city name to fetch relevant travel posts and safety tips from Reddit. "
        "      - If the Reddit posts tool returns no results, recall it with the same parameters until valid posts are obtained.\n\n"
        "  6. **Final Output:** Assemble the gathered data (flights, hotels, weather, attractions, restaurants, and Reddit travel tips) into a complete travel itinerary that exactly matches the following JSON schema:\n\n"
        f"{schema}\n\n"
        "      - Return a pure JSON string (without any markdown code fences or extra text) that exactly matches this schema.\n"
        "  7. Fill in the actual values for each field in the schema properly and do not hallucinate.\n"
        "  8. If any tool call returns no results or an empty response, recall that tool with the same parameters until a valid response is obtained.\n\n"
        "Use the above steps to handle all travel planning and itinerary requests."
    ),
    model="gpt-4o-mini",
    tools=[
        wikipedia_tool,
        flight_tool,
        hotels_tool,
        weather_tool,
        nearby_places_tool,
        current_date_tool,
        distance_duration_tool,
        reddit_posts_tool
    ]
)

    logger.info(f"Assistant created: {assistant.name} (ID: {assistant.id})")

    thread = client.beta.threads.create()
    logger.info(f"Thread created with ID: {thread.id}")

    # ---------------------------
    # Chat Loop with Tool Handling
    # ---------------------------
    print("\n💬 **Interactive Assistant Chat** (Type 'exit' to quit)")
    print("--------------------------------------------------------")

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            print("👋 Exiting chat. Goodbye!")
            break

        # Send user's message to the assistant.
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )

        print("🤖 Thinking...")
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        # Poll for run status and check for tool calls.
        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            logger.debug(f"Run status: {run_status.status}")
            if hasattr(run_status, "required_action") and run_status.required_action is not None:
                try:
                    required_action = run_status.required_action.dict()
                except Exception:
                    required_action = run_status.required_action
                logger.debug(f"Required action: {required_action}")
                if "submit_tool_outputs" in required_action:
                    tool_calls = required_action["submit_tool_outputs"].get("tool_calls", [])
                    if tool_calls:
                        tool_call = tool_calls[0]
                        logger.debug(f"Tool call detected: {tool_call}")
                        function_name = tool_call["function"]["name"]

                        # Cancel active run to send tool output.
                        client.beta.threads.runs.cancel(thread_id=thread.id, run_id=run.id)
                        logger.debug(f"Canceled run {run.id} to send tool output.")

                        if function_name == "search_wikipedia":
                            args = json.loads(tool_call["function"]["arguments"])
                            query = args["query"]
                            logger.info(f"Wikipedia tool call for query: {query}")
                            wiki_result = search_wikipedia(query)
                            client.beta.threads.messages.create(
                                thread_id=thread.id,
                                role="assistant",
                                content=(
                                    f"📚 Wikipedia Search Result:\n"
                                    f"Title: {wiki_result['title']}\n"
                                    f"Content: {wiki_result['content']}\n"
                                    f"URL: {wiki_result['url']}"
                                )
                            )
                        elif function_name == "fetch_flight_results":
                            args = json.loads(tool_call["function"]["arguments"])
                            logger.info(f"Flight tool call with arguments: {args}")
                            origin_iata = args.get("departure_id") or args.get("origin")
                            destination_iata = args.get("arrival_id") or args.get("destination")
                            try:
                                start_date = datetime.strptime(args["outbound_date"], '%Y-%m-%d')
                            except Exception as e:
                                logger.error("Date parsing error for outbound_date: " + str(e))
                                start_date = datetime.now()
                            if args["return_date"]:
                                try:
                                    end_date = datetime.strptime(args["return_date"], '%Y-%m-%d')
                                except Exception as e:
                                    logger.error("Date parsing error for return_date: " + str(e))
                                    end_date = start_date
                            else:
                                end_date = None
                            flight_deals = get_flight_deals(
                                origin_iata=args["departure_id"],
                                destination_iata=args["arrival_id"],
                                start_date=start_date,
                                end_date=end_date
                            )
                            if not flight_deals.get("outbound"):
                                logger.warning("No outbound flight details extracted for the provided parameters.")
                            formatted_result = format_flight_deals(
                                flight_deals,
                                origin=args["departure_id"],
                                destination=args["arrival_id"],
                                outbound_date=args["outbound_date"],
                                return_date=args["return_date"] if args["return_date"] else args["outbound_date"]
                            )
                            client.beta.threads.messages.create(
                                thread_id=thread.id,
                                role="assistant",
                                content=formatted_result
                            )
                        elif function_name == "fetch_hotels":
                            args = json.loads(tool_call["function"]["arguments"])
                            logger.info(f"HOTELS tool call with arguments: {args}")
                            destination = args["destination"]
                            check_in_date = args["check_in_date"]
                            check_out_date = args["check_out_date"]
                            hotels_result = get_hotel_deals(
                                destination,
                                datetime.strptime(check_in_date, '%Y-%m-%d'),
                                datetime.strptime(check_out_date, '%Y-%m-%d')
                            )
                            formatted_hotels = format_hotel_deals(
                                hotels_result,
                                destination=destination,
                                check_in_date=check_in_date,
                                check_out_date=check_out_date
                            )
                            client.beta.threads.messages.create(
                                thread_id=thread.id,
                                role="assistant",
                                content=formatted_hotels
                            )
                        elif function_name == "fetch_weather":
                            args = json.loads(tool_call["function"]["arguments"])
                            logger.info(f"Weather tool call with arguments: {args}")
                            destination = args["destination"]
                            start_date_str = args["start_date"]
                            end_date_str = args["end_date"]
                            fallback = args.get("fallback", "")
                            weather_result = fetch_weather(destination, start_date_str, end_date_str, fallback)
                            client.beta.threads.messages.create(
                                thread_id=thread.id,
                                role="assistant",
                                content=f"🌤 Weather Report:\n{weather_result}"
                            )
                        elif function_name == "find_nearby_places":
                            args = json.loads(tool_call["function"]["arguments"])
                            logger.info(f"Nearby places tool call with arguments: {args}")
                            try:
                                latitude = float(args["latitude"])
                                longitude = float(args["longitude"])
                            except Exception as e:
                                logger.error("Error parsing latitude/longitude: " + str(e))
                                latitude, longitude = 0.0, 0.0
                            radius = int(args.get("radius", 100000))
                            place_type = args.get("place_type", "tourist_attraction")
                            places = find_nearby_places(latitude, longitude, radius, place_type)
                            formatted_places = format_nearby_places(places)
                            client.beta.threads.messages.create(
                                thread_id=thread.id,
                                role="assistant",
                                content=formatted_places
                            )
                        elif function_name == "get_current_date":
                            logger.info("Current date tool call.")
                            current_date = get_current_date()
                            client.beta.threads.messages.create(
                                thread_id=thread.id,
                                role="assistant",
                                content=f"Today's date is: {current_date}"
                            )
                        elif function_name == "get_distance_duration":
                            args = json.loads(tool_call["function"]["arguments"])
                            origin = args["origin"]
                            destination = args["destination"]
                            mode = args.get("mode", "driving")
                            distance_result = get_distance_duration(origin, destination, mode)
                            if distance_result:
                                formatted_distance = (
                                    f"Distance from {origin} to {destination}:\n"
                                    f"- **Distance:** {distance_result['distance_text']}\n"
                                    f"- **Duration:** {distance_result['duration_text']}"
                                )
                            else:
                                formatted_distance = "Unable to retrieve distance information at this time."
                            client.beta.threads.messages.create(
                                thread_id=thread.id,
                                role="assistant",
                                content=formatted_distance
                            )
                        elif function_name == "get_reddit_posts":
                            args = json.loads(tool_call["function"]["arguments"])
                            destination = args["destination"]
                            subreddit = args.get("subreddit", "travel")
                            limit = int(args.get("limit", 5))
                            reddit_posts, _ = get_reddit_posts(destination, subreddit, limit)
                            formatted_posts = f"Reddit posts related to '{destination}':\n"
                            for idx, post in enumerate(reddit_posts, 1):
                                formatted_posts += f"{idx}. Content: {post['content'] or 'No text content'}\n"
                                if post.get('external_content'):
                                    formatted_posts += f"   External Content: {post['external_content']}\n"
                                if post.get('comments'):
                                    formatted_posts += f"   Top Comments: {' | '.join(post['comments'])}\n"
                            client.beta.threads.messages.create(
                                thread_id=thread.id,
                                role="assistant",
                                content=formatted_posts
                            )
                        run = client.beta.threads.runs.create(
                            thread_id=thread.id,
                            assistant_id=assistant.id
                        )
            if run_status.status == "completed":
                break
            time.sleep(1)

        # After each run, collect assistant messages.
        final_messages = []
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        for msg in messages.data:
            if msg.role == "assistant":
                for content in msg.content:
                    if content.type == "text":
                        text = content.text.value.strip()
                        # Optionally, filter out raw tool outputs if necessary.
                        if text and not (text.startswith("📚 Wikipedia Search Result:") or 
                                         text.startswith("Hotel") or 
                                         text.startswith("🌤 Weather Report:") or 
                                         text.startswith("Today's date is:")):
                            final_messages.append(text)
        # Join final messages into a single string.
        final_output = "\n\n".join(final_messages)
        print(f"\n🤖 Final Assistant Output:\n{final_output}")
    return final_output

if __name__ == '__main__':
    results = interactive_travel_assistant()

