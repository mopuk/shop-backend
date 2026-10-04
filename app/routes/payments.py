from typing import Annotated

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import config
from app.database import get_db
from app.enums import OrderStatus
from app.models.order import OrderModel
from app.models.user import UserModel
from app.routes.auth import get_current_active_user
from app.services.payments import (
    handle_payment_cancelation,
    handle_payment_creation,
    handle_payment_failure,
    handle_payment_processing,
    handle_payment_success,
)

client = stripe.StripeClient(config.STRIPE_SECRET_KEY)

router = APIRouter(prefix="/api/v1/payment", tags=["payments"])


@router.post("/create-intent")
async def create_intent(
    order_id: int,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    order = await db.scalar(
        select(OrderModel).where(
            OrderModel.id == order_id, OrderModel.user_id == current_user.id
        )
    )

    if order is None:
        raise HTTPException(404, "Order not found")
    elif order.status != OrderStatus.processing:
        raise HTTPException(400, "Order is not processing and cannot be paid for")

    if order.stripe_payment_intent_id is not None:
        try:
            existing_intent = client.v1.payment_intents.retrieve(
                order.stripe_payment_intent_id
            )
            if existing_intent.status not in ["canceled", "succeeded"]:
                return {
                    "client_secret": existing_intent.client_secret,
                    "order_id": order.id,
                }
        except stripe.StripeError:
            pass
    try:
        payment_intent = await client.v1.payment_intents.create_async(
            {
                "amount": int(order.total * 100),
                "currency": "rub",
                "metadata": {
                    "order_id": str(order.id),
                    "user_id": str(current_user.id),
                    "order_number": order.order_number,
                },
                "automatic_payment_methods": {"enabled": True},
            }
        )
        order.stripe_payment_intent_id = payment_intent.id
        await db.commit()

    except stripe.StripeError as exc:
        raise HTTPException(502, f"Stripe gateway failure: {exc!s}")

    return {"client_secret": payment_intent.client_secret, "order_id": order.id}


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: Annotated[str | None, Depends(Header(alias="Stripe-Signature"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if not stripe_signature:
        raise HTTPException(400, "Missing Stripe-Signature Header")

    raw_payload = await request.body()
    event = None

    try:
        event = stripe.Webhook.construct_event(
            raw_payload, stripe_signature, config.STRIPE_WEBHOOK_SECRET
        )
    except stripe.SignatureVerificationError:
        raise HTTPException(400, "Invalid Stripe-Signature Header")

    except ValueError:
        raise HTTPException(400, "Invalid payload")

    event_type = event["type"]
    event_data = event["data"]["object"]

    if event_type == "payment_intent.succeeded":
        await handle_payment_success(event_data, db)
    elif event_type == "payment_intent.payment_failed":
        await handle_payment_failure(event_data, db)
    elif event_type == "payment_intent.canceled":
        await handle_payment_cancelation(event_data, db)
    elif event_type == "payment_intent.created":
        await handle_payment_creation(event_data, db)
    elif event_type == "payment_intent.processing":
        await handle_payment_processing(event_data, db)
    else:
        return {"status": 200, "message": f"Unhandled event type: {event_type}"}

    return {"status": "success"}
