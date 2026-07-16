import jwt

from datetime import timedelta, datetime, timezone
from app.config import config
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from app.models.user import UserModel
from app.schemas.user import TokenData, Token, UserCreate, UserResponse
from app.database import get_db
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from pydantic import EmailStr
from app.security import DUMMY_HASH, verify_password, get_password_hash, check_requirements_for_password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"],
)


async def get_user_by_id(user_id: int, db: AsyncSession):
    stmt = select(UserModel).where(UserModel.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(email: str, db: AsyncSession):
    stmt = select(UserModel).where(UserModel.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_username(username: str, db: AsyncSession):
    stmt = select(UserModel).where(UserModel.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_user(field: str | int | EmailStr, db: AsyncSession):
    if isinstance(field, str):
        if "@" in field:
            return await get_user_by_email(field, db)
        return await get_user_by_username(field, db)
    if isinstance(field, int):
        return await get_user_by_id(field, db)
    
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(get_db)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        token_data = TokenData(user_id=int(user_id_str))
    except jwt.InvalidTokenError as exc:
        raise credentials_exception from exc
    
    user = await get_user(token_data.user_id, db=db)
    
    if not user:
        raise HTTPException(404, "User not found")
    return user
    
def get_current_active_user(current_user: Annotated[UserModel, Depends(get_current_user)]):
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    return current_user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET_KEY, config.JWT_ALGORITHM)
    return encoded_jwt

async def authenticate_user(username: str, password: str, db: AsyncSession):
    user = await get_user(username, db)
    
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[AsyncSession, Depends(get_db)]):
    user = await authenticate_user(username=form_data.username, password=form_data.password, db=db)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    access_token_expires = timedelta(minutes=int(config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
 
@router.post("/register")
async def register(user_data: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    username = user_data.username
    password = user_data.password
    email = user_data.email
    if not check_requirements_for_password(password):
        raise HTTPException(
            403,
            "Password does not meet the requirements"
        )
    existing_username = await get_user(username, db)
    existing_email = await get_user(email, db)
    if existing_username:
        raise HTTPException(
            409, "Username already registered"
        )
    if existing_email:
        raise HTTPException(
            409, "Email already registered"
        )
    hashed_password = get_password_hash(password)
    
    new_user = UserModel(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_active=True,
        role="customer"
    )
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            409, "Username or email already exist"
        )
    
    access_token = create_access_token(
        data={"sub": str(new_user.id)}, 
        expires_delta=timedelta(minutes=int(config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
        )
    return Token(access_token=access_token, token_type="bearer")
    
@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Annotated[UserModel, Depends(get_current_active_user)]):
    return current_user