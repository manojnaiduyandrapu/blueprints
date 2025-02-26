import json
from travel_document import TripItinerary

wikipedia_tool = {
    "type": "function",
    "function": {
        "name": "search_wikipedia",
        "description": "Fetch Wikipedia content for a given query.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The Wikipedia search term"}
            },
            "required": ["query"]
        }
    }
}

flight_tool = {
    "type": "function",
    "function": {
        "name": "fetch_flight_results",
        "description": (
            "Fetch flight results from SerpAPI using the provided details. "
            "For flight queries, extract origin/destination IATA codes and outbound/return dates."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "departure_id": {"type": "string", "description": "IATA code for origin airport"},
                "arrival_id": {"type": "string", "description": "IATA code for destination airport"},
                "outbound_date": {"type": "string", "description": "Outbound flight date (YYYY-MM-DD)"},
                "return_date": {"type": "string", "description": "Return flight date (YYYY-MM-DD)"}
            },
            "required": ["departure_id", "arrival_id", "outbound_date", "return_date"]
        }
    }
}

hotels_tool = {
    "type": "function",
    "function": {
        "name": "fetch_hotels",
        "description": (
            "Fetch hotel results from SerpAPI based on destination, check-in, and check-out dates, "
            "and number of adults/children."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "destination": {"type": "string", "description": "Destination city or location"},
                "check_in_date": {"type": "string", "description": "Check-in date (YYYY-MM-DD)"},
                "check_out_date": {"type": "string", "description": "Check-out date (YYYY-MM-DD)"},
                "adults": {"type": "integer", "description": "Number of adults"},
                "children": {"type": "integer", "description": "Number of children"}
            },
            "required": ["destination", "check_in_date", "check_out_date"]
        }
    }
}

weather_tool = {
    "type": "function",
    "function": {
        "name": "fetch_weather",
        "description": "Fetches weather forecast or historical weather data for a given destination and date range.",
        "parameters": {
            "type": "object",
            "properties": {
                "destination": {"type": "string", "description": "Destination city or address"},
                "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                "fallback": {"type": "string", "description": "Fallback city name if geocoding fails", "default": ""}
            },
            "required": ["destination", "start_date", "end_date"]
        }
    }
}

nearby_places_tool = {
    "type": "function",
    "function": {
        "name": "find_nearby_places",
        "description": "Finds nearby places of a specific type within a given radius around a location.",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number", "description": "Latitude of the location"},
                "longitude": {"type": "number", "description": "Longitude of the location"},
                "radius": {"type": "integer", "description": "Search radius in meters"},
                "place_type": {"type": "string", "description": "Type of place (e.g., tourist_attraction, restaurant)", "default": "tourist_attraction"}
            },
            "required": ["latitude", "longitude"]
        }
    }
}

current_date_tool = {
    "type": "function",
    "function": {
        "name": "get_current_date",
        "description": "Returns the current date in YYYY-MM-DD format.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

distance_duration_tool = {
    "type": "function",
    "function": {
        "name": "get_distance_duration",
        "description": "Fetches the distance and travel duration between two locations using the Google Distance Matrix API. Mode can be driving, walking, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "origin": {"type": "string", "description": "Starting location (address, city, or place name)"},
                "destination": {"type": "string", "description": "Destination location (address, city, or place name)"},
                "mode": {"type": "string", "description": "Mode of travel (e.g., driving, walking, bicycling). Default is driving.", "default": "driving"}
            },
            "required": ["origin", "destination"]
        }
    }
}

reddit_posts_tool = {
    "type": "function",
    "function": {
        "name": "get_reddit_posts",
        "description": "Fetches recent Reddit posts related to a given destination from a specified subreddit, including external content and top comments.",
        "parameters": {
            "type": "object",
            "properties": {
                "destination": {"type": "string", "description": "Destination or query for Reddit posts."},
                "subreddit": {"type": "string", "description": "Subreddit to search in. Default is 'travel'."},
                "limit": {"type": "integer", "description": "Number of posts to fetch. Default is 5."}
            },
            "required": ["destination"]
        }
    }
}

schema = TripItinerary.schema_json(indent=2)
