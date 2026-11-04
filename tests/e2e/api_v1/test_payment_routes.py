from types import SimpleNamespace
from unittest.mock import ANY, AsyncMock, Mock

import pytest
from httpx import AsyncClient

from app.enums import OrderStatus
from app.models.order import OrderModel
from app.routes import payments as payment_routes


@pytest.fixture
async def order(db_session, active_user):
    value = OrderModel(
        user_id=active_user.id,
        status=OrderStatus.created,
        subtotal=20,
        total=25.99,
        shipping_total=5.99,
        grand_total=25.99,
    )
    db_session.add(value)
    await db_session.flush()
    return value


@pytest.mark.anyio
async def test_create_payment_intent(
    async_client: AsyncClient, authenticated_headers, order, monkeypatch
):
    create_intent = AsyncMock(
        return_value=SimpleNamespace(
            id="pi_test", client_secret="pi_test_secret"
        )
    )
    monkeypatch.setattr(
        payment_routes.client.v1.payment_intents, "create_async", create_intent
    )

    response = await async_client.post(
        f"/api/v1/payment/create-intent/{order.order_number}",
        headers=authenticated_headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "client_secret": "pi_test_secret",
        "order_id": order.id,
    }
    create_intent.assert_awaited_once()
    assert create_intent.await_args.args[0]["amount"] == 2599
    assert create_intent.await_args.args[0]["metadata"]["order_id"] == str(order.id)


@pytest.mark.anyio
async def test_create_payment_intent_reuses_existing_nonterminal_intent(
    async_client: AsyncClient, authenticated_headers, order, db_session, monkeypatch
):
    order.stripe_payment_intent_id = "pi_existing"
    await db_session.commit()
    existing_intent = SimpleNamespace(
        status="requires_action", client_secret="existing_secret"
    )
    retrieve_intent = Mock(return_value=existing_intent)
    create_intent = AsyncMock()
    monkeypatch.setattr(
        payment_routes.client.v1.payment_intents, "retrieve", retrieve_intent
    )
    monkeypatch.setattr(
        payment_routes.client.v1.payment_intents, "create_async", create_intent
    )

    response = await async_client.post(
        f"/api/v1/payment/create-intent/{order.order_number}",
        headers=authenticated_headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "client_secret": "existing_secret",
        "order_id": order.id,
    }
    retrieve_intent.assert_called_once_with("pi_existing")
    create_intent.assert_not_awaited()


@pytest.mark.anyio
async def test_create_payment_intent_replaces_terminal_intent(
    async_client: AsyncClient, authenticated_headers, order, db_session, monkeypatch
):
    order.stripe_payment_intent_id = "pi_canceled"
    await db_session.commit()
    monkeypatch.setattr(
        payment_routes.client.v1.payment_intents,
        "retrieve",
        Mock(return_value=SimpleNamespace(status="canceled", client_secret=None)),
    )
    create_intent = AsyncMock(
        return_value=SimpleNamespace(
            id="pi_replacement", client_secret="replacement_secret"
        )
    )
    monkeypatch.setattr(
        payment_routes.client.v1.payment_intents, "create_async", create_intent
    )

    response = await async_client.post(
        f"/api/v1/payment/create-intent/{order.order_number}",
        headers=authenticated_headers,
    )

    assert response.status_code == 200
    assert response.json()["client_secret"] == "replacement_secret"
    assert order.stripe_payment_intent_id == "pi_replacement"
    create_intent.assert_awaited_once()


@pytest.mark.anyio
async def test_create_payment_intent_rejects_missing_or_paid_order(
    async_client: AsyncClient, authenticated_headers, order, db_session
):
    missing = await async_client.post(
        "/api/v1/payment/create-intent/ORD-MISSING", headers=authenticated_headers
    )
    order.status = OrderStatus.paid
    await db_session.commit()
    paid = await async_client.post(
        f"/api/v1/payment/create-intent/{order.order_number}",
        headers=authenticated_headers,
    )

    assert missing.status_code == 404
    assert paid.status_code == 400
    assert paid.json()["detail"] == (
        "Order is not processing or created and cannot be paid for"
    )


