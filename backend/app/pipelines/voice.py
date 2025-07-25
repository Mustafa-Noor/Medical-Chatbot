import os
import uuid
from groq import Groq
from services.chat_service import handle_chat
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.services.chat_service import handle_chat

client = Groq(api_key=settings.Groq_key)

async def process_voice_chat(audio_file: UploadFile, db: AsyncSession, current_user):
    audio_id = str(uuid.uuid4())
    audio_path = f"temp_{audio_id}.wav"
    
    # 1. Save file
    with open(audio_path, "wb") as f:
        f.write(await audio_file.read())

    # 2. Transcribe with Groq
    with open(audio_path, "rb") as f:
        stt_response = client.audio.transcriptions.create(
            file=f,
            model="whisper-large-v3-turbo",
            response_format="verbose_json",
            language="en",
            temperature=0.0
        )
    os.remove(audio_path)
    user_input = stt_response.text

    # 3. Chatbot logic
    chat_response = await handle_chat(
        request={"message": user_input},
        db=db,
        current_user=current_user
    )
    chatbot_text = chat_response["response"]

    # 4. Text-to-Speech
    output_audio_path = f"output_{audio_id}.wav"
    tts_response = client.audio.speech.create(
        model="playai-tts",
        voice="Deedee-PlayAI",
        input=chatbot_text,
        response_format="wav"
    )
    tts_response.write_to_file(output_audio_path)

    return {
        "text": chatbot_text,
        "audio_path": output_audio_path,
        "user_input": user_input
    }
