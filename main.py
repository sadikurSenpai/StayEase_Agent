from fastapi import FastAPI

from routers import chat

app = FastAPI(
    title="StayEase AI Agent",
    description="Conversational accommodation booking agent for StayEase Bangladesh",
    version="1.0.0",
)

app.include_router(chat.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the StayEase AI Agent API"}