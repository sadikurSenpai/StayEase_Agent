import os
from collections.abc import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv()

DATABASE_URL: str = os.environ["DATABASE_URL"]

# fully async SQLAlchemy 2.0 pattern, compatible with FastAPI's async lifecycle
engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

print("DB Engine initialized successfully.")

# yields an AsyncSession as a FastAPI dependency — routers import this later
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session