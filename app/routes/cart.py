from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.cart import CartItemModel
from app.models.user import UserModel
from app.routes.auth import get_current_active_user
from app.schemas.cart import CartItemCreate, CartResponse
from app.services.cart import (
    find_cart_item,
    get_cart_item,
    get_or_create_cart_with_items,
    get_variant,
)

router = APIRouter(prefix="/api/v1", tags=["carts"])


@router.get("/cart/items", response_model=CartResponse)
async def get_cart(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    cart = await get_or_create_cart_with_items(current_user.id, db)

    return cart


@router.post("/cart/items", response_model=CartResponse)
async def add_item(
    item: CartItemCreate,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if item.quantity < 1:
        raise HTTPException(422, "Quantity must be at least 1")

    variant = await get_variant(item.variant_id, db)
    cart = await get_or_create_cart_with_items(current_user.id, db)
    existing_item: CartItemModel | None = find_cart_item(cart, variant.id)

    if existing_item is None:
        new_item = CartItemModel(
            cart_id=cart.id,
            variant_id=item.variant_id,
            quantity=item.quantity,
            price_at_addition=variant.variant_price,
        )
        db.add(new_item)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            existing = await get_cart_item(item.variant_id, cart.id, db)
            if existing is None:
                raise HTTPException(
                    500, "Unexpected error resolving cart item conflict"
                )

            existing.quantity += item.quantity
            await db.commit()

    else:
        existing_item.quantity += item.quantity
        await db.commit()

    return await get_or_create_cart_with_items(current_user.id, db)


@router.patch("/cart/items", response_model=CartResponse)
async def change_item(
    item: CartItemCreate,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if item.quantity < 1:
        raise HTTPException(422, "Quantity must be at least 1")

    cart = await get_or_create_cart_with_items(current_user.id, db)
    existing_item = find_cart_item(cart, item.variant_id)

    if not existing_item:
        raise HTTPException(404, "Item not in cart")

    existing_item.quantity = item.quantity

    await db.commit()
    return await get_or_create_cart_with_items(current_user.id, db)


@router.delete("/cart/items/{variant_id}", response_model=CartResponse)
async def delete_item(
    variant_id: int,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):

    cart = await get_or_create_cart_with_items(current_user.id, db)
    existing_item = find_cart_item(cart, variant_id)

    if not existing_item:
        raise HTTPException(404, "Item not found")

    await db.delete(existing_item)
    await db.commit()
    return await get_or_create_cart_with_items(current_user.id, db)
