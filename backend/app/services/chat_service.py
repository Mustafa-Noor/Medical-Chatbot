from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.models.chat import ChatSession, ChatMessage, SenderType, SourceType
from app.schemas.chat import ChatRequest, ChatResponse
from app.pipelines.graph import run_pipeline

async def handle_chat(request: ChatRequest, db: AsyncSession, current_user) -> ChatResponse:
    # 1. Get or create chat session
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
        session = ChatSession(
            user_id=current_user.id,
            topic=request.topic,
            title=request.message[:50]
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

    # 3. Run pipeline to get reply
    reply_text = run_pipeline(query=request.message, topic=request.topic)
    reply_source = SourceType.llm

    # 4. Save assistant reply
    bot_msg = ChatMessage(
        session_id=session.id,
        sender=SenderType.assistant,
        message=reply_text,
        source=reply_source
    )
    db.add(bot_msg)
    await db.commit()

    # 5. Return response
    return ChatResponse(
        session_id=session.id,
        reply=reply_text,
        source=reply_source
    )

