from __future__ import annotations

import datetime

from langchain_core.tools import tool
from pydantic import BaseModel, Field


#  Input schemas 

class SearchPropertiesInput(BaseModel):
    location: str = Field(..., description="City or area name, e.g. Cox's Bazar")
    check_in: datetime.date = Field(..., description="Check-in date (YYYY-MM-DD)")
    check_out: datetime.date = Field(..., description="Check-out date (YYYY-MM-DD)")
    num_guests: int = Field(..., ge=1, description="Number of guests")


class ListingDetailsInput(BaseModel):
    listing_id: int = Field(..., description="Primary key of the listing row")


class CreateBookingInput(BaseModel):
    listing_id: int = Field(..., description="Primary key of the listing to book")
    guest_name: str = Field(..., description="Full name of the guest")
    check_in: datetime.date = Field(..., description="Check-in date (YYYY-MM-DD)")
    check_out: datetime.date = Field(..., description="Check-out date (YYYY-MM-DD)")


#  Tool definitions 

@tool(args_schema=SearchPropertiesInput)
def search_available_properties(
    location: str,
    check_in: datetime.date,
    check_out: datetime.date,
    num_guests: int,
) -> list[dict]:
    """Search listings table for available properties matching location, dates, and guest count."""
    # TODO: async DB query —
    #   SELECT * FROM listings
    #   WHERE location ILIKE %location%
    #     AND available = true
    #     AND max_guests >= num_guests
    return []


@tool(args_schema=ListingDetailsInput)
def get_listing_details(listing_id: int) -> dict:
    """Fetch the full details of a single listing row by its primary key."""
    # TODO: async DB query — SELECT * FROM listings WHERE id = listing_id
    return {}


@tool(args_schema=CreateBookingInput)
def create_booking(
    listing_id: int,
    guest_name: str,
    check_in: datetime.date,
    check_out: datetime.date,
) -> dict:
    """Insert a new row into the bookings table and return confirmation details."""
    # TODO: async DB query —
    #   1. fetch price_per_night from listings WHERE id = listing_id
    #   2. total_price = price_per_night * (check_out - check_in).days
    #   3. INSERT INTO bookings (listing_id, guest_name, check_in, check_out, total_price)
    return {}


# Exported list consumed by ToolNode in graph.py
TOOLS = [search_available_properties, get_listing_details, create_booking]