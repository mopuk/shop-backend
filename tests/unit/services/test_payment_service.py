import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import OrderStatus
from app.models.order import OrderModel
from app.models.user import UserModel
from app.services.payments import (
    _extract_order_and_user_ids,
    handle_payment_cancelation,
    handle_payment_creation,
    handle_payment_failure,
    handle_payment_success,
)


@pytest.mark.parametrize(
    ("metadata", "expected"),
    [
        ({"order_id": "4", "user_id": "8"}, (4, 8)),
        ({"order_id": "invalid", "user_id": "8"}, (None, None)),
        ({"order_id": "4"}, (None, None)),
        ({"order_id": None, "user_id": "8"}, (None, None)),
    ],
)
def test_extract_payment_metadata(metadata, expected):
    assert _extract_order_and_user_ids({"metadata": metadata}) == expected


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("handler", "status"),
    [
        (handle_payment_creation, OrderStatus.processing),
        (handle_payment_success, OrderStatus.paid),
        (handle_payment_failure, OrderStatus.failed),
        (handle_payment_cancelation, OrderStatus.canceled),
    ],
)
async def test_payment_event_updates_order_status(
    handler, status: OrderStatus, db_session: AsyncSession
):
    user = UserModel(
        username=f"payment-user-{status.value}",
        email=f"payment-{status.value}@example.com",
        hashed_password="unused",
    )
    db_session.add(user)
    await db_session.flush()
    order = OrderModel(
        user_id=user.id,
        status=OrderStatus.created,
        subtotal=0,
        total=5.99,
        shipping_total=5.99,
        grand_total=5.99,
    )
    db_session.add(order)
    await db_session.flush()

    await handler(
        {"metadata": {"order_id": str(order.id), "user_id": str(user.id)}},
        db_session,
    )
    await db_session.refresh(order)

    assert order.status == status


@pytest.mark.anyio
async def test_payment_event_ignores_missing_metadata(db_session: AsyncSession):
    await handle_payment_success({"metadata": {}}, db_session)
    await handle_payment_failure({}, db_session)


@pytest.mark.anyio
async def test_payment_event_rejects_order_owned_by_another_user(
    db_session: AsyncSession,
):
    user = UserModel(
        username="payment-owner",
        email="payment-owner@example.com",
        hashed_password="unused",
    )
    other_user = UserModel(
        username="payment-other",
        email="payment-other@example.com",
        hashed_password="unused",
    )
    db_session.add_all([user, other_user])
    await db_session.flush()
    order = OrderModel(
        user_id=user.id,
        status=OrderStatus.created,
        subtotal=0,
        total=5.99,
        shipping_total=5.99,
        grand_total=5.99,
    )
    db_session.add(order)
    await db_session.flush()

    with pytest.raises(HTTPException) as error:
        await handle_payment_success(
            {"metadata": {"order_id": str(order.id), "user_id": str(other_user.id)}},
            db_session,
        )

    assert error.value.status_code == 404
