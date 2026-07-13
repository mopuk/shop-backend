from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, StringConstraints


class BaseScheme(BaseModel):
    model_config = ConfigDict(from_attributes=True)


tag_string = Annotated[str, StringConstraints(max_length=40)]


class ProductScheme(BaseScheme):
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
    variants: list["ProductVariantScheme"] = Field(default_factory=list)
    category: "CategoryScheme"
    brand: "BrandScheme"


class ProductVariantScheme(BaseScheme):
    id: int
    variant_price: Decimal = Field(max_digits=10, decimal_places=2)
    stock: int
    is_available: bool
    product_id: int
    color_id: int
    material_id: int
    size_id: int
    product: "ProductScheme | None" = None
    size: "ProductSizeScheme"
    color: "ProductColorScheme"
    material: "ProductMaterialScheme"
    images: list["ProductImageScheme"] = Field(default_factory=list)


class ProductSizeScheme(BaseScheme):
    id: int
    name: Annotated[str, Query(max_length=40)]
    sort_order: int
    variants: list["ProductVariantScheme"] = Field(default_factory=list)


class ProductColorScheme(BaseScheme):
    id: int
    name: Annotated[str, Query(max_length=40)]
    hex_code: Annotated[str, Query(max_length=7)]
    slug: Annotated[str, Query(max_length=255)]
    variants: list["ProductVariantScheme"] = Field(default_factory=list)


class ProductMaterialScheme(BaseScheme):
    id: int
    name: Annotated[str, Query(max_length=40)]
    slug: Annotated[str, Query(max_length=255)]
    variants: list["ProductVariantScheme"] = Field(default_factory=list)


class ProductImageScheme(BaseScheme):
    id: int
    url: HttpUrl
    alt_text: Annotated[str, Query(max_length=100)]
    sort_order: int
    variant_id: int
    variant: "ProductVariantScheme | None" = None


class CategoryScheme(BaseScheme):
    id: int
    name: Annotated[str, Query(max_length=40)]
    slug: Annotated[str, Query(max_length=255)]
    parent_id: int | None = None
    image: str | None = None
    parent: "CategoryScheme | None" = None
    children: list["CategoryScheme"] = Field(default_factory=list)
    products: list["ProductScheme"] = Field(default_factory=list)


class BrandScheme(BaseScheme):
    id: int
    name: Annotated[str, Query(max_length=40)]
    slug: Annotated[str, Query(max_length=255)]
    products: list["ProductScheme"] = Field(default_factory=list)
