
from typing import Annotated
from fastapi import Depends, APIRouter
from app.routes.auth import get_current_active_user
from app.models.user import UserModel
from app.models.cart import CartModel, CartItemModel
from app.schemas.cart import CartResponse
from app.database import get_db
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


router = APIRouter(
    prefix="/api/v1",
    tags=["carts"]
)

@router.get("/cart", response_model=CartResponse)
async def get_cart(current_user: Annotated[UserModel, Depends(get_current_active_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    smtm = select(CartModel).where(CartModel.id == current_user.id).options(
        selectinload(CartModel.items)
    )
    cart = await db.execute(smtm)
    
    return cart