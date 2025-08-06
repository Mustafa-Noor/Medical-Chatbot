from fastapi import APIRouter, File, UploadFile, Depends, Query, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.security import deps
from app.pipelines.voice import transcribe_audio, get_chatbot_reply, generate_tts_audio, process_voice_chat
from app.services.chat_service import update_session_memory
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional
from app.database import get_db, AsyncSessionLocal
from fastapi import BackgroundTasks
import base64

router = APIRouter(
    prefix="/voice",
    tags=["Voice"]
)

@router.post("/transcribe")
async def transcribe_endpoint(audio: UploadFile, current_user=Depends(deps.get_current_user)):
    user_input = await transcribe_audio(audio)
    return {"user_input": user_input}


@router.post("/reply")
async def reply_endpoint(
    payload: dict,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(deps.get_current_user)
):
    user_input = payload["user_input"]
    topic = payload["topic"]
    session_id = payload.get("session_id")

    chatbot_text, new_session_id = await get_chatbot_reply(user_input, topic, db, current_user, session_id, background_tasks)
    return {
        "text": chatbot_text,
        "session_id": new_session_id
    }


@router.post("/tts")
async def tts_endpoint(
    payload: dict,
    background_tasks: BackgroundTasks,
):
    text = payload["text"]
    session_id = payload.get("session_id")

    audio_stream = generate_tts_audio(text)

    if session_id:
        # Do NOT pass `db` directly — create a fresh one in background task
        background_tasks.add_task(update_session_memory_safe, session_id)

    return StreamingResponse(audio_stream, media_type="audio/webm; codecs=opus")


async def update_session_memory_safe(session_id: str):
    session_id = int(session_id)
    try:
        async with AsyncSessionLocal() as db:
            await update_session_memory(session_id, db)
    except Exception as e:
        print(f"[TTS] Memory update failed for session {session_id}: {e}")


@router.post("/process")
async def full_pipeline(
    audio: UploadFile,
    topic: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(deps.get_current_user),
    session_id: str | None = None
):
    result = await process_voice_chat(audio, topic, db, current_user, session_id, background_tasks)
    return {
        "text": result["text"],
        "user_input": result["user_input"],
        "session_id": result["session_id"]
    }

# @router.post("/voice-chat")
# async def voice_chat(
#     audio: UploadFile = File(...),
#     topic: str = Form(...),
#     db: AsyncSession = Depends(deps.get_db),
#     session_id: Optional[str] = Form(None),
#     current_user=Depends(deps.get_current_user)
# ):

#     result = await process_voice_chat(audio, topic, db, current_user, session_id)

#     # Convert audio stream to base64
#     audio_base64 = base64.b64encode(result["audio_stream"].read()).decode("utf-8")

#     return JSONResponse({
#         "text": result["text"],
#         "user_input": result["user_input"],
#         "audio_base64": audio_base64,
#         "session_id": result["session_id"]
#     })
#     # result = await process_voice_chat(audio, topic, db, current_user)

#     # return {
#     #     "text": result["text"],
#     #     "user_input": result["user_input"],
#     #     "audio_path": result["audio_path"]
#     # }
