from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.models.chat import ChatSession, ChatMessage, SenderType, SourceType
from app.schemas.chat import ChatRequest, ChatResponse

async def handle_chat(request: ChatRequest, db: AsyncSession, current_user) -> ChatResponse:
    # 1. Handle session
    session = await get_or_create_session(request, db, current_user)

    # 2. Save user message
    await save_message(db, session.id, SenderType.user, request.message)

    # 3. Generate reply (placeholder logic)
    reply_text = await generate_bot_reply(request.message)  
    reply_source = SourceType.llm

    # 4. Save assistant message
    await save_message(db, session.id, SenderType.assistant, reply_text, reply_source)

    # 5. Return response
    return ChatResponse(
        session_id=session.id,
        reply=reply_text,
        source=reply_source,
    )

async def get_or_create_session(request: ChatRequest, db: AsyncSession, current_user):
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
        return session

    # Create new session
    session = ChatSession(
        user_id=current_user.id,
        topic=request.topic,
        title=request.message[:50]
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session

async def save_message(db: AsyncSession, session_id: int, sender: SenderType, message: str, source: SourceType = None):
    msg = ChatMessage(
        session_id=session_id,
        sender=sender,
        message=message,
        source=source
    )
    db.add(msg)
    await db.commit()

async def generate_bot_reply(user_message: str) -> str:
    # TODO: Replace this with your actual LLM logic
    return "This is a placeholder reply."
