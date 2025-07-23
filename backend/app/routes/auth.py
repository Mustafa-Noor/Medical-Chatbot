from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.user import UserCreate, UserOut, UserLogin
from app.schemas.token_schema import TokenData
from app.schemas.password import ForgotPasswordRequest, ResetPasswordRequest
from app.models.user import User
from sqlalchemy.future import select
from app.security import hashing, jwt_token, deps
from fastapi.security import OAuth2PasswordRequestForm
from app.utils.send_email import send_reset_email
from app.config import settings
import os
from dotenv import load_dotenv

load_dotenv()


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
            password=hashing.hash_password(user.password)  # Hash the password before saving
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return UserOut.model_validate(new_user)

    except HTTPException:
        raise

    except Exception as e:
        await db.rollback()
        print("ERROR:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")



@router.post("/login")
async def login_user(request: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(User).where(User.username == request.username)
        result = await db.execute(stmt)
        db_user = result.scalar_one_or_none()

        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        if not hashing.verify_password(request.password, db_user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        #return UserOut.model_validate(db_user)
        access_token = jwt_token.create_access_token(
            data={"sub": db_user.username}
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": db_user.id
        }


    except HTTPException:
        raise

    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/me", response_model=TokenData)
async def get_current_user(current_user: TokenData = Depends(deps.get_current_user)):
    try:
        return current_user
    except HTTPException:
        raise
    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.username == request.username))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = jwt_token.create_reset_token(user.email)
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"

    await send_reset_email(user.email, reset_link)  # Make sure this is async
    return {"message": "Reset link sent to your email"}


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)
):
    payload = jwt_token.verify_reset_token(request.token)

    result = await db.execute(select(User).where(User.email == payload.get("sub")))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = hashing.hash_password(request.new_password)
    await db.commit()
    return {"message": "Password reset successful"}




