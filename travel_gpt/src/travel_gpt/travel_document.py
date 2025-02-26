from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class Overview(BaseModel):
    trip_duration: str = Field(..., description="Total duration of the trip (e.g., '4 days').")
    itinerary_focus: str = Field(
        ..., description="The main focus or theme of the trip (e.g., 'Urban exploration, historical landmarks, culinary experiences, and leisure activities')."
    )
    travel_route: str = Field(
        ..., description="The travel route (e.g., 'Depart from New York (JFK, LaGuardia, or Newark) to Boston Logan International Airport')."
    )

class Flight(BaseModel):
    departure_time: str = Field(..., description="Local departure time (e.g., '2025-02-24T07:00:00').")
    arrival_time: str = Field(..., description="Local arrival time (e.g., '2025-02-24T08:30:00').")
    flight_number: str = Field(..., description="Flight number (e.g., 'AA123').")
    airline: str = Field(..., description="Airline name (e.g., 'American Airlines').")
    aircraft: str = Field(..., description="Type of aircraft (e.g., 'Boeing 737').")
    price: float = Field(..., description="Ticket price in USD.")
    duration_minutes: int = Field(..., description="Flight duration in minutes.")

class FlightDetails(BaseModel):
    outbound: Flight = Field(..., description="Details of the outbound flight.")
    inbound: Flight = Field(..., description="Details of the return flight.")

class Hotel(BaseModel):
    name: str = Field(..., description="Hotel name.")
    location: str = Field(..., description="Hotel location or address.")
    check_in_time: str = Field(..., description="Hotel check-in time (e.g., '3:00 PM').")
    check_out_time: str = Field(..., description="Hotel check-out time (e.g., '11:00 AM').")
    price_per_night: float = Field(..., description="Price per night in USD.")
    amenities: List[str] = Field(..., description="Key hotel amenities (e.g., 'Free Wi-Fi, Breakfast included, Gym').")

class Restaurant(BaseModel):
    name: str = Field(..., description="Name of the restaurant.")
    address: str = Field(..., description="Address of the restaurant.")

class DailyItinerary(BaseModel):
    day: int = Field(..., description="Day number of the trip (e.g., 1 for the first day).")
    day_date: date = Field(..., description="The calendar date for the day (YYYY-MM-DD).")
    breakfast_restaurant: Optional[Restaurant] = Field(None, description="Details of the breakfast restaurant (if applicable).")
    morning_activities: List[str] = Field(..., description="Activities planned for the morning.")
    lunch_restaurant: Optional[Restaurant] = Field(None, description="Details of the lunch restaurant (if applicable).")
    afternoon_activities: List[str] = Field(..., description="Activities planned for the afternoon.")
    dinner_restaurant: Optional[Restaurant] = Field(None, description="Details of the dinner restaurant (if applicable).")
    evening_activities: List[str] = Field(..., description="Activities planned for the evening.")

class TripItinerary(BaseModel):
    overview: Overview = Field(..., description="A brief overview of the trip.")
    flights: FlightDetails = Field(..., description="Outbound and inbound flight information.")
    hotel: Hotel = Field(..., description="Hotel details and key amenities.")
    daily_schedule: List[DailyItinerary] = Field(..., description="A detailed, day-by-day itinerary.")
    packing_list: List[str] = Field(..., description="A list of suggested items to pack.")
    safety_measures: List[str] = Field(..., description="Important safety and health precautions.")
