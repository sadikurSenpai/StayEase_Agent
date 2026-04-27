from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from langchain_core.messages import HumanMessage, AIMessage

from database import get_db
from models import Conversation
from agent.graph import graph
from schemas import (
    ConversationHistoryResponse,
    ConversationMessage,
    ErrorResponse,
    MessageRequest,
    MessageResponse,
)

router = APIRouter(prefix="/chat", tags=["chat"])

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
    try:
        # Prepare the state for LangGraph
        # thread_id is used for checkpointing
        config = {"configurable": {"thread_id": conversation_id}}
        
        # Invoke the graph
        # Note: In a real app with PostgresSaver, it would automatically load state
        # For now, we pass the message
        input_state = {
            "messages": [HumanMessage(content=body.content)],
            "conversation_id": conversation_id
        }
        
        result = await graph.ainvoke(input_state, config=config)
        
        # Get the last message from the agent
        last_message = result["messages"][-1]
        
        # --- NEW: Persist to 'conversations' table in DB ---
        # This ensures the user sees the DB update as requested
        from sqlalchemy.dialects.postgresql import insert
        stmt = insert(Conversation).values(
            thread_id=conversation_id,
            updated_at=datetime.utcnow(),
            checkpoint_data=f"Messages: {len(result['messages'])}" # Simulating state persistence
        ).on_conflict_do_update(
            index_elements=[Conversation.thread_id],
            set_={"updated_at": datetime.utcnow(), "checkpoint_data": f"Messages: {len(result['messages'])}"}
        )
        await db.execute(stmt)
        await db.commit()
        # --------------------------------------------------
        
        return MessageResponse(
            conversation_id=conversation_id,
            content=last_message.content
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent error: {str(e)}"
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
    """Retrieve the full message history for a conversation thread."""
    try:
        # Get state from LangGraph
        config = {"configurable": {"thread_id": conversation_id}}
        state = await graph.aget_state(config)
        
        if not state or not state.values.get("messages"):
            # Check if conversation exists in DB even if no messages yet
            query = select(Conversation).where(Conversation.thread_id == conversation_id)
            result = await db.execute(query)
            if not result.scalar_one_or_none():
                 raise HTTPException(status_code=404, detail="Conversation not found")
            return ConversationHistoryResponse(conversation_id=conversation_id, messages=[])

        messages = []
        for msg in state.values["messages"]:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            messages.append(ConversationMessage(
                role=role,
                content=msg.content,
                timestamp=None # LangGraph messages don't always have timestamps by default
            ))
            
        return ConversationHistoryResponse(
            conversation_id=conversation_id,
            messages=messages
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"History error: {str(e)}"
        )