@pytest.mark.anyio
async def test_create_payment_intent_requires_authentication(
    async_client: AsyncClient, order
):
    response = await async_client.post(
        f"/api/v1/payment/create-intent/{order.order_number}"
    )

    assert response.status_code == 401


@pytest.mark.anyio
async def test_webhook_validates_header_and_dispatches_event(
    async_client: AsyncClient, monkeypatch
):
    missing_header = await async_client.post("/api/v1/payment/webhook", content=b"{}")
    assert missing_header.status_code == 400
    assert missing_header.json()["detail"] == "Missing Stripe-Signature Header"

    event = {
        "type": "payment_intent.succeeded",
        "data": {"object": SimpleNamespace(to_dict=lambda: {"metadata": {}})},
    }
    monkeypatch.setattr(
        payment_routes.stripe.Webhook, "construct_event", lambda *_args: event
    )
    success_handler = AsyncMock()
    monkeypatch.setattr(payment_routes, "handle_payment_success", success_handler)

    response = await async_client.post(
        "/api/v1/payment/webhook",
        content=b"{}",
        headers={"Stripe-Signature": "test-signature"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "success"}
    success_handler.assert_awaited_once_with({"metadata": {}}, ANY)


@pytest.mark.anyio
async def test_webhook_returns_unhandled_event_message(
    async_client: AsyncClient, monkeypatch
):
    event = {
        "type": "customer.created",
        "data": {"object": SimpleNamespace(to_dict=lambda: {})},
    }
    monkeypatch.setattr(
        payment_routes.stripe.Webhook, "construct_event", lambda *_args: event
    )

    response = await async_client.post(
        "/api/v1/payment/webhook",
        content=b"{}",
        headers={"Stripe-Signature": "test-signature"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": 200,
        "message": "Unhandled event type: customer.created",
    }


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("event_type", "handler_name"),
    [
        ("payment_intent.payment_failed", "handle_payment_failure"),
        ("payment_intent.canceled", "handle_payment_cancelation"),
        ("payment_intent.created", "handle_payment_creation"),
    ],
)
async def test_webhook_dispatches_supported_events(
    async_client: AsyncClient,
    monkeypatch,
    event_type: str,
    handler_name: str,
):
    event = {
        "type": event_type,
        "data": {"object": SimpleNamespace(to_dict=lambda: {"metadata": {}})},
    }
    handler = AsyncMock()
    monkeypatch.setattr(
        payment_routes.stripe.Webhook, "construct_event", lambda *_args: event
    )
    monkeypatch.setattr(payment_routes, handler_name, handler)

    response = await async_client.post(
        "/api/v1/payment/webhook",
        content=b"{}",
        headers={"Stripe-Signature": "test-signature"},
    )

    assert response.status_code == 200
    handler.assert_awaited_once_with({"metadata": {}}, ANY)


@pytest.mark.anyio
async def test_webhook_rejects_invalid_signature_and_payload(
    async_client: AsyncClient, monkeypatch
):
    def reject_signature(*_args):
        raise payment_routes.stripe.SignatureVerificationError(
            "bad signature", "signature"
        )

    monkeypatch.setattr(
        payment_routes.stripe.Webhook, "construct_event", reject_signature
    )
    invalid_signature = await async_client.post(
        "/api/v1/payment/webhook",
        content=b"{}",
        headers={"Stripe-Signature": "invalid"},
    )

    def reject_payload(*_args):
        raise ValueError("invalid")

    monkeypatch.setattr(
        payment_routes.stripe.Webhook, "construct_event", reject_payload
    )
    invalid_payload = await async_client.post(
        "/api/v1/payment/webhook",
        content=b"not-json",
        headers={"Stripe-Signature": "valid"},
    )

    assert invalid_signature.status_code == 400
    assert invalid_signature.json()["detail"] == "Invalid Stripe-Signature Header"
    assert invalid_payload.status_code == 400
    assert invalid_payload.json()["detail"] == "Invalid payload"
