from sqlalchemy import Column, Integer, Text, Float, Boolean, TIMESTAMP, ForeignKey, Enum, func
from app.db.database import Base
import enum

class AnswerSource(enum.Enum):
    csv = "csv"
    rag = "rag"
    llm = "llm"

class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    chat_session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    user_query = Column(Text, nullable=False)
    source = Column(Enum(AnswerSource), nullable=False)
    matched_qa_id = Column(Integer, nullable=True)
    rag_score = Column(Float, nullable=True)
    llm_answer_used = Column(Boolean, default=False)
    llm_answer_text = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
