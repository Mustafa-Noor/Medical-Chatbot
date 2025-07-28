from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime

class AnswerSource(str, Enum):
    csv = "csv"
    rag = "json"
    llm = "llm"

class ChatLogCreate(BaseModel):
    user_id: int
    chat_session_id: int
    user_query: str
    source: AnswerSource
    matched_qa_id: Optional[int] = None
    rag_score: Optional[float] = None
    llm_answer_used: Optional[bool] = False
    llm_answer_text: Optional[str] = None

class ChatLogOut(BaseModel):
    id: int
    user_id: int
    chat_session_id: int
    user_query: str
    source: AnswerSource
    matched_qa_id: Optional[int]
    rag_score: Optional[float]
    llm_answer_used: bool
    llm_answer_text: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True
