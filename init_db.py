import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from models import Base, Listing
from database import DATABASE_URL, AsyncSessionLocal

async def seed_data():
    async with AsyncSessionLocal() as session:
        # Check if we already have data
        from sqlalchemy import select
        result = await session.execute(select(Listing).limit(1))
        if result.scalars().first():
            print("Database already seeded.")
            return

        print("Seeding database with BD tourist spots...")
        listings = [
            Listing(
                name="Sea View Suite",
                location="Cox's Bazar",
                price_per_night=5000,
                description="A luxurious suite with a direct view of the Bay of Bengal.",
                max_guests=2,
                available=True
            ),
            Listing(
                name="Ocean Breeze Villa",
                location="Cox's Bazar",
                price_per_night=8500,
                description="Spacious villa perfect for families, located right on the beach.",
                max_guests=5,
                available=True
            ),
            Listing(
                name="Hilltop Resthouse",
                location="Cox's Bazar",
                price_per_night=3000,
                description="Quiet resthouse on the hills of Himchari with a panoramic view.",
                max_guests=2,
                available=True
            ),
            Listing(
                name="Sylhet Tea Garden Cottage",
                location="Sylhet",
                price_per_night=4500,
                description="Cozy cottage surrounded by lush tea gardens in Sreemangal.",
                max_guests=3,
                available=True
            ),
            Listing(
                name="Saint Martin Coral Resort",
                location="Saint Martin",
                price_per_night=6000,
                description="Experience the blue waters in the only coral island of Bangladesh.",
                max_guests=2,
                available=True
            )
        ]
        session.add_all(listings)
        await session.commit()
        print("Database seeded successfully.")

async def init_db():
    print(f"Connecting to {DATABASE_URL}...")
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
    
    await seed_data()
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())
