from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Boolean, Text, Date, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass

class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(100), nullable=False)
    price_per_night = Column(Integer, nullable=False)
    description = Column(Text)
    max_guests = Column(Integer, nullable=False)
    available = Column(Boolean, default=True)

    bookings = relationship("Booking", back_populates="listing")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    guest_name = Column(String(255), nullable=False)
    check_in = Column(Date, nullable=False)
    check_out = Column(Date, nullable=False)
    total_price = Column(Integer, nullable=False)
    status = Column(String(50), default="confirmed")

    listing = relationship("Listing", back_populates="bookings")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String(255), unique=True, nullable=False)
    checkpoint_data = Column(Text) # Storing as text/bytea for LangGraph
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
