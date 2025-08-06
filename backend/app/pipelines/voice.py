# import os
# import uuid
# from groq import Groq
# from fastapi import UploadFile
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.config import settings
# from app.services.chat_service import handle_chat
# from app.schemas.chat import ChatRequest
# from fastapi.responses import StreamingResponse
# from io import BytesIO
# from elevenlabs import ElevenLabs
# import logging
# logger = logging.getLogger()
# from io import BytesIO



# async def process_voice_chat(audio_file: UploadFile, topic: str, db: AsyncSession, current_user, session_id: str | None = None):
#     print("🚨 Voice reached")
#     logger.info("🎤================= VOICE PIPELINE START =================")
#     logger.info("🚨 Voice pipeline has been entered!")

#     # 1. Read audio once
#     audio_bytes = await audio_file.read()

#     # Optional: save to disk for logging/debug
#     audio_path = f"/tmp/temp_{uuid.uuid4()}.wav"
#     with open(audio_path, "wb") as f:
#         f.write(audio_bytes)
#     logger.info(f"💾 Audio saved to {audio_path}")


#     audio_file_like = BytesIO(audio_bytes)
#     audio_file_like.name = "audio.wav"
#     logger.info(f"📁 Audio filename received: {audio_file.filename}")


#     # 2. Transcribe using in-memory BytesIO
#     groq_client = Groq(api_key=settings.Groq_key)

#     stt_response = groq_client.audio.transcriptions.create(
#         file=audio_file_like,
#         model="whisper-large-v3-turbo",
#         response_format="verbose_json",
#         language="en",
#         temperature=0.0
#     )

#     user_input = stt_response.text
#     logger.info(f"📝 Transcription: {user_input}")

#     # Cleanup file (optional)
#     os.remove(audio_path)

#     # 3. Run chat pipeline
#     logger.info("🧠 [Running Chat Pipeline]")
#     chat_request = ChatRequest(message=user_input, topic=topic, session_id=session_id)

#     chat_response = await handle_chat(
#         request=chat_request,
#         db=db,
#         current_user=current_user
#     )

#     print("voice response session id :", chat_response.session_id)

#     chatbot_text = chat_response.reply
#     logger.info(f"✅ Final Answer: {chatbot_text[:300]}")
#     logger.info(f"🔗 Source: {chat_response.source}")

#     # 4. Convert reply to audio with ElevenLabs
#     eleven_client = ElevenLabs(api_key=settings.Eleven_key)
#     logger.info("🔊 [Generating TTS Audio with ElevenLabs]")

#     tts_generator = eleven_client.text_to_speech.convert(
#         voice_id="JBFqnCBsd6RMkjVDRZzb",
#         output_format="mp3_44100_128",
#         text=chatbot_text,
#         model_id="eleven_multilingual_v2"
#     )

#     tts_audio_bytes = b"".join(tts_generator)
#     audio_stream = BytesIO(tts_audio_bytes)

#     logger.info(f"🔉 Final TTS audio size: {len(tts_audio_bytes)} bytes")
#     logger.info("📤 [Voice Chat Completed] Response ready to return")
#     logger.info("🎤================= VOICE PIPELINE END ===================")

#     return {
#         "text": chatbot_text,
#         "user_input": user_input,
#         "audio_stream": audio_stream,
#         "session_id": chat_response.session_id
#     }


# app/utils/audio_utils.py

import os
import uuid
from io import BytesIO
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from groq import Groq
from elevenlabs import ElevenLabs
from app.config import settings
from app.services.chat_service import handle_chat, handle_voice_chat
from app.schemas.chat import ChatRequest
import logging
from fastapi import BackgroundTasks

logger = logging.getLogger()


async def transcribe_audio(audio_file: UploadFile) -> str:
    logger.info("🎙️ [Transcribing Audio]")

    audio_bytes = await audio_file.read()

    # Optional: save temp file for debugging
    temp_path = f"/tmp/temp_{uuid.uuid4()}.wav"
    with open(temp_path, "wb") as f:
        f.write(audio_bytes)

    audio_file_like = BytesIO(audio_bytes)
    audio_file_like.name = "audio.wav"

    groq_client = Groq(api_key=settings.Groq_key)

    stt_response = groq_client.audio.transcriptions.create(
        file=audio_file_like,
        model="whisper-large-v3-turbo",
        response_format="verbose_json",
        language="en",
        temperature=0.0
    )

    os.remove(temp_path)
    logger.info(f"📝 Transcription Result: {stt_response.text}")
    return stt_response.text


async def get_chatbot_reply(user_input: str, topic: str, db: AsyncSession, current_user, session_id: str | None = None, background_tasks: BackgroundTasks = None) -> tuple[str, str]:
    logger.info("🧠 [Getting Chatbot Reply]")

    chat_request = ChatRequest(message=user_input, topic=topic, session_id=session_id)
    chat_response = await handle_voice_chat(chat_request, db, current_user, background_tasks)

    logger.info(f"✅ Chatbot Response: {chat_response.reply[:300]}")
    return chat_response.reply, chat_response.session_id


def generate_tts_audio(text: str) -> BytesIO:
    logger.info("🔊 [Generating TTS]")

    eleven_client = ElevenLabs(api_key=settings.Eleven_key)

    tts_generator = eleven_client.text_to_speech.convert(
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        output_format="opus_48000_32",
        text=text,
        model_id="eleven_multilingual_v2"
    )

    tts_audio = b"".join(tts_generator)
    logger.info(f"🔉 TTS audio generated: {len(tts_audio)} bytes")
    return BytesIO(tts_audio)


async def process_voice_chat(
    audio_file: UploadFile,
    topic: str,
    db: AsyncSession,
    current_user,
    background_tasks: BackgroundTasks,
    session_id: str | None = None,
):
    logger.info("🎤 [Voice Chat Pipeline Start]")

    user_input = await transcribe_audio(audio_file)

    chatbot_text, new_session_id = await get_chatbot_reply(user_input, topic, db, current_user, session_id, background_tasks)

    audio_stream = generate_tts_audio(chatbot_text)

    return {
        "text": chatbot_text,
        "user_input": user_input,
        "audio_stream": audio_stream,
        "session_id": new_session_id
    }