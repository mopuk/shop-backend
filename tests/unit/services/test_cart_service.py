import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart import CartItemModel, CartModel
from app.services.cart import (
    find_cart_item,
    get_cart_item,
    get_or_create_cart_with_items,
    get_variant,
)


@pytest.mark.anyio
async def test_get_or_create_cart_with_items(
    db_session: AsyncSession, catalog, active_user
):
    cart = await get_or_create_cart_with_items(active_user.id, db_session)
    assert cart.user_id == active_user.id
    assert cart.items == []

    item = CartItemModel(
        cart_id=cart.id,
        variant_id=catalog[0]["variant"].id,
        quantity=2,
        price_at_addition=catalog[0]["variant"].variant_price,
    )
    db_session.add(item)
    await db_session.flush()

    fetched = await get_or_create_cart_with_items(active_user.id, db_session)
    assert len(fetched.items) == 1
    assert fetched.items[0].variant_id == catalog[0]["variant"].id


@pytest.mark.anyio
async def test_get_variant_and_cart_item(
    db_session: AsyncSession, catalog, active_user
):
    cart = CartModel(user_id=active_user.id)
    db_session.add(cart)
    await db_session.flush()
    item = CartItemModel(
        cart_id=cart.id,
        variant_id=catalog[0]["variant"].id,
        quantity=1,
        price_at_addition=catalog[0]["variant"].variant_price,
    )
    db_session.add(item)
    await db_session.flush()

    assert (await get_variant(catalog[0]["variant"].id, db_session)).id == catalog[0][
        "variant"
    ].id
    assert await get_cart_item(catalog[0]["variant"].id, cart.id, db_session) is item
    assert await get_cart_item(catalog[1]["variant"].id, cart.id, db_session) is None

    with pytest.raises(HTTPException) as error:
        await get_variant(9999, db_session)
    assert error.value.status_code == 404


def test_find_cart_item_matches_variant():
    cart = CartModel(user_id=1)
    first = CartItemModel(variant_id=2, quantity=1, price_at_addition=10)
    second = CartItemModel(variant_id=3, quantity=1, price_at_addition=10)
    cart.items = [first, second]

    assert find_cart_item(cart, 3) is second
    assert find_cart_item(cart, 4) is None
