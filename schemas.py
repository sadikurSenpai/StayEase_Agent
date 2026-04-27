from __future__ import annotations

import datetime
from typing import Literal

from pydantic import BaseModel, Field


#  Request schemas
class MessageRequest(BaseModel):
    # guest sends content: str
    content: str = Field(..., min_length=1, description="Guest's message text") 


#  Response schemas
class MessageResponse(BaseModel):
    # agent replies with conversation_id, hardcoded role="assistant", and content: str
    conversation_id: str
    role: Literal["assistant"] = "assistant" 
    content: str 


class ConversationMessage(BaseModel):
    # each history item with discriminated role union and an optional timestamp (conversations table has updated_at but individual
    # message timestamps come from checkpoint data)
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime.datetime | None = None


class ConversationHistoryResponse(BaseModel):
    # wraps the list under conversation_id
    conversation_id: str
    messages: list[ConversationMessage]


#  Error schema
class ErrorResponse(BaseModel):
    # shared shape for all 4xx/5xx responses= declarations in the router
    detail: str
