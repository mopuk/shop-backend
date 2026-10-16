from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    Enum,
    FetchedValue,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.enums import OrderStatus

if TYPE_CHECKING:
    from app.models.order import OrderItemModel
    from app.models.product import ProductVariantModel
    from app.models.user import UserModel


def generate_order_number():
    return f"ORD-{uuid4().hex[:8].upper()}"

class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    order_number: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False, default=generate_order_number)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus, native_enum=True), nullable=False, default=OrderStatus.pending)

    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    shipping_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    grand_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), server_onupdate=FetchedValue())

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="orders")
<<<<<<< Updated upstream
    items: Mapped[list["OrderItemModel"]] = relationship("OrderItemModel", back_populates="order", cascade="all, delete-orphan")
=======
    items: Mapped[list["OrderItemModel"]] = relationship(
        "OrderItemModel", back_populates="order", cascade="all, delete-orphan"
    )

    def __str__(self) -> str:
        return (
            f"Order #{self.id}: {self.status}\n"
            f"items: {[f'{item!s}\n' for item in self.items]}\n"
            f"created at: {self.created_at}, updated at: {self.updated_at}"
        )

>>>>>>> Stashed changes

class OrderItemModel(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variants.id"), nullable=False)

    product_name: Mapped[str] = mapped_column(String(128), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    price_paid: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped["OrderModel"] = relationship("OrderModel", back_populates="items")
    variant: Mapped["ProductVariantModel"] = relationship("ProductVariantModel")

    def __str__(self) -> str:
        return f"Order item #{self.id}: {self.product_name}, {self.price_paid} x {self.quantity}"
