from fastapi import APIRouter, File, UploadFile, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.security import deps
from app.pipelines.voice import process_voice_chat

router = APIRouter(
    prefix="/voice",
    tags=["Voice"]
)

@router.post("/voice-chat")
async def voice_chat(
    audio: UploadFile = File(...),
    topic: str = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user=Depends(deps.get_current_user)
):
    result = await process_voice_chat(audio, topic, db, current_user)

    return {
        "text": result["text"],
        "user_input": result["user_input"],
        "audio_path": result["audio_path"]
    }
