from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import OrderStatus
from app.services.orders import get_order_by_id


async def handle_payment_success(event_data, db: AsyncSession):
    user_id = int(event_data.get("metadata", {}).get("user_id"))
    order_id = int(event_data.get("metadata", {}).get("order_id"))

    if order_id and user_id:
        order = await get_order_by_id(order_id, user_id, db)
        if order:
            order.status = OrderStatus.paid
            await db.commit()


async def handle_payment_failure(event_data, db: AsyncSession):
    user_id = int(event_data.get("metadata", {}).get("user_id"))
    order_id = int(event_data.get("metadata", {}).get("order_id"))
    if order_id and user_id:
        order = await get_order_by_id(order_id, user_id, db)
        if order:
            order.status = OrderStatus.failed
            await db.commit()


async def handle_payment_cancelation(event_data, db: AsyncSession):
    user_id = int(event_data.get("metadata", {}).get("user_id"))
    order_id = int(event_data.get("metadata", {}).get("order_id"))

    if order_id and user_id:
        order = await get_order_by_id(order_id, user_id, db)
        if order:
            order.status = OrderStatus.canceled
            await db.commit()


async def handle_payment_creation(event_data, db: AsyncSession):
    user_id = int(event_data.get("metadata", {}).get("user_id"))
    order_id = int(event_data.get("metadata", {}).get("order_id"))

    if order_id and user_id:
        order = await get_order_by_id(order_id, user_id, db)
        if order:
            order.status = OrderStatus.created
            await db.commit()


async def handle_payment_processing(event_data, db: AsyncSession):
    user_id = int(event_data.get("metadata", {}).get("user_id"))
    order_id = int(event_data.get("metadata", {}).get("order_id"))

    if order_id and user_id:
        order = await get_order_by_id(order_id, user_id, db)
        if order:
            order.status = OrderStatus.processing
            await db.commit()
