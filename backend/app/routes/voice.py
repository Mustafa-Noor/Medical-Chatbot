from fastapi import APIRouter, File, UploadFile, Depends, Query, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.security import deps
from app.pipelines.voice import process_voice_chat
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional
import base64

router = APIRouter(
    prefix="/voice",
    tags=["Voice"]
)

@router.post("/voice-chat")
async def voice_chat(
    audio: UploadFile = File(...),
    topic: str = Form(...),
    db: AsyncSession = Depends(deps.get_db),
    session_id: Optional[str] = Form(None),
    current_user=Depends(deps.get_current_user)
):

    result = await process_voice_chat(audio, topic, db, current_user, session_id)

    # Convert audio stream to base64
    audio_base64 = base64.b64encode(result["audio_stream"].read()).decode("utf-8")

    return JSONResponse({
        "text": result["text"],
        "user_input": result["user_input"],
        "audio_base64": audio_base64
    })
    # result = await process_voice_chat(audio, topic, db, current_user)

    # return {
    #     "text": result["text"],
    #     "user_input": result["user_input"],
    #     "audio_path": result["audio_path"]
    # }
