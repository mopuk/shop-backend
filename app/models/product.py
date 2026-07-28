from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.enums import TargetGroup


class ProductModel(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(String(250))
    short_description: Mapped[str | None] = mapped_column(String(50))
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    thumbnail: Mapped[str] = mapped_column(String(255), nullable=False)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String(40)), nullable=True)
    is_featured: Mapped[bool] = mapped_column(nullable=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    gender: Mapped[TargetGroup] = mapped_column(Enum(TargetGroup, native_enum=True), nullable=False)
    base_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False, index=True)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id"), nullable=False, index=True)

    variants: Mapped[list["ProductVariantModel"]] = relationship("ProductVariantModel", back_populates="product")
    category: Mapped["CategoryModel"] = relationship("CategoryModel", back_populates="products")
    brand: Mapped["BrandModel"] = relationship("BrandModel", back_populates="products")

class ProductVariantModel(Base):
    __tablename__ = "product_variants"

    id: Mapped[int] = mapped_column(primary_key=True)
    variant_price:Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    is_available: Mapped[bool] = mapped_column(nullable=False, server_default="false")
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    color_id:Mapped[int] = mapped_column(Integer, ForeignKey("product_colors.id"), nullable=False)
    material_id:Mapped[int] = mapped_column(Integer, ForeignKey("product_materials.id"), nullable=False)
    size_id:Mapped[int] = mapped_column(Integer, ForeignKey("product_sizes.id"), nullable=False)
    thumbnail: Mapped[str | None] = mapped_column(String(255), nullable=True)

    size: Mapped["ProductSizeModel"] = relationship("ProductSizeModel", back_populates="variants")
    color: Mapped["ProductColorModel"] = relationship("ProductColorModel", back_populates="variants")
    material: Mapped["ProductMaterialModel"] = relationship("ProductMaterialModel", back_populates="variants")
    product: Mapped["ProductModel"] = relationship("ProductModel", back_populates="variants")
    images: Mapped[list["ProductImageModel"]] = relationship("ProductImageModel", back_populates="variant")

class ProductImageModel(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    alt_text: Mapped[str] = mapped_column(String(100), nullable=False)
    sort_order: Mapped[int] = mapped_column(nullable=False)
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variants.id"), nullable=False)

    variant: Mapped[Optional["ProductVariantModel"]] = relationship("ProductVariantModel", back_populates="images")


class ProductSizeModel(Base):
    __tablename__ = "product_sizes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    variants: Mapped[list["ProductVariantModel"]] = relationship("ProductVariantModel", back_populates="size")

class ProductColorModel(Base):
    __tablename__ = "product_colors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    hex_code: Mapped[str] = mapped_column(String(7), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    variants: Mapped[list["ProductVariantModel"]] = relationship("ProductVariantModel", back_populates="color")

class ProductMaterialModel(Base):
    __tablename__ = "product_materials"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    variants: Mapped[list["ProductVariantModel"]] = relationship("ProductVariantModel", back_populates="material")

class CategoryModel(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=True, index=True)
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)

    parent: Mapped[Optional["CategoryModel"]] = relationship("CategoryModel", remote_side=[id], back_populates="children")
    children: Mapped[list["CategoryModel"]] = relationship("CategoryModel", back_populates="parent")
    products: Mapped[list["ProductModel"]] = relationship("ProductModel", back_populates="category")

class BrandModel(Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    products: Mapped[list["ProductModel"]] = relationship("ProductModel", back_populates="brand")
