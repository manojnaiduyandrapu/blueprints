import requests
from bs4 import BeautifulSoup
import logging
import json
from typing import Type, Union, get_args, get_origin
from pydantic import BaseModel

def fetch_external_url_content(url: str) -> str:
    try:
        response = requests.get(url, headers={'User-Agent': 'travel-planner-app/0.1'}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        content = '\n'.join([para.get_text() for para in paragraphs[:5]])
        return content
    except Exception as e:
        logging.error(f"Error fetching external content from {url}: {e}")
        return ""

def map_weather_code_to_description(code: int) -> str:
    weather_codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
        55: "Dense drizzle", 56: "Light freezing drizzle", 57: "Dense freezing drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        66: "Light freezing rain", 67: "Heavy freezing rain", 71: "Slight snow fall",
        73: "Moderate snow fall", 75: "Heavy snow fall", 77: "Snow grains",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        85: "Slight snow showers", 86: "Heavy snow showers", 95: "Thunderstorm",
        96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
    }
    return weather_codes.get(code, "Unknown weather condition")

def get_python_type_name(t):
    type_map = {str: "string", int: "integer", float: "number", bool: "boolean"}
    return type_map.get(t, "string")  # default to string for unknown types


def get_field_schema_for_primitive(annotation, description):
    return {"type": get_python_type_name(annotation), "description": description}


def get_field_schema_for_list(annotation, description):
    args = get_args(annotation)
    item_type = args[0] if args else str
    if isinstance(item_type, type) and issubclass(item_type, BaseModel):
        items_schema = generate_model_schema(item_type)
    else:
        items_schema = {"type": get_python_type_name(item_type)}

    return {
        "type": "array",
        "items": items_schema,
        "description": description,
    }


def get_field_schema(field_info):
    origin = get_origin(field_info.annotation)

    if origin is Union:
        args = get_args(field_info.annotation)
        if len(args) == 2 and type(None) in args:
            non_none_type = next(arg for arg in args if arg is not type(None))
            schema = get_field_schema_for_type(non_none_type, field_info.description)
            schema["nullable"] = True
            return schema

    return get_field_schema_for_type(field_info.annotation, field_info.description)


def get_field_schema_for_type(annotation, description):
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return generate_model_schema(annotation)
    elif get_origin(annotation) is list:
        return get_field_schema_for_list(annotation, description)
    else:
        return get_field_schema_for_primitive(annotation, description)


def generate_model_schema(model: Type[BaseModel]):
    properties = {}
    for field_name, field_info in model.model_fields.items():
        if field_name != "id":  # Skip the id field as it's auto-generated
            properties[field_name] = get_field_schema(field_info)

    return {
        "type": "object",
        "properties": properties,
    }


def generate_json_schema(model: Type[BaseModel]) -> str:
    schema = generate_model_schema(model)
    return json.dumps(schema, indent=2)
