import os
from typing import Dict, Any
from langchain_core.messages import AIMessage, HumanMessage
from .state import AgentState

def classify_intent(state: AgentState) -> dict:
    """
    Analyzes the latest user message to categorize the intent.
    Updates the state with the detected intent.
    """
    # Simple keyword-based classification for the skeleton
    last_message = state["messages"][-1].content.lower()
    
    if any(k in last_message for k in ["book", "confirm", "reserve"]):
        intent = "book"
    elif any(k in last_message for k in ["detail", "info", "about", "tell me more"]):
        intent = "details"
    elif any(k in last_message for k in ["search", "find", "available", "room", "stay"]):
        intent = "search"
    else:
        # Default or escalate if it's completely off-topic
        intent = "search" # Default to search for now
        
    return {"intent": intent}

def agent_node(state: AgentState) -> dict:
    """
    Decides whether to call a tool or reply to the user.
    For this skeleton, we return a mock response that simulates the agent's behavior.
    """
    # In a real implementation, you'd call ChatGroq(api_key=...).bind_tools(tools)
    intent = state.get("intent", "search")
    
    # Mocking the AI's response based on intent
    if intent == "search":
        content = "I'm searching for available properties for you..."
    elif intent == "details":
        content = "Let me get the details for that property."
    elif intent == "book":
        content = "Processing your booking request."
    else:
        content = "How can I help you today?"
        
    return {"messages": [AIMessage(content=content)]}

def escalate_node(state: AgentState) -> dict:
    """
    Handles messages that fall outside the three main intents.
    """
    return {"messages": [AIMessage(content="I'm sorry, I can only help with searching, details, and booking. I'll escalate this to a human agent.")]}
