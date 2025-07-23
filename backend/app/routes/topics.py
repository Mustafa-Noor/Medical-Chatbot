
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
import logging

from app.database import get_db
from app.models.topics import UserTopic  # ✅ your DB model
from app.config import settings  # Optional if using env for path

router = APIRouter(prefix="/topics", tags=["Topics"])
logger = logging.getLogger("uvicorn")


# ✅ Pydantic model for topic submission
class TopicSelection(BaseModel):
    user_id: int
    topic: str


# ✅ GET: fetch all folder-based topics
@router.get("/")
def get_topics():
    embeddings_dir = r"C:\\Users\\DXB\\Documents\\Medical-chatbot\\Medical-Chatbot\\data\\embeddings"

    try:
        topics = [
            {
                "value": folder,
                "label": folder.replace("__", ": ").replace("_", " ")
            }
            for folder in os.listdir(embeddings_dir)
            if os.path.isdir(os.path.join(embeddings_dir, folder))
        ]
        topics.sort(key=lambda x: x["label"])
        return topics
    except Exception as e:
        logger.error(f"Error loading topics: {e}")
        return {"error": str(e)}


# ✅ POST: save selected topic for a user
@router.post("/user/topic")
async def save_user_topic(selection: TopicSelection, db: AsyncSession = Depends(get_db)):
    try:
        print("📥 Incoming topic selection:", selection.dict())

        user_topic = UserTopic(user_id=selection.user_id, topic=selection.topic)
        db.add(user_topic)
        await db.commit()  # ✅ This is the fix!
        print("✅ Topic committed to DB")

        return {"message": "Topic saved successfully"}
    except Exception as e:
        await db.rollback()  # ✅ Make this async too
        print("❌ DB error:", e)
        raise HTTPException(status_code=500, detail="Failed to save topic")



