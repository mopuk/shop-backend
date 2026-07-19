from sqlalchemy import Integer, String, DateTime, ForeignKey, Numeric, func, FetchedValue, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from decimal import Decimal
from app.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import UserModel
    from app.models.product import ProductModel

class CartModel(Base):
    __tablename__ = "carts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), server_onupdate=FetchedValue())
    
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="cart")
    items: Mapped[list["CartItemModel"]] = relationship("CartItemModel", back_populates="cart", cascade="all, delete-orphan")
    
class CartItemModel(Base):
    __tablename__ = "cart_items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id"), nullable=False)
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variants.id"), nullable=False)
    
    quantity: Mapped[int] = mapped_column(nullable=False, default=1)
    price_at_addition: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    cart: Mapped["CartModel"] = relationship("CartModel", back_populates="items")
    variant: Mapped["ProductModel"] = relationship("ProductVariantModel")
    
    __table_args__ = (
        UniqueConstraint('cart_id', 'variant_id', name='uq_cart_item'),
    )