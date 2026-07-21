
from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException
from app.routes.auth import get_current_active_user
from app.models.user import UserModel
from app.models.product import ProductVariantModel
from app.models.cart import CartModel, CartItemModel
from app.schemas.cart import CartResponse, CartItemCreate
from app.database import get_db
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

router = APIRouter(
    prefix="/api/v1",
    tags=["carts"]
)

CART_ITEMS_OPTIONS = (selectinload(CartModel.items)
    .options(
        joinedload(CartItemModel.variant).options(
            selectinload(ProductVariantModel.images),
            joinedload(ProductVariantModel.product)
        )
    )
)

async def get_or_create_cart_with_items(
    user_id: int, 
    db: AsyncSession,
) -> CartModel:
    """Returnes a cart with items loaded instead of relying on db.refresh()"""
    
    cart = await db.scalar(
        select(CartModel)
        .where(CartModel.user_id == user_id)
        .options(CART_ITEMS_OPTIONS)
        .execution_options(populate_existing=True)
    )
    if cart is None:
        cart = CartModel(user_id=user_id)
        db.add(cart)
        await db.flush()
        
        cart = await db.scalar(
            select(CartModel)
            .where(CartModel.user_id == user_id)
            .options(CART_ITEMS_OPTIONS)
        )
        
    return cart

async def get_variant(variant_id: int, db: AsyncSession) -> ProductVariantModel:
    variant = await db.scalar(
        select(ProductVariantModel).where(ProductVariantModel.id == variant_id)
    )
    
    if variant is None:
        raise HTTPException(404, "Product variant not found")
    
    return variant

async def get_cart_item(variant_id: int, cart_id: int, db: AsyncSession) -> CartItemModel | None:
    item = await db.scalar(
        select(CartItemModel)
        .where(
            CartItemModel.variant_id == variant_id, 
            CartItemModel.cart_id == cart_id
        )
    )
    
    return item

def find_cart_item(cart: CartModel, variant_id: int) -> CartItemModel | None:
    """Removes the need for additional query, finds items in-memory"""
    return next((i for i in cart.items if i.variant_id == variant_id), None)
    
@router.get("/cart/items", response_model=CartResponse)
async def get_cart(
    current_user: Annotated[UserModel, Depends(get_current_active_user)], 
    db: Annotated[AsyncSession, Depends(get_db)]
):
    cart = await get_or_create_cart_with_items(current_user.id, db)
    
    return cart

@router.post("/cart/items", response_model=CartResponse)
async def add_item(
    item: CartItemCreate, 
    current_user: Annotated[UserModel, Depends(get_current_active_user)], 
    db: Annotated[AsyncSession, Depends(get_db)]
):
    if item.quantity < 1:
        raise HTTPException(422, "Quantity must be at least 1")
        
    variant = await get_variant(item.variant_id, db)
    cart = await get_or_create_cart_with_items(current_user.id, db)
    existing_item = find_cart_item(cart, variant.id)
    
    if existing_item is None:
        new_item = CartItemModel(
            cart_id=cart.id,
            variant_id=item.variant_id,
            quantity=item.quantity,
            price_at_addition=variant.variant_price
        )
        db.add(new_item)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            existing = await get_cart_item(item.variant_id, cart.id, db)
            if existing is None:
                raise HTTPException(
                    500, 
                    "Unexpected error resolving cart item conflict"
                )
            existing.quantity += item.quantity
            await db.commit()
            
    else:
        existing_item.quantity += item.quantity
    
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
    db: Annotated[AsyncSession, Depends(get_db)]
):
    
    cart = await get_or_create_cart_with_items(current_user.id, db)
    existing_item = find_cart_item(cart, variant_id)

    if not existing_item:
        raise HTTPException(404, "Item not found")

    await db.delete(existing_item)
    await db.commit()
    return await get_or_create_cart_with_items(current_user.id, db)
