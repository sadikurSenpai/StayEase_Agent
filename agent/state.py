from __future__ import annotations

from typing import Annotated, Literal

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict):
    # Full conversation history. add_messages appends rather than replaces —
    # required for the ReAct loop and PostgresSaver checkpointing to work.
    messages: Annotated[list[BaseMessage], add_messages]

    # Maps to conversations.thread_id so PostgresSaver can load/save per session.
    conversation_id: str

    intent: Literal["search", "details", "book", "escalate"] | None
