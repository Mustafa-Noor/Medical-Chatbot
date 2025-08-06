from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from sqlalchemy import update

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.models.chat import ChatSession, ChatMessage, SenderType, SourceType
from app.schemas.chat import ChatRequest, ChatResponse
from app.pipelines.graph import run_pipeline
from app.utils.llm import call_llm
from fastapi import BackgroundTasks

async def handle_chat(
    request: ChatRequest, 
    db: AsyncSession, 
    current_user,
    background_tasks: BackgroundTasks
) -> ChatResponse:
    
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
    # await db.commit()

    # 3. Fetch recent messages (6)
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.id.desc())
        .limit(6)
    )
    recent_messages = list(reversed(result.scalars().all()))

    memory_pairs = [
        f"{'User' if m.sender == SenderType.user else 'Assistant'}: {m.message}"
        for m in recent_messages
    ]

    recent_context = "\n".join(memory_pairs)

    # 4. Use long-term memory + recent context
    long_term_memory = session.memory or ""
    if long_term_memory:
        combined_context = long_term_memory
    else:
        combined_context = recent_context

    print("Context sent to LLM:\n", combined_context)

    # 5. Run pipeline with memory context
    result = run_pipeline(
        query=request.message,
        topic=request.topic,
        memory=combined_context
    )

    reply_text = result["answer"]
    reply_source = SourceType(result["source"])

    # 6. Save assistant message
    bot_msg = ChatMessage(
        session_id=session.id,
        sender=SenderType.assistant,
        message=reply_text,
        source=reply_source
    )
    db.add(bot_msg)
    await db.commit()

    # 7. Background task to update memory
    background_tasks.add_task(update_session_memory, session.id, db)

    # 8. Return response
    return ChatResponse(
        session_id=session.id,
        reply=reply_text,
        source=reply_source
    )

# it does not have background task of memory saving
async def handle_voice_chat(
    request: ChatRequest, 
    db: AsyncSession, 
    current_user,
    background_tasks: BackgroundTasks
) -> ChatResponse:
    
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

    # 3. Fetch recent messages (6)
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.id.desc())
        .limit(6)
    )
    recent_messages = list(reversed(result.scalars().all()))

    memory_pairs = [
        f"{'User' if m.sender == SenderType.user else 'Assistant'}: {m.message}"
        for m in recent_messages
    ]

    recent_context = "\n".join(memory_pairs)

    # 4. Use long-term memory + recent context
    long_term_memory = session.memory or ""
    if long_term_memory:
        combined_context = long_term_memory
    else:
        combined_context = recent_context

    print("Context sent to LLM:\n", combined_context)

    # 5. Run pipeline with memory context
    result = run_pipeline(
        query=request.message,
        topic=request.topic,
        memory=combined_context
    )

    reply_text = result["answer"]
    reply_source = SourceType(result["source"])

    # 6. Save assistant message
    bot_msg = ChatMessage(
        session_id=session.id,
        sender=SenderType.assistant,
        message=reply_text,
        source=reply_source
    )
    db.add(bot_msg)
    await db.commit()

    # # 7. Background task to update memory
    # background_tasks.add_task(update_session_memory, session.id, db)

    # 8. Return response
    return ChatResponse(
        session_id=session.id,
        reply=reply_text,
        source=reply_source
    )

async def update_session_memory(session_id: str, db: AsyncSession):
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.id)
        .limit(8)
    )
    all_messages = result.scalars().all()

    memory_pairs = [
        f"{'User' if m.sender == SenderType.user else 'Assistant'}: {m.message}"
        for m in all_messages
    ]

    if len(memory_pairs) <= 6:
        new_memory = "\n".join(memory_pairs)
    else:
        joined_memory = "\n".join(memory_pairs)
        summary_prompt = f"""You are a summarization assistant. Summarize the following medical conversation between a user and an assistant.

    Provide a **brief and concise** summary that captures only the most important medical points and user concerns. Avoid unnecessary details.

    Conversation:
    {joined_memory}

    Concise Summary:"""
        new_memory = call_llm(summary_prompt)

    # Save new memory to session
    await db.execute(
        update(ChatSession)
        .where(ChatSession.id == session_id)
        .values(memory=new_memory)
    )
    await db.commit()






# async def handle_chat(request: ChatRequest, db: AsyncSession, current_user) -> ChatResponse:
#     # 1. Get or create chat session
#     if request.session_id is not None:
#         result = await db.execute(
#             select(ChatSession).where(
#                 ChatSession.id == request.session_id,
#                 ChatSession.user_id == current_user.id
#             )
#         )
#         session = result.scalar_one_or_none()
#         if not session:
#             raise HTTPException(status_code=404, detail="Session not found")
#     else:
        
#         session = ChatSession(
#             user_id=current_user.id,
#             topic=request.topic,
#             title=request.message[:50]
#         )
#         db.add(session)
#         await db.commit()
#         await db.refresh(session)

#     # 2. Save user message
#     user_msg = ChatMessage(
#         session_id=session.id,
#         sender=SenderType.user,
#         message=request.message
#     )
#     db.add(user_msg)
#     await db.commit()

#     result = await db.execute(
#     select(ChatMessage)
#     .where(ChatMessage.session_id == session.id)
#     .order_by(ChatMessage.id.desc())
#     .limit(6)
#     )

#     recent_messages = list(reversed(result.scalars().all()))

#     print("recent messages: ", recent_messages)


#     memory_pairs = [
#         f"{'User' if m.sender == SenderType.user else 'Assistant'}: {m.message}"
#         for m in recent_messages
#     ]

#     # Decide context strategy
#     if len(memory_pairs) < 6:  # Less than 3 turns
#         memory = "\n".join(memory_pairs)
#     else:
#         # Summarize previous messages using your normal `call_llm`
#         memory = "\n".join(memory_pairs)
#         summary_prompt = f"""
#         You are a summarization assistant. Summarize the following medical conversation between a user and an assistant:

#         {memory}

#         Summarized Context:
#         """
#         memory = call_llm(summary_prompt)


#     print("memeory:" , memory)
#     # 3. Run pipeline to get reply
#     result = run_pipeline(query=request.message, topic=request.topic, memory = memory)
#     reply_text = result["answer"]
#     reply_source = SourceType(result["source"])  # Ensures it's a valid enum value


#     # 4. Save assistant reply
#     bot_msg = ChatMessage(
#         session_id=session.id,
#         sender=SenderType.assistant,
#         message=reply_text,
#         source=reply_source
#     )
#     db.add(bot_msg)
#     await db.commit()
#     # print("message response with source:", reply_text, reply_source)

#     # 5. Return response
#     return ChatResponse(
#         session_id=session.id,
#         reply=reply_text,
#         source=reply_source
#     )

