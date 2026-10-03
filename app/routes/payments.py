from typing import Annotated

import stripe
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import config
from app.database import get_db
from app.enums import OrderStatus
from app.models.order import OrderModel
from app.models.user import UserModel
from app.routes.auth import get_current_active_user

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
    elif order.status != OrderStatus.pending:
        raise HTTPException(400, "Order is not pending")

    if order.stripe_payment_intent_id is not None:
        try:
            existing_intent = client.v1.payment_intents.retrieve(
                order.stripe_payment_intent_id
            )
            if existing_intent.status not in ["canceled", "succeded"]:
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
