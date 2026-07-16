from typing import Optional, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Integer, Numeric, DateTime, func, Enum, FetchedValue
from datetime import datetime
from decimal import Decimal

from app.database import Base
from app.enums import OrderStatus

if TYPE_CHECKING:
    from app.models.user import UserModel
    from app.models.order import OrderItemModel
    from app.models.product import ProductModel

class OrderModel(Base):
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    order_number: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus, native_enum=True), nullable=False, default=OrderStatus.pending)
    
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    shipping_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    grand_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=FetchedValue())
    
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="orders")
    items: Mapped[list["OrderItemModel"]] = relationship("OrderItemModel", back_populates="order", cascade="all, delete-orphan")
    
class OrderItemModel(Base):
    __tablename__ = "order_items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    product_name: Mapped[str] = mapped_column(String(128), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_paid: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    order: Mapped["OrderModel"] = relationship("OrderModel", back_populates="items")
    product: Mapped["ProductModel"] = relationship("ProductModel")