from decimal import Decimal

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_cart_add_update_and_remove_item(
    async_client: AsyncClient, authenticated_headers, catalog
):
    headers = authenticated_headers
    variant_id = catalog[0]["variant"].id

    empty_cart = await async_client.get("/api/v1/cart/items", headers=headers)
    assert empty_cart.status_code == 200
    assert empty_cart.json()["items"] == []

    first_add = await async_client.post(
        "/api/v1/cart/items",
        headers=headers,
        json={"variant_id": variant_id, "quantity": 2},
    )
    assert first_add.status_code == 200
    assert len(first_add.json()["items"]) == 1
    item = first_add.json()["items"][0]
    assert item["quantity"] == 2
    assert Decimal(item["price_at_addition"]) == Decimal("20.00")

    second_add = await async_client.post(
        "/api/v1/cart/items",
        headers=headers,
        json={"variant_id": variant_id, "quantity": 3},
    )
    assert second_add.status_code == 200
    assert second_add.json()["items"][0]["quantity"] == 5

    changed = await async_client.patch(
        "/api/v1/cart/items",
        headers=headers,
        json={"variant_id": variant_id, "quantity": 4},
    )
    assert changed.status_code == 200
    assert changed.json()["items"][0]["quantity"] == 4

    deleted = await async_client.delete(
        f"/api/v1/cart/items/{variant_id}", headers=headers
    )
    assert deleted.status_code == 200
    assert deleted.json()["items"] == []


@pytest.mark.anyio
async def test_cart_validates_missing_items_and_quantities(
    async_client: AsyncClient, authenticated_headers, catalog
):
    headers = authenticated_headers
    missing_variant = await async_client.post(
        "/api/v1/cart/items",
        headers=headers,
        json={"variant_id": 9999, "quantity": 1},
    )
    zero_quantity = await async_client.post(
        "/api/v1/cart/items",
        headers=headers,
        json={"variant_id": catalog[0]["variant"].id, "quantity": 0},
    )
    missing_cart_item = await async_client.patch(
        "/api/v1/cart/items",
        headers=headers,
        json={"variant_id": catalog[0]["variant"].id, "quantity": 2},
    )
    missing_delete = await async_client.delete(
        "/api/v1/cart/items/9999", headers=headers
    )

    assert missing_variant.status_code == 404
    assert zero_quantity.status_code == 422
    assert missing_cart_item.status_code == 404
    assert missing_delete.status_code == 404


@pytest.mark.anyio
async def test_cart_requires_authentication(async_client: AsyncClient):
    response = await async_client.get("/api/v1/cart/items")

    assert response.status_code == 401


@pytest.mark.anyio
async def test_create_and_list_order_from_cart(
    async_client: AsyncClient, authenticated_headers, catalog
):
    headers = authenticated_headers
    variant_id = catalog[0]["variant"].id
    await async_client.post(
        "/api/v1/cart/items",
        headers=headers,
        json={"variant_id": variant_id, "quantity": 2},
    )

    created = await async_client.post("/api/v1/orders", headers=headers)

    assert created.status_code == 200
    order = created.json()
    assert order["status"] == "created"
    assert order["subtotal"] == "40.00"
    assert order["shipping_total"] == "5.99"
    assert order["total"] == "45.99"
    assert order["grand_total"] == "45.99"
    assert order["items"][0]["product_name"] == "Product 0"
    assert order["items"][0]["quantity"] == 2
    assert order["items"][0]["price_paid"] == "20.00"

    fetched = await async_client.get(
        f"/api/v1/orders/{order['order_number']}", headers=headers
    )
    listed = await async_client.get("/api/v1/orders", headers=headers)

    assert fetched.status_code == 200
    assert fetched.json()["id"] == order["id"]
    assert listed.status_code == 200
    assert [entry["order_number"] for entry in listed.json()["orders"]] == [
        order["order_number"]
    ]


@pytest.mark.anyio
async def test_order_lookup_is_scoped_to_authenticated_user(
    async_client: AsyncClient, authenticated_headers, catalog
):
    not_found = await async_client.get(
        "/api/v1/orders/ORD-DOESNOTEXIST", headers=authenticated_headers
    )

    assert not_found.status_code == 404
    assert not_found.json()["detail"] == "Order not found"


@pytest.mark.anyio
async def test_order_delete_only_allows_processing_orders(
    async_client: AsyncClient, authenticated_headers, catalog, db_session
):
    from sqlalchemy import select

    from app.enums import OrderStatus
    from app.models.order import OrderModel

    headers = authenticated_headers
    await async_client.post(
        "/api/v1/cart/items",
        headers=headers,
        json={"variant_id": catalog[0]["variant"].id, "quantity": 1},
    )
    created = await async_client.post("/api/v1/orders", headers=headers)
    order_number = created.json()["order_number"]

    rejected = await async_client.delete(
        f"/api/v1/orders/{order_number}", headers=headers
    )
    assert rejected.status_code == 409

    order = await db_session.scalar(
        select(OrderModel).where(OrderModel.order_number == order_number)
    )
    order.status = OrderStatus.processing
    await db_session.commit()
    deleted = await async_client.delete(
        f"/api/v1/orders/{order_number}", headers=headers
    )
    assert deleted.status_code == 204
    assert deleted.content == b""
