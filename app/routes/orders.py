from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from decimal import Decimal

from app.database import get_db
from app.routes.auth import get_current_active_user
from app.routes.cart import CART_ITEMS_OPTIONS
from app.models.user import UserModel
from app.models.order import OrderModel, OrderItemModel
from app.models.cart import CartModel, CartItemModel
from app.models.product import ProductVariantModel
from app.schemas.order import OrderSchema, OrderListSchema
from app.enums import OrderStatus

router = APIRouter(
    prefix="/api/v1",
    tags=["orders"]
)

SHIPPING_FLAT_RATE = Decimal("5.99")

   
@router.get("/orders/{order_id}", response_model=OrderSchema)
async def get_order(
    order_id: int, 
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    order = await db.scalar(
        select(OrderModel)
        .where(OrderModel.id == order_id, OrderModel.user_id == current_user.id)
        .options(
            selectinload(OrderModel.items).options(
                selectinload(OrderItemModel.variant)
            )
        )
    )
    
    if order is None:
        raise HTTPException(404, "Order not found")
    
    return order

@router.get("/orders", response_model=OrderListSchema)
async def get_orders(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    orders = await db.scalars(
        select(OrderModel)
        .where(OrderModel.user_id == current_user.id)
    )
    
    return {
        "orders": orders.all()
    }
 
@router.post("/orders", response_model=OrderSchema)
async def create_order(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    cart_items = (await db.scalars(
        select(CartItemModel)
        .join(CartModel)
        .where(CartModel.user_id == current_user.id)
        .options(
            selectinload(CartItemModel.variant).options(
                joinedload(ProductVariantModel.product)
            )
        )
        )).all()
    
    subtotal = sum(item.price_at_addition * item.quantity for item in cart_items)
    shipping_total = SHIPPING_FLAT_RATE
    total = subtotal + shipping_total
    grand_total = total
        
    new_order = OrderModel(
        user_id=current_user.id,
        status=OrderStatus.pending,
        subtotal=subtotal,
        total=total,
        shipping_total=shipping_total,
        grand_total=grand_total
    )
    
    db.add(new_order)
    await db.flush()
    
    for item in cart_items:
        order_item = OrderItemModel(
            order_id=new_order.id,
            variant_id=item.variant_id,
            product_name=item.variant.product.name,
            quantity=item.quantity,
            price_paid=item.price_at_addition,        
        )
        db.add(order_item)
    
    await db.commit()
    
    order_with_items = await db.scalar(
        select(OrderModel)
        .where(OrderModel.id == new_order.id)
        .options(
            selectinload(OrderModel.items).options(
                joinedload(OrderItemModel.variant).options(
                    selectinload(ProductVariantModel.images),
                    joinedload(ProductVariantModel.product)
                )
            )
        )
    )
    return order_with_items
