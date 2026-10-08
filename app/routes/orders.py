from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.database import get_db
from app.enums import OrderStatus
from app.models.cart import CartItemModel, CartModel
from app.models.order import OrderItemModel, OrderModel
from app.models.product import ProductVariantModel
from app.models.user import UserModel
from app.routes.auth import get_current_active_user
from app.schemas.order import OrderListSchema, OrderSchema
from app.services.orders import get_order_by_number, get_orders_by_user_id

router = APIRouter(prefix="/api/v1", tags=["orders"])

SHIPPING_FLAT_RATE = Decimal("5.99")


@router.get("/orders/{order_number}", response_model=OrderSchema)
async def get_order(
    order_number: str,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await get_order_by_number(order_number, current_user.id, db)


@router.get("/orders", response_model=OrderListSchema)
async def get_orders(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    orders = await get_orders_by_user_id(current_user.id, db)

    return {"orders": orders}


@router.post("/orders", response_model=OrderSchema)
async def create_order(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    cart_items = (
        await db.scalars(
            select(CartItemModel)
            .join(CartModel)
            .where(CartModel.user_id == current_user.id)
            .options(
                selectinload(CartItemModel.variant).options(
                    joinedload(ProductVariantModel.product)
                )
            )
        )
    ).all()

    subtotal = sum(item.price_at_addition * item.quantity for item in cart_items)
    shipping_total = SHIPPING_FLAT_RATE
    total = subtotal + shipping_total
    grand_total = total

    new_order = OrderModel(
        user_id=current_user.id,
        status=OrderStatus.processing,
        subtotal=subtotal,
        total=total,
        shipping_total=shipping_total,
        grand_total=grand_total,
    )

    db.add(new_order)
    await db.flush()

    for item in cart_items:
        order_item = OrderItemModel(
            order_id=new_order.id,
            variant_id=item.variant_id,
            product_name=item.variant.product.name,
            quantity=item.quantity,
            price_paid=item.price_at_addition,
        )
        db.add(order_item)

    await db.commit()

    order_with_items = await db.scalar(
        select(OrderModel)
        .where(OrderModel.id == new_order.id)
        .options(
            selectinload(OrderModel.items).options(
                joinedload(OrderItemModel.variant).options(
                    selectinload(ProductVariantModel.images),
                    joinedload(ProductVariantModel.product),
                )
            )
        )
    )
    return order_with_items


@router.delete("/orders/{order_number}", status_code=204)
async def delete_order(
    order_number: str,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user_id = current_user.id
    order = await get_order_by_number(order_number, user_id, db)

    if order.status != OrderStatus.processing:
        raise HTTPException(409, "Only processing orders can be deleted")

    await db.delete(order)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(500, "Unexpected error resolving order deletion conflict")
