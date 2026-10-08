from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import OrderStatus
from app.services.orders import get_order_by_id


def _extract_order_and_user_ids(event_data: dict) -> tuple[int | None, int | None]:
    metadata = event_data.get("metadata", {})
    raw_order_id = metadata.get("order_id")
    raw_user_id = metadata.get("user_id")

    if not raw_order_id or not raw_user_id:
        print(f"Webhook event missing metadata keys. metadata={metadata}")
        return None, None

    try:
        return int(raw_order_id), int(raw_user_id)
    except (ValueError, TypeError) as exc:
        print(f"Failed to cast metadata IDs: {exc}")
        return None, None


async def handle_payment_success(event_data: dict, db: AsyncSession):
    order_id, user_id = _extract_order_and_user_ids(event_data)
    if not order_id or not user_id:
        return

    order = await get_order_by_id(order_id, user_id, db)
    if order:
        order.status = OrderStatus.paid
        await db.commit()


async def handle_payment_failure(event_data: dict, db: AsyncSession):
    order_id, user_id = _extract_order_and_user_ids(event_data)
    if not order_id or not user_id:
        return

    order = await get_order_by_id(order_id, user_id, db)
    if order:
        order.status = OrderStatus.failed
        await db.commit()


async def handle_payment_cancelation(event_data: dict, db: AsyncSession):
    order_id, user_id = _extract_order_and_user_ids(event_data)
    if not order_id or not user_id:
        return

    order = await get_order_by_id(order_id, user_id, db)
    if order:
        order.status = OrderStatus.canceled
        await db.commit()


async def handle_payment_creation(event_data: dict, db: AsyncSession):
    order_id, user_id = _extract_order_and_user_ids(event_data)
    if not order_id or not user_id:
        return

    order = await get_order_by_id(order_id, user_id, db)
    if order:
        order.status = OrderStatus.created
        await db.commit()


async def handle_payment_processing(event_data: dict, db: AsyncSession):
    order_id, user_id = _extract_order_and_user_ids(event_data)
    if not order_id or not user_id:
        return

    order = await get_order_by_id(order_id, user_id, db)
    if order:
        order.status = OrderStatus.processing
        await db.commit()
