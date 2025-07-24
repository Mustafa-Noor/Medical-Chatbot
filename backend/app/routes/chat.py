from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.chat import ChatSession, ChatMessage, SenderType, SourceType
from app.schemas.chat import ChatRequest, ChatResponse, ChatSessionOut, ChatMessageOut
from app.security import deps
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.future import select


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
    # 1. Check if session_id is provided
    if request.session_id is not None:
        result = await db.execute(
            select(ChatSession).where(
                ChatSession.id == request.session_id,
                ChatSession.user_id == current_user.id
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        # Create new session
        session = ChatSession(
            user_id=current_user.id,
            topic=request.topic,
            title=request.message[:50]  # First 50 chars as default title
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)

    # 2. Save user message
    user_msg = ChatMessage(
        session_id=session.id,
        sender=SenderType.user,
        message=request.message
    )
    db.add(user_msg)
    await db.commit()


    # here llm logic will be implemented
    # 3. Generate bot reply (placeholder logic — replace with real bot logic)
    reply_text = "This is a placeholder reply."  # Replace with actual logic
    reply_source = SourceType.llm

    # 4. Save assistant message
    bot_msg = ChatMessage(
        session_id=session.id,
        sender=SenderType.assistant,
        message=reply_text,
        source=reply_source,
    )
    db.add(bot_msg)
    await db.commit()

    # 5. Return response
    return ChatResponse(
        session_id=session.id,
        reply=reply_text,
        source=reply_source,
    )


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
