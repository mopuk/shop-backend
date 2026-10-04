from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models.cart import CartItemModel, CartModel
from app.models.product import ProductModel, ProductVariantModel

CART_ITEMS_OPTIONS = selectinload(CartModel.items).options(
    joinedload(CartItemModel.variant).options(
        selectinload(ProductVariantModel.images),
        joinedload(ProductVariantModel.size),
        joinedload(ProductVariantModel.color),
        joinedload(ProductVariantModel.material),
        joinedload(ProductVariantModel.product).options(
            joinedload(ProductModel.brand),
            joinedload(ProductModel.category),
        ),
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
        if cart is None:
            raise RuntimeError("Cart was not found after creation")

    return cart


async def get_variant(variant_id: int, db: AsyncSession) -> ProductVariantModel:
    variant = await db.scalar(
        select(ProductVariantModel).where(ProductVariantModel.id == variant_id)
    )

    if variant is None:
        raise HTTPException(404, "Product variant not found")

    return variant


async def get_cart_item(
    variant_id: int, cart_id: int, db: AsyncSession
) -> CartItemModel | None:
    item = await db.scalar(
        select(CartItemModel).where(
            CartItemModel.variant_id == variant_id, CartItemModel.cart_id == cart_id
        )
    )

    return item


def find_cart_item(cart: CartModel, variant_id: int) -> CartItemModel | None:
    """Removes the need for additional query, finds items in-memory"""
    return next((i for i in cart.items if i.variant_id == variant_id), None)
