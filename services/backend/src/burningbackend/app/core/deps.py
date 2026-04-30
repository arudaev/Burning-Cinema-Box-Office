from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from burningbackend.app.core.config import settings
from burningbackend.app.core.security import decode_access_token
from burningbackend.app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/{settings.API_V1_STR}/auth/token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    subject = decode_access_token(token, settings.SECRET_KEY)
    user = await User.get_by_username(username=subject) if subject else None
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_superuser(user: User = Depends(get_current_user)) -> User:
    if not user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    return user
