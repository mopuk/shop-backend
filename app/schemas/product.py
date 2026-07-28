
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.enums import TargetGroup


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

tag_string = Annotated[str, StringConstraints(max_length=40)]


class ProductSchema(BaseSchema):
    id: int
    name: Annotated[str, Query(max_length=40)]
    description: Annotated[str, Query(max_length=250)] | None = None
    short_description: Annotated[str, Query(max_length=50)] | None = None
    slug: Annotated[str, Query(max_length=255)]
    thumbnail: str
    tags: list[tag_string] | None = None
    is_featured: bool
    created_at: datetime
    gender: TargetGroup
    base_price: Decimal = Field(max_digits=10, decimal_places=2)
    variants: list["ProductVariantNestedSchema"] = Field(default_factory=list)
    category: "CategorySummarySchema"
    brand: "BrandSchema"


class ProductVariantSchema(BaseSchema):
    """Used for /products to include product"""
    id: int
    variant_price: Decimal = Field(max_digits=10, decimal_places=2)
    stock: int
    is_available: bool
    product: "ProductSummarySchema | None" = None
    size: "ProductSizeSchema"
    color: "ProductColorSchema"
    material: "ProductMaterialSchema"
    images: list["ProductImageSchema"] = Field(default_factory=list)

class ProductVariantNestedSchema(BaseSchema):
    """Used when nested inside ProductSchema, does not include product"""
    id: int
    variant_price: Decimal = Field(max_digits=10, decimal_places=2)
    stock: int
    is_available: bool
    size: "ProductSizeSchema"
    color: "ProductColorSchema"
    material: "ProductMaterialSchema"
    images: list["ProductImageSchema"] = Field(default_factory=list)

class ProductSummarySchema(BaseSchema):
    """Used inside ProductVariant"""
    id: int
    name: str
    slug: str
    thumbnail: str
    brand: "BrandSchema"
    category: "CategorySummarySchema"
class CategorySummarySchema(BaseSchema):
    """Used inside ProductVariant"""
    id: int
    name: str
    slug: str

class ProductSizeSchema(BaseSchema):
    id: int
    name: Annotated[str, Query(max_length=40)]
    sort_order: int

class ProductColorSchema(BaseSchema):
    id: int
    name: Annotated[str, Query(max_length=40)]
    hex_code: Annotated[str, Query(max_length=7)]
    slug: Annotated[str, Query(max_length=255)]

class ProductMaterialSchema(BaseSchema):
    id: int
    name: Annotated[str, Query(max_length=40)]
    slug: Annotated[str, Query(max_length=255)]

class ProductImageSchema(BaseSchema):
    id: int
    url: str
    alt_text: Annotated[str, Query(max_length=100)]
    sort_order: int
    variant_id: int

class CategorySchema(BaseSchema):
    id: int
    name: Annotated[str, Query(max_length=40)]
    slug: Annotated[str, Query(max_length=255)]
    parent_id: int | None = None
    image_url: str | None = None
    parent: "CategorySchema | None" = None
    children: list["CategorySchema"] = Field(default_factory=list)

class BrandSchema(BaseSchema):
    id: int
    name: Annotated[str, Query(max_length=40)]
    slug: Annotated[str, Query(max_length=255)]

class ProductVariantListResponse(BaseSchema):
    variants: list[ProductVariantSchema]

class CategoryListResponse(BaseSchema):
    categories: list[CategorySummarySchema]

class BrandListResponse(BaseSchema):
    brands: list[BrandSchema]

class FiltersListResponse(BaseSchema):
    sizes: list[ProductSizeSchema]
    materials: list[ProductMaterialSchema]
    colors: list[ProductColorSchema]
