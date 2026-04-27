import os
from typing import Dict, Any, Literal
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from .state import AgentState
from .tools import search_available_properties, get_listing_details, create_booking

# Initialize LLM
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.environ.get("GROQ_API_KEY")
)

class IntentClassification(BaseModel):
    """Plan for the next step based on the user's message."""
    intent: Literal["search", "details", "book", "escalate"] = Field(
        description="The classified intent of the user's message."
    )

def classify_intent(state: AgentState) -> dict:
    """
    Analyzes the latest user message to categorize the intent using the LLM.
    """
    system_prompt = (
        "You are an intent classifier for StayEase, a rental platform in Bangladesh. "
        "Classify the user's message into one of these categories:\n"
        "- search: If the user is looking for available properties, rooms, or stays.\n"
        "- details: If the user is asking for more info about a specific property or listing.\n"
        "- book: If the user wants to confirm a booking or make a reservation.\n"
        "- escalate: If the user's request is outside these three (e.g., complaints, complex support, unrelated topics)."
    )
    
    # Using structured output for classification
    structured_llm = llm.with_structured_output(IntentClassification)
    response = structured_llm.invoke([
        SystemMessage(content=system_prompt),
        *state["messages"]
    ])
    
    return {"intent": response.intent}

def agent_node(state: AgentState) -> dict:
    """
    The main agent node that decides which tool to call or responds to the user.
    """
    system_prompt = (
        "You are the StayEase AI Assistant, helping guests find and book accommodations in Bangladesh. "
        "You must handle three main tasks: search for properties, provide details, and create bookings. "
        "Always be polite, helpful, and concise. All prices are in BDT. "
        "Current context: User's intent is classified as {intent}."
    ).format(intent=state.get("intent"))
    
    # Bind tools to the LLM
    tools = [search_available_properties, get_listing_details, create_booking]
    llm_with_tools = llm.bind_tools(tools)
    
    response = llm_with_tools.invoke([
        SystemMessage(content=system_prompt),
        *state["messages"]
    ])
    
    return {"messages": [response]}

def escalate_node(state: AgentState) -> dict:
    """
    Handles out-of-scope requests by politely informing the user about human escalation.
    """
    response_text = (
        "I'm sorry, I'm only able to assist with searching for properties, providing listing details, "
        "and managing bookings at the moment. I've escalated your request to a human representative "
        "who will get back to you shortly. Is there anything else I can help with regarding our rentals?"
    )
    return {"messages": [AIMessage(content=response_text)]}
