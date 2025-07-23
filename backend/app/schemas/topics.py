# schemas/topics.py

from pydantic import BaseModel

class TopicCreate(BaseModel):
    user_id: int
    topic: str
