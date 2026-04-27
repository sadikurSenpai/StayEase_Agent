from fastapi import FastAPI

from routers import chat

from dotenv import load_dotenv
load_dotenv()
import os
from langchain_groq import ChatGroq

llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="llama-3.1-8b-instant", temperature=0.7)
result= llm.invoke("What is the capital of France?").content
print(result)


# app = FastAPI(
#     title="StayEase AI Agent",
#     description="Conversational accommodation booking agent for StayEase Bangladesh",
#     version="1.0.0",
# )


# # Mounts the chat router under /api, so final paths are /api/chat/{id}/message and /api/chat/{id}/history
# app.include_router(chat.router, prefix="/api")

# @app.get("/")
# async def root():
#     return {"message": "Welcome to the StayEase AI Agent API"}