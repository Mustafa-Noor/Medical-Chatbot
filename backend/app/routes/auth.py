from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from sqlalchemy.future import select
import traceback

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]

)


@router.post("/register")
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(User).where(
            (User.email == user.email) | (User.username == user.username)
        )
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email or Username already registered")

        new_user = User(
            username=user.username,
            email=user.email,
            password=user.password  # hash this in production
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return UserOut.model_validate(new_user)

    except Exception as e:
        await db.rollback()
        print("ERROR:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")

