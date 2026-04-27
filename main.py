from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers import chat
from init_db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize and seed database on startup
    await init_db()
    yield

app = FastAPI(
    title="StayEase AI Agent",
    description="Conversational accommodation booking agent for StayEase Bangladesh",
    version="1.0.0",
    lifespan=lifespan,
)


# Mounts the chat router under /api, so final paths are /api/chat/{id}/message and /api/chat/{id}/history
app.include_router(chat.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the StayEase AI Agent API"}