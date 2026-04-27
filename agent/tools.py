from langchain_core.tools import tool
from pydantic import BaseModel, Field

class SearchPropertiesInput(BaseModel):
    location: str = Field(description="The city or location where the guest wants to stay (e.g., Cox's Bazar).")
    check_in: str = Field(description="Check-in date in YYYY-MM-DD format.")
    check_out: str = Field(description="Check-out date in YYYY-MM-DD format.")
    guests: int = Field(description="Number of guests.")

@tool("search_available_properties", args_schema=SearchPropertiesInput)
def search_available_properties(location: str, check_in: str, check_out: str, guests: int) -> list[dict]:
    """Search for available properties in a given location for specific dates and guest count."""
    # Skeleton implementation
    return [{"id": 1, "name": "Sea View Suite", "price_per_night": 5000}]


class GetListingDetailsInput(BaseModel):
    listing_id: int = Field(description="The unique ID of the property listing.")

@tool("get_listing_details", args_schema=GetListingDetailsInput)
def get_listing_details(listing_id: int) -> dict:
    """Retrieve detailed information and description for a specific property listing."""
    # Skeleton implementation
    return {"id": listing_id, "description": "A beautiful suite with sea views.", "max_guests": 2}


class CreateBookingInput(BaseModel):
    listing_id: int = Field(description="The unique ID of the property to book.")
    guest_name: str = Field(description="The name of the guest making the booking.")
    check_in: str = Field(description="Check-in date in YYYY-MM-DD format.")
    check_out: str = Field(description="Check-out date in YYYY-MM-DD format.")

@tool("create_booking", args_schema=CreateBookingInput)
def create_booking(listing_id: int, guest_name: str, check_in: str, check_out: str) -> dict:
    """Create a new booking for a guest and return the booking confirmation."""
    # Skeleton implementation
    return {"booking_id": 123, "status": "confirmed"}