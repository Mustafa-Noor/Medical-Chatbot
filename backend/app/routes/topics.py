
from fastapi import APIRouter, Depends, HTTPException
from app.security import deps
from app.utils import get_folders
import os

router = APIRouter(prefix="/topics", tags=["Topics"])

@router.get("")
def get_topics(current_user: dict = Depends(deps.get_current_user)):
    try:
        topics = get_folders.get_topic_folders()
        return topics
    except Exception as e:
        return {"error": str(e)}


#this is making me changes just 


# # ✅ POST: save selected topic for a user
# @router.post("/user/topic")
# async def save_user_topic(selection: TopicSelection, db: AsyncSession = Depends(get_db)):
#     try:
#         print("📥 Incoming topic selection:", selection.dict())

#         user_topic = UserTopic(user_id=selection.user_id, topic=selection.topic)
#         db.add(user_topic)
#         await db.commit()  # ✅ This is the fix!
#         print("✅ Topic committed to DB")

#         return {"message": "Topic saved successfully"}
#     except Exception as e:
#         await db.rollback()  # ✅ Make this async too
#         print("❌ DB error:", e)
#         raise HTTPException(status_code=500, detail="Failed to save topic")



