from typing import TypedDict, Annotated, Literal
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    Represents the state of our conversation and agent.
    """
    messages: Annotated[list[BaseMessage], add_messages]
    conversation_id: str
    intent: Literal["search", "details", "book", "escalate"] | None
