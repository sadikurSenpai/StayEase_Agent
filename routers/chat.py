from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas import (
    ConversationHistoryResponse,
    ErrorResponse,
    MessageRequest,
    MessageResponse,
)

router = APIRouter(prefix="/chat", tags=["chat"])

#   - Both handlers are fully typed (MessageRequest in, MessageResponse / ConversationHistoryResponse out)
#   - Both accept the AsyncSession dependency so they're ready to receive DB calls
#   - Both raise 501 stubs until the agent service layer is wired in
#   - OpenAPI error responses documented via responses= for each possible HTTP error code

@router.post(
    "/{conversation_id}/message",
    response_model=MessageResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        404: {"model": ErrorResponse, "description": "Conversation not found"},
        500: {"model": ErrorResponse, "description": "Agent processing error"},
    },
    status_code=status.HTTP_200_OK,
)
async def send_message(
    conversation_id: str,
    body: MessageRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Receive a guest message, run it through the LangGraph agent, and return the reply."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Agent integration not yet implemented",
    )


@router.get(
    "/{conversation_id}/history",
    response_model=ConversationHistoryResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Conversation not found"},
        500: {"model": ErrorResponse, "description": "Failed to retrieve history"},
    },
    status_code=status.HTTP_200_OK,
)
async def get_conversation_history(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
) -> ConversationHistoryResponse:
    """Retrieve the full message history for a conversation thread from the conversations table."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="History retrieval not yet implemented",
    )
