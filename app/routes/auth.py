from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import config
from app.database import get_db
from app.models.cart import CartModel
from app.models.user import UserModel
from app.schemas.user import Token, UserCreateSchema, UserResponseSchema
from app.security import check_requirements_for_password, get_password_hash
from app.services.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_user,
)

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"],
)


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user = await authenticate_user(
        username=form_data.username, password=form_data.password, db=db
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        minutes=int(config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/register")
async def register(
    user_data: UserCreateSchema, db: Annotated[AsyncSession, Depends(get_db)]
):
    username = user_data.username
    password = user_data.password
    email = user_data.email
    if not check_requirements_for_password(password):
        raise HTTPException(403, "Password does not meet the requirements")
    existing_username = await get_user(username, db)
    existing_email = await get_user(email, db)
    if existing_username:
        raise HTTPException(409, "Username already registered")
    if existing_email:
        raise HTTPException(409, "Email already registered")
    hashed_password = get_password_hash(password)

    new_user = UserModel(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_active=True,
        role="customer",
    )
    new_user.cart = CartModel()
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(409, "Username or email already exist")

    access_token = create_access_token(
        data={"sub": str(new_user.id)},
        expires_delta=timedelta(minutes=int(config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)),
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponseSchema)
async def get_me(current_user: Annotated[UserModel, Depends(get_current_active_user)]):
    return current_user
