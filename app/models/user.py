from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.cart import CartModel
    from app.models.order import OrderModel

from app.database import Base
from app.enums import Role
from app.models.cart import CartModel
from app.models.order import OrderModel


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    role: Mapped[Role] = mapped_column(Enum(Role, native_enum=True, name="user_role_enum"), nullable=False, default=Role.customer)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    cart: Mapped[Optional["CartModel"]] = relationship("CartModel", back_populates="user", uselist=False, cascade="all, delete-orphan")
    orders: Mapped[list["OrderModel"]] = relationship("OrderModel", back_populates="user")
