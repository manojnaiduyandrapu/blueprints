from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class Activity(BaseModel):
    name: str = Field(..., description="A short title describing the activity, e.g., 'Visit museum'.")
    fare: Optional[float] = Field(None, description="Ticket price or entrance fee associated with the activity.")
    distance_km: Optional[float] = Field(None, description="Approximate distance in kilometers from the hotel or previous location.")
    duration_minutes: Optional[int] = Field(None, description="Estimated time (in minutes) to complete this activity or travel.")
    transport_mode: Optional[str] = Field(None, description="Mode of transport (e.g., 'walking', 'driving').")

class DayWeather(BaseModel):
    description: Optional[str] = Field(None, description="Short weather description (e.g., 'Sunny', 'Partly Cloudy').")
    temperature_high: Optional[float] = Field(None, description="Expected high temperature for the day.")
    temperature_low: Optional[float] = Field(None, description="Expected low temperature for the day.")

class Flight(BaseModel):
    departure_time: str = Field(..., description="Scheduled departure time (local).")
    arrival_time: str = Field(..., description="Scheduled arrival time (local).")
    flight_number: str = Field(..., description="Flight identifier (e.g., 'AA123').")
    aircraft: str = Field(..., description="Aircraft type (e.g., 'Boeing 737').")
    price: float = Field(..., description="Cost of the flight ticket.")
    duration_minutes: int = Field(..., description="Approximate flight duration in minutes.")

class FlightDetails(BaseModel):
    outbound: Flight = Field(..., description="Flight details for the outbound journey.")
    inbound: Flight = Field(..., description="Flight details for the return journey.")

class EstimatedCosts(BaseModel):
    hotel: float = Field(..., description="Daily hotel cost.")
    lunch: Optional[float] = Field(0.0, description="Estimated daily lunch cost.")
    dinner: Optional[float] = Field(0.0, description="Estimated daily dinner cost.")
    total_day_expense: float = Field(..., description="Total expense for the day, including hotel, meals, and activities.")

class DaySchedule(BaseModel):
    day: int = Field(..., description="Ordinal index for the day of the trip.")
    day_date: date = Field(..., description="Calendar date for this day.")
    weather: Optional[DayWeather] = Field(None, description="Weather forecast or conditions for this day.")
    breakfast: str = Field(..., description="Breakfast details or location with costs if available.")
    morning_activities: List[Activity] = Field(..., description="List of planned activities for the morning with costs if available.")
    lunch: str = Field(..., description="Lunch details or location with costs if available.")
    afternoon_activities: List[Activity] = Field(..., description="List of planned activities for the afternoon with costs if available.")
    evening_activities: List[Activity] = Field(..., description="List of planned activities for the evening with costs if available.")
    dinner: str = Field("Dinner not specified", description="Dinner details or location with costs if available.")
    estimated_costs: EstimatedCosts = Field(..., description="Breakdown of the day's estimated costs.")

class SummaryCosts(BaseModel):
    hotel_stay: float = Field(..., description="Total cost for all hotel nights.")
    flight_costs: float = Field(..., description="Total cost for all flights.")
    total_daily_expenses: float = Field(..., description="Sum of daily activity/meal expenses across all days.")
    total_trip_costs: float = Field(..., description="Grand total of flights, hotel, and daily expenses.")
    remaining_budget: float = Field(..., description="Budget left after accounting for all estimated costs.")

class TripItinerary(BaseModel):
    origin: str = Field(..., description="Starting city.")
    destination: str = Field(..., description="Destination city.")
    start_date: date = Field(..., description="Trip start date.")
    end_date: date = Field(..., description="Trip end date.")
    hotel_name: str = Field(..., description="Name of the hotel where the traveler will stay.")
    check_in_time: str = Field(..., description="Hotel check-in time (e.g., '3:00 PM').")
    check_out_time: str = Field(..., description="Hotel check-out time (e.g., '12:00 PM').")
    hotel_price_per_night: float = Field(..., description="Nightly rate for the chosen hotel.")
    total_daily_expense_budget: float = Field(..., description="Maximum allotted daily expenses for meals and activities.")
    flight_details: FlightDetails = Field(..., description="Outbound and inbound flight information.")
    days: List[DaySchedule] = Field(..., description="List of day-by-day schedules.")
    summary_costs: SummaryCosts = Field(..., description="Calculated summary of the trip's total costs.")
    what_to_pack: List[str] = Field(..., description="Suggestions or requirements for items to pack depending on the weather conditions.")
    safety_measures: List[str] = Field(..., description="Safety or precaution tips for the traveler.")
