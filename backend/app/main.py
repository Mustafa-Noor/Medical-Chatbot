import os
os.environ["TRANSFORMERS_CACHE"] = "/tmp/huggingface"
os.environ["HF_HOME"] = "/tmp/huggingface"

from fastapi import FastAPI
from .routes import auth
from .database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, chat, topics, voice
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

app = FastAPI()

# origins = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
#     "https://medical-chatbot-cyan.vercel.app",  # Add your deployed frontend here
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         # Allow all origins
    allow_credentials=True,      # Allow cookies, authorization headers, etc.
    allow_methods=["*"],         # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],         # Allow all headers
)


app.include_router(topics.router)
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(voice.router)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Hybrid Medical Chatbot API!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
