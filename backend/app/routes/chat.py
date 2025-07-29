from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.chat import ChatSession, ChatMessage, SenderType, SourceType
from app.schemas.chat import ChatRequest, ChatResponse, ChatSessionOut, ChatMessageOut
from app.security import deps
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.future import select
from app.services.chat_service import handle_chat
from sqlalchemy import delete


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/send-message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(deps.get_current_user)
):
    return await handle_chat(request, db, current_user)



@router.get("/sessions", response_model=list[ChatSessionOut])
async def get_sessions(
    topic: str = Query(..., description="Topic selected from dropdown"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(deps.get_current_user)
):
    result = await db.execute(
        select(ChatSession)
        .where(
            ChatSession.user_id == current_user.id,
            ChatSession.topic == topic
        )
        .order_by(ChatSession.created_at.desc())
    )
    sessions = result.scalars().all()
    return sessions


@router.get("/messages", response_model=list[ChatMessageOut])
async def get_messages_for_session(
    session_id: int = Query(..., description="Session ID to fetch messages for"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(deps.get_current_user)
):
    # 1. Check if session belongs to user
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.id == session_id)
        .where(ChatSession.user_id == current_user.id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or not authorized")

    # 2. Fetch messages in ascending order
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
    )
    messages = result.scalars().all()

    return messages


@router.delete("/session/{session_id}")
async def delete_chat_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(deps.get_current_user)
):
    # Check if session exists and belongs to user
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or not authorized")

    # Delete session and cascade messages if relationship is set up
    await db.delete(session)
    await db.commit()

    return {"message": "Session deleted successfully"}




#############