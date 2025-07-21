from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.security import jwt_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")



def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    return jwt_token.verify_token(token, credentials_exception=credentials_exception)
