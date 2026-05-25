from typing import Optional
import enum
from app import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Integer, Numeric, DateTime, Boolean, func, Enum
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
from decimal import Decimal

class TargetGroup(enum.Enum):
    men = "men"
    women = "women"
    unisex = "unisex"
    
class Product(db.Model):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(250))
    short_description: Mapped[Optional[str]] = mapped_column(String(50))
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    thumbnail: Mapped[str] = mapped_column(String(255), nullable=False)
    tags: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String(40)))
    is_featured: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    gender: Mapped[TargetGroup] = mapped_column(Enum(TargetGroup, native_enum=True), nullable=False)
    base_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    brand_id: Mapped[int] = mapped_column(Integer, ForeignKey("brands.id"), nullable=False, index=True)
    
    variants: Mapped[list["ProductVariant"]] = relationship("ProductVariant", back_populates="product")
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    brand: Mapped["Brand"] = relationship("Brand", back_populates="products")
    
class ProductVariant(db.Model):
    __tablename__ = "product_variants"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    variant_price:Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    color_id:Mapped[int] = mapped_column(Integer, ForeignKey("product_colors.id"), nullable=False)
    material_id:Mapped[int] = mapped_column(Integer, ForeignKey("product_materials.id"), nullable=False)
    size_id:Mapped[int] = mapped_column(Integer, ForeignKey("product_sizes.id"), nullable=False)
    
    product: Mapped["Product"] = relationship("Product", back_populates="variants")
    size: Mapped["ProductSize"] = relationship("ProductSize", back_populates="variants")
    color: Mapped["ProductColor"] = relationship("ProductColor", back_populates="variants")
    material: Mapped["ProductMaterial"] = relationship("ProductMaterial", back_populates="variants")
    images: Mapped[list["ProductImage"]] = relationship("ProductImage", back_populates="variant")
    
class ProductSize(db.Model):
    __tablename__ = "product_sizes"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    
    variants: Mapped[list["ProductVariant"]] = relationship("ProductVariant", back_populates="size")

class ProductColor(db.Model):
    __tablename__ = "product_colors"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    hex_code: Mapped[str] = mapped_column(String(7), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    
    variants: Mapped[list["ProductVariant"]] = relationship("ProductVariant", back_populates="color")
    
class ProductMaterial(db.Model):
    __tablename__ = "product_materials"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    
    variants: Mapped[list["ProductVariant"]] = relationship("ProductVariant", back_populates="material")
    
class ProductImage(db.Model):
    __tablename__ = "product_images"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    alt_text: Mapped[str] = mapped_column(String(100), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    variant_id: Mapped[int] = mapped_column(Integer, ForeignKey("product_variants.id"), nullable=False)
    
    variant: Mapped[Optional["ProductVariant"]] = relationship("ProductVariant", back_populates="images")
    
class Category(db.Model):
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    parent_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    
    parent: Mapped[Optional["Category"]] = relationship("Category", remote_side=[id], back_populates="children")
    children: Mapped[list["Category"]] = relationship("Category", back_populates="parent")
    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")

class Brand(db.Model):
    __tablename__ = "brands"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    products: Mapped[list["Product"]] = relationship("Product", back_populates="brand")