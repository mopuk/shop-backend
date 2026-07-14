import enum
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Integer, Numeric, DateTime, Boolean, func, Enum, Text, FetchedValue, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY

from datetime import datetime
from decimal import Decimal
from app.database import Base

from app.enums import TargetGroup, Role, OrderStatus

# Correlated with products
class ProductModel(Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(250))
    short_description: Mapped[Optional[str]] = mapped_column(String(50))
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    thumbnail: Mapped[str] = mapped_column(String(255), nullable=False)
    tags: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String(40)), nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    gender: Mapped[TargetGroup] = mapped_column(Enum(TargetGroup, native_enum=True), nullable=False)
    base_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    brand_id: Mapped[int] = mapped_column(Integer, ForeignKey("brands.id"), nullable=False, index=True)
    
    variants: Mapped[list["ProductVariantModel"]] = relationship("ProductVariant", back_populates="product")
    category: Mapped["CategoryModel"] = relationship("Category", back_populates="products")
    brand: Mapped["BrandModel"] = relationship("Brand", back_populates="products")
    
class ProductVariantModel(Base):
    __tablename__ = "product_variants"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    variant_price:Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    color_id:Mapped[int] = mapped_column(Integer, ForeignKey("product_colors.id"), nullable=False)
    material_id:Mapped[int] = mapped_column(Integer, ForeignKey("product_materials.id"), nullable=False)
    size_id:Mapped[int] = mapped_column(Integer, ForeignKey("product_sizes.id"), nullable=False)
    
    product: Mapped["ProductModel"] = relationship("Product", back_populates="variants")
    size: Mapped["ProductSizeModel"] = relationship("ProductSize", back_populates="variants")
    color: Mapped["ProductColorModel"] = relationship("ProductColor", back_populates="variants")
    material: Mapped["ProductMaterialModel"] = relationship("ProductMaterial", back_populates="variants")
    images: Mapped[list["ProductImageModel"]] = relationship("ProductImage", back_populates="variant")
    
class ProductSizeModel(Base):
    __tablename__ = "product_sizes"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    
    variants: Mapped[list["ProductVariantModel"]] = relationship("ProductVariant", back_populates="size")

class ProductColorModel(Base):
    __tablename__ = "product_colors"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    hex_code: Mapped[str] = mapped_column(String(7), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    
    variants: Mapped[list["ProductVariantModel"]] = relationship("ProductVariant", back_populates="color")
    
class ProductMaterialModel(Base):
    __tablename__ = "product_materials"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    
    variants: Mapped[list["ProductVariantModel"]] = relationship("ProductVariant", back_populates="material")
    
class ProductImageModel(Base):
    __tablename__ = "product_images"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    alt_text: Mapped[str] = mapped_column(String(100), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    variant_id: Mapped[int] = mapped_column(Integer, ForeignKey("product_variants.id"), nullable=False)
    
    variant: Mapped[Optional["ProductVariantModel"]] = relationship("ProductVariant", back_populates="images")
    
class CategoryModel(Base):
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    parent_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    image: Mapped[str] = mapped_column(Text, nullable=True)
    
    parent: Mapped[Optional["CategoryModel"]] = relationship("Category", remote_side=[id], back_populates="children")
    children: Mapped[list["CategoryModel"]] = relationship("Category", back_populates="parent")
    products: Mapped[list["ProductModel"]] = relationship("Product", back_populates="category")

class BrandModel(Base):
    __tablename__ = "brands"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    products: Mapped[list["ProductModel"]] = relationship("Product", back_populates="brand")
    
# User
class UserModel(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    role: Mapped[Role] = mapped_column(Enum(Role, native_enum=True), nullable=False, default=Role.customer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    
    cart: Mapped[Optional["CartModel"]] = relationship("Cart", back_populates="user", uselist=False, cascade="all, delete-orphan")
    orders: Mapped[list["OrderModel"]] = relationship("Order", back_populates="user")

# Correlated with carts
class CartModel(Base):
    __tablename__ = "carts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=FetchedValue())
    
    user: Mapped["UserModel"] = relationship("User", back_populates="cart")
    items: Mapped[list["CartItemModel"]] = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    
class CartItemModel(Base):
    __tablename__ = "cart_items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    cart_id: Mapped[int] = mapped_column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    price_at_addition: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    cart: Mapped["CartModel"] = relationship("Cart", back_populates="items")
    product: Mapped["ProductModel"] = relationship("Product")
    
    __table_args__ = (
        UniqueConstraint('cart_id', 'slug', name='uq_cart_item_slug'),
    )
    

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
    
    user: Mapped["UserModel"] = relationship("User", back_populates="orders")
    items: Mapped[list["OrderItemModel"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
class OrderItemModel(Base):
    __tablename__ = "order_items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    product_name: Mapped[str] = mapped_column(String(128), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_paid: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    order: Mapped["OrderModel"] = relationship("Order", back_populates="items")
    product: Mapped["ProductModel"] = relationship("Product")