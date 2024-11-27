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
    accommodation_preferences: Optional[AccommodationPreferences] = Field(
        default=None,
        description="User's accommodation preferences."
    )
