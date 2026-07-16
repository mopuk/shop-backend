
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, StringConstraints


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

tag_string = Annotated[str, StringConstraints(max_length=40)]


class ProductSchema(BaseSchema):
    id: int
    name: Annotated[str, Query(max_length=40)]
    description: Annotated[str, Query(max_length=250)] | None = None
    short_description: Annotated[str, Query(max_length=50)] | None = None
    slug: Annotated[str, Query(max_length=255)]
    thumbnail: HttpUrl
    tags: list[tag_string] | None = None
    is_featured: bool
    created_at: datetime
    gender: Literal["men", "women", "unisex"]
    base_price: Decimal = Field(max_digits=10, decimal_places=2)
    category_id: int
    brand_id: int
    variants: list["ProductVariantSchema"] = Field(default_factory=list)
    category: "CategorySchema"
    brand: "BrandSchema"


class ProductVariantSchema(BaseSchema):
    id: int
    variant_price: Decimal = Field(max_digits=10, decimal_places=2)
    stock: int
    is_available: bool
    product_id: int
    color_id: int
    material_id: int
    size_id: int
    product: "ProductSchema | None" = None
    size: "ProductSizeSchema"
    color: "ProductColorSchema"
    material: "ProductMaterialSchema"
    images: list["ProductImageSchema"] = Field(default_factory=list)


class ProductSizeSchema(BaseSchema):
    id: int
    name: Annotated[str, Query(max_length=40)]
    sort_order: int
    variants: list["ProductVariantSchema"] = Field(default_factory=list)


class ProductColorSchema(BaseSchema):
    id: int
    name: Annotated[str, Query(max_length=40)]
    hex_code: Annotated[str, Query(max_length=7)]
    slug: Annotated[str, Query(max_length=255)]
    variants: list["ProductVariantSchema"] = Field(default_factory=list)


class ProductMaterialSchema(BaseSchema):
    id: int
    name: Annotated[str, Query(max_length=40)]
    slug: Annotated[str, Query(max_length=255)]
    variants: list["ProductVariantSchema"] = Field(default_factory=list)


class ProductImageSchema(BaseSchema):
    id: int
    url: HttpUrl
    alt_text: Annotated[str, Query(max_length=100)]
    sort_order: int
    variant_id: int
    variant: "ProductVariantSchema | None" = None


class CategorySchema(BaseSchema):
    id: int
    name: Annotated[str, Query(max_length=40)]
    slug: Annotated[str, Query(max_length=255)]
    parent_id: int | None = None
    image: str | None = None
    parent: "CategorySchema | None" = None
    children: list["CategorySchema"] = Field(default_factory=list)
    products: list["ProductSchema"] = Field(default_factory=list)


class BrandSchema(BaseSchema):
    id: int
    name: Annotated[str, Query(max_length=40)]
    slug: Annotated[str, Query(max_length=255)]
    products: list["ProductSchema"] = Field(default_factory=list)
