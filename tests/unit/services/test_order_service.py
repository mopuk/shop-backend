import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import OrderStatus
from app.models.order import OrderItemModel, OrderModel
from app.models.user import UserModel
from app.services.orders import (
    get_order_by_id,
    get_order_by_number,
    get_orders_by_user_id,
)


@pytest.mark.anyio
async def test_order_queries_scope_by_user_and_load_items(
    db_session: AsyncSession, catalog
):
    user = UserModel(
        username="order-service-user",
        email="order-service@example.com",
        hashed_password="unused",
    )
    db_session.add(user)
    await db_session.flush()
    item_user_id = user.id
    order = OrderModel(
        user_id=item_user_id,
        status=OrderStatus.processing,
        subtotal=20,
        total=25.99,
        shipping_total=5.99,
        grand_total=25.99,
    )
    db_session.add(order)
    await db_session.flush()
    order_item = OrderItemModel(
        order_id=order.id,
        variant_id=catalog[0]["variant"].id,
        product_name="Product 0",
        quantity=1,
        price_paid=20,
    )
    db_session.add(order_item)
    await db_session.flush()

    fetched_by_id = await get_order_by_id(order.id, item_user_id, db_session)
    fetched_by_number = await get_order_by_number(
        order.order_number, item_user_id, db_session
    )
    user_orders = await get_orders_by_user_id(item_user_id, db_session)

    assert fetched_by_id.id == order.id
    assert fetched_by_number.order_number == order.order_number
    assert fetched_by_number.items[0].variant.product.slug == "product-0"
    assert [item.id for item in user_orders] == [order.id]


@pytest.mark.anyio
async def test_order_queries_reject_unknown_and_other_users(
    db_session: AsyncSession,
):
    user = UserModel(
        username="other-order-user",
        email="other-order@example.com",
        hashed_password="unused",
    )
    db_session.add(user)
    await db_session.flush()
    order = OrderModel(
        user_id=user.id,
        status=OrderStatus.processing,
        subtotal=0,
        total=5.99,
        shipping_total=5.99,
        grand_total=5.99,
    )
    db_session.add(order)
    await db_session.flush()

    for query in (
        get_order_by_id(order.id, user.id + 1, db_session),
        get_order_by_number(order.order_number, user.id + 1, db_session),
        get_order_by_id(9999, user.id, db_session),
        get_order_by_number("ORD-MISSING", user.id, db_session),
    ):
        with pytest.raises(HTTPException) as error:
            await query
        assert error.value.status_code == 404
