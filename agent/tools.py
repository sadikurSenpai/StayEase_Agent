from langchain_core.tools import tool
from pydantic import BaseModel, Field
from sqlalchemy import select, and_
from datetime import datetime
from database import AsyncSessionLocal
from models import Listing, Booking

class SearchPropertiesInput(BaseModel):
    location: str = Field(description="The city or location where the guest wants to stay (e.g., Cox's Bazar).")
    check_in: str = Field(description="Check-in date in YYYY-MM-DD format.")
    check_out: str = Field(description="Check-out date in YYYY-MM-DD format.")
    guests: int = Field(description="Number of guests.")

@tool("search_available_properties", args_schema=SearchPropertiesInput)
async def search_available_properties(location: str, check_in: str, check_out: str, guests: int) -> list[dict]:
    """Search for available properties in a given location for specific dates and guest count."""
    async with AsyncSessionLocal() as session:
        # Simple search logic: location match and enough guest capacity
        # In a real app, we'd also check date availability against the bookings table
        query = select(Listing).where(
            and_(
                Listing.location.ilike(f"%{location}%"),
                Listing.max_guests >= guests,
                Listing.available == True
            )
        )
        result = await session.execute(query)
        listings = result.scalars().all()
        
        return [
            {
                "id": l.id,
                "name": l.name,
                "location": l.location,
                "price_per_night": l.price_per_night,
                "max_guests": l.max_guests
            } for l in listings
        ]


class GetListingDetailsInput(BaseModel):
    listing_id: int = Field(description="The unique ID of the property listing.")

@tool("get_listing_details", args_schema=GetListingDetailsInput)
async def get_listing_details(listing_id: int) -> dict:
    """Retrieve detailed information and description for a specific property listing."""
    async with AsyncSessionLocal() as session:
        query = select(Listing).where(Listing.id == listing_id)
        result = await session.execute(query)
        listing = result.scalar_one_or_none()
        
        if not listing:
            return {"error": f"Listing with ID {listing_id} not found."}
            
        return {
            "id": listing.id,
            "name": listing.name,
            "description": listing.description,
            "price_per_night": listing.price_per_night,
            "max_guests": listing.max_guests,
            "location": listing.location
        }


class CreateBookingInput(BaseModel):
    listing_id: int = Field(description="The unique ID of the property to book.")
    guest_name: str = Field(description="The name of the guest making the booking.")
    check_in: str = Field(description="Check-in date in YYYY-MM-DD format.")
    check_out: str = Field(description="Check-out date in YYYY-MM-DD format.")

@tool("create_booking", args_schema=CreateBookingInput)
async def create_booking(listing_id: int, guest_name: str, check_in: str, check_out: str) -> dict:
    """Create a new booking for a guest and return the booking confirmation."""
    async with AsyncSessionLocal() as session:
        # Get listing to calculate total price
        query = select(Listing).where(Listing.id == listing_id)
        result = await session.execute(query)
        listing = result.scalar_one_or_none()
        
        if not listing:
            return {"error": f"Listing with ID {listing_id} not found."}
            
        # Parse dates
        d1 = datetime.strptime(check_in, "%Y-%m-%d").date()
        d2 = datetime.strptime(check_out, "%Y-%m-%d").date()
        num_nights = (d2 - d1).days
        
        if num_nights <= 0:
            return {"error": "Check-out must be after check-in."}
            
        total_price = num_nights * listing.price_per_night
        
        booking = Booking(
            listing_id=listing_id,
            guest_name=guest_name,
            check_in=d1,
            check_out=d2,
            total_price=total_price,
            status="confirmed"
        )
        
        session.add(booking)
        await session.commit()
        await session.refresh(booking)
        
        return {
            "booking_id": booking.id,
            "property_name": listing.name,
            "guest_name": booking.guest_name,
            "total_price": booking.total_price,
            "status": booking.status
        }