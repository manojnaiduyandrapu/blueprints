# models.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class AccommodationPreferences(BaseModel):
    entire_room: Optional[bool] = Field(
        default=None,
        description="Whether the user prefers an entire room."
    )
    pet_friendly: Optional[bool] = Field(
        default=None,
        description="Whether the accommodation should be pet-friendly."
    )

class TravelQuery(BaseModel):
    origin: str = Field(
        ...,
        description="The starting point of the trip."
    )
    destinations: List[str] = Field(
        ...,
        description="A list of destinations to visit during the trip."
    )
    start_date: datetime = Field(
        ...,
        description="The start date of the trip in YYYY-MM-DD format."
    )
    end_date: datetime = Field(
        ...,
        description="The end date of the trip in YYYY-MM-DD format."
    )
    budget: Optional[float] = Field(
        default=None,
        description="Total budget for the trip in USD."
    )
    transportation_mode: Optional[str] = Field(
        default=None,
        description="Mode of transportation for the trip (e.g., driving, transit)."
    )
    accommodation_preferences: Optional[AccommodationPreferences] = Field(
        default=None,
        description="User's accommodation preferences."
    )
    # Optional: Add distance and duration if you want to store them
    distance: Optional[str] = Field(
        default=None,
        description="Distance between origin and destination."
    )
    duration: Optional[str] = Field(
        default=None,
        description="Duration between origin and destination."
    )

class Activity(BaseModel):
    time: str = Field(
        ...,
        description="Scheduled time for the activity."
    )
    description: str = Field(
        ...,
        description="Description of the activity."
    )
    location: Optional[str] = Field(
        None,
        description="Location of the activity."
    )
    distance_from_previous: Optional[str] = Field(
        None,
        description="Distance from the previous activity."
    )
    duration_from_previous: Optional[str] = Field(
        None,
        description="Duration from the previous activity."
    )

class DailyItinerary(BaseModel):
    date: str = Field(
        ...,
        description="Date of the day's itinerary."
    )
    activities: List[Activity] = Field(
        ...,
        description="List of activities for the day."
    )

class Itinerary(BaseModel):
    leg: str = Field(
        ...,
        description="Description of the trip leg (e.g., New York to Los Angeles)."
    )
    distance: str = Field(
        ...,
        description="Distance of the trip leg."
    )
    flight_duration: str = Field(
        ...,
        description="Duration of the flight."
    )
    accommodation: str = Field(
        ...,
        description="Accommodation details."
    )
    total_accommodation_cost: float = Field(
        ...,
        description="Total cost of accommodation for the leg."
    )
    remaining_budget: float = Field(
        ...,
        description="Remaining budget after accommodation and flights."
    )
    daily_itineraries: List[DailyItinerary] = Field(
        ...,
        description="List of daily itineraries."
    )
    total_estimated_cost: float = Field(
        ...,
        description="Total estimated cost of the trip."
    )
    remaining_budget_final: float = Field(
        ...,
        description="Remaining budget after all expenses."
    )
