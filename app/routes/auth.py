import jwt

from jwt.exceptions import InvalidKeyTypeError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from app.models import UserModel
from app.schemas import UserSchema
from app.database import get_db
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from pwdlib import PasswordHash


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("dummypassword")

router = APIRouter(
    prefix="/auth"
    tags=["auth"]
)

async def get_user(user_id, db: AsyncSession):
    stmt = select(UserModel).where(UserModel.id == user_id)
    result = await db.execute(stmt)
    
    return result.scalar_one_or_none()

async def get_current_user(current_user: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(get_db)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authencate": "Bearer"}
    )
    try:
        
    except InvalidKeyTypeError:
        raise credentials_exception
@router.get("/me"m response_model=UserSchema)
async def get_me(current_user: Annotated[UserModel, Depends(get_current_user)]):
    return current_user