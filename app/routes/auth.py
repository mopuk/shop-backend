import jwt

from app.config import config
from jwt.exceptions import InvalidKeyTypeError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from app.models import UserModel
from app.schemas import UserSchema
from app.schemas.user import TokenData
from app.database import get_db
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from pwdlib import PasswordHash
from app.security import password_hash, DUMMY_HASH


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

router = APIRouter(
    prefix="/auth"
    tags=["auth"]
)

async def get_user(user_id, db: AsyncSession):
    stmt = select(UserModel).where(UserModel.id == user_id)
    result = await db.execute(stmt)
    
    return result.scalar_one_or_none()


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(get_db)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authencate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except InvalidKeyTypeError:
        raise credentials_exception
    
    smtm = select(UserModel).where(UserModel.id == user_id)
    result = await db.execute(smtm)
    user = result.scalar_one_or_none()
    
    if not user:
        return HTTPException(404, "User not found")
    return user
    
async def get_current_active_user(current_user: Annotated[UserModel, Depends(get_current_user)]):
    if not current_user.is_active:
        return HTTPException(status_code=400, detail="Inactive user")
    return current_user

@router.get("/me", response_model=UserSchema)
async def get_me(current_user: Annotated[UserModel, Depends(get_current_active_user)]):
    return current_user