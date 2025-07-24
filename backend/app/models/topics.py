# from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, func
# from sqlalchemy.orm import relationship
# from app.database import Base

# # class UserTopic(Base):
# #     __tablename__ = "user_topics"

# #     id = Column(Integer, primary_key=True, index=True)
# #     user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
# #     topic = Column(String, nullable=False)

#     # Optional: define relationship if needed later
#     # user = relationship("User", back_populates="topics")

# class Topic(Base):
#     __tablename__ = "topics"

#     id = Column(Integer, primary_key=True)
#     name = Column(String(255), nullable=False, unique=True)
#     created_at = Column(TIMESTAMP, server_default=func.now())

