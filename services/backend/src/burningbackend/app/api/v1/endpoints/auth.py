from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from burningbackend.app.core.config import settings
from burningbackend.app.core.deps import get_current_user
from burningbackend.app.core.security import create_access_token
from burningbackend.app.models.user import User

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


class RefreshRequest(BaseModel):
    token: str


@router.post("/token", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = await User.authenticate(username=form.username, password=form.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        subject=user.username,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        secret_key=settings.SECRET_KEY,
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/refresh", response_model=Token)
async def refresh(user: User = Depends(get_current_user)) -> Token:
    access_token = create_access_token(
        subject=user.username,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        secret_key=settings.SECRET_KEY,
    )
    return Token(access_token=access_token, token_type="bearer")
