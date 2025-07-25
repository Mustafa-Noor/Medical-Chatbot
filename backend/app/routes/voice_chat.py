# from fastapi import APIRouter, File, UploadFile, Depends
# from fastapi.responses import FileResponse
# from sqlalchemy.ext.asyncio import AsyncSession
# from services import deps
# from pipeline.voice import process_voice_chat

# router = APIRouter()

# @router.post("/voice-chat")
# async def voice_chat(
#     audio: UploadFile = File(...),
#     db: AsyncSession = Depends(deps.get_db),
#     current_user=Depends(deps.get_current_user)
# ):
#     result = await process_voice_chat(audio, db, current_user)

#     return {
#         "text": result["text"],
#         "user_input": result["user_input"],
#         "audio_path": result["audio_path"]
#     }
