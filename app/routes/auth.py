from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from app.schemes import User
from sqlalchemy.orm import Session
from app.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

router = APIRouter(
    prefix="/auth"
    tags=["auth"]
)

async def get_current_user(current_user: Annotated[str, Depends(oauth2_scheme)], db: Annotated[Session, Depends(get_db)]):
    
@router.get("/me")
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    