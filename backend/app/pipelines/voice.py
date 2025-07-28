import os
import uuid
from groq import Groq
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.services.chat_service import handle_chat
from app.schemas.chat import ChatRequest
from fastapi.responses import StreamingResponse
from io import BytesIO
from elevenlabs import ElevenLabs




async def process_voice_chat(audio_file: UploadFile, topic:str, db: AsyncSession, current_user):
    audio_id = str(uuid.uuid4())
    audio_path = f"temp_{audio_id}.wav"

    client = Groq(api_key=settings.Groq_key)
    
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
    chat_request = ChatRequest(message=user_input, topic=topic)

    chat_response = await handle_chat(
        request=chat_request,
        db=db,
        current_user=current_user
    )

    chatbot_text = chat_response.reply

    client = ElevenLabs(api_key=settings.Eleven_key)

    tts_generator = client.text_to_speech.convert(
    voice_id="JBFqnCBsd6RMkjVDRZzb",     # Replace with desired voice ID
    output_format="mp3_44100_128",      
    text=chatbot_text,
    model_id="eleven_multilingual_v2"
)

    # # 4. Generate TTS audio in-memory (no saving)
    # tts_response = client.audio.speech.create(
    #     model="playai-tts",
    #     voice="Deedee-PlayAI",
    #     input=chatbot_text,
    #     response_format="wav"
    # )

    # Step 2: Join generator chunks to bytes
    tts_audio_bytes = b"".join(tts_generator)

    # Step 3: Wrap in BytesIO
    audio_stream = BytesIO(tts_audio_bytes)

    # Step 4: Return result
    return {
        "text": chatbot_text,
        "user_input": user_input,
        "audio_stream": audio_stream
    }

    # audio_bytes = tts_response.read()
    # audio_stream = BytesIO(audio_bytes)

    # # Return text + audio stream
    # return {
    #     "text": chatbot_text,
    #     "user_input": user_input,
    #     "audio_stream": audio_stream
    # }

    # 4. Text-to-Speech
    # output_audio_filename = f"output_{audio_id}.wav"

    # # Create the full path using BASE_DIR
    # audio_dir = os.path.join(settings.BASE_DIR, "app", "static", "audio")
    # os.makedirs(audio_dir, exist_ok=True)  # Ensure folder exists

    # output_audio_path = os.path.join(audio_dir, output_audio_filename)

    # # Generate TTS audio
    # tts_response = client.audio.speech.create(
    #     model="playai-tts",
    #     voice="Deedee-PlayAI",
    #     input=chatbot_text,
    #     response_format="wav"
    # )
    # tts_response.write_to_file(output_audio_path)

    # # Return relative URL to frontend
    # audio_url = f"/static/audio/{output_audio_filename}"

    # return {
    #     "text": chatbot_text,
    #     "audio_path": audio_url,
    #     "user_input": user_input
    # }