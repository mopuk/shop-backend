from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import OrderItemModel, OrderModel


async def get_order_by_id(order_id: int, user_id: int, db: AsyncSession):
    order = await db.scalar(
        select(OrderModel)
        .where(OrderModel.id == order_id, OrderModel.user_id == user_id)
        .options(
            selectinload(OrderModel.items).options(selectinload(OrderItemModel.variant))
        )
    )

    if order is None:
        raise HTTPException(404, "Order not found")

    return order


async def get_orders_by_user_id(user_id: int, db: AsyncSession):
    orders = await db.scalars(select(OrderModel).where(OrderModel.user_id == user_id))

    return orders.all()
