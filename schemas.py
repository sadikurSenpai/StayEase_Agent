from __future__ import annotations

import datetime
from typing import Literal

from pydantic import BaseModel, Field


#  Request schemas
class MessageRequest(BaseModel):
    content: str = Field(..., min_length=1, description="Guest's message text")


#  Response schemas
class MessageResponse(BaseModel):
    conversation_id: str
    role: Literal["assistant"] = "assistant"
    content: str


class ConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime.datetime | None = None


class ConversationHistoryResponse(BaseModel):
    conversation_id: str
    messages: list[ConversationMessage]


#  Error schema
class ErrorResponse(BaseModel):
    detail: str
