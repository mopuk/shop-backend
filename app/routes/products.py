import math
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.database import get_db
from app.models.product import (
    BrandModel,
    CategoryModel,
    ProductColorModel,
    ProductMaterialModel,
    ProductModel,
    ProductSizeModel,
    ProductVariantModel,
)
from app.schemas.product import (
    BrandListResponse,
    CategoryListResponse,
    FiltersListResponse,
    ProductSchema,
    ProductVariantListResponse,
)

router = APIRouter(prefix="/api/v1", tags=["products"])

sorting_options = {
    "newest": ProductModel.created_at.desc(),
    "price_asc": ProductVariantModel.variant_price.asc(),
    "price_desc": ProductVariantModel.variant_price.desc(),
    "name_asc": ProductModel.name.asc(),
    "name_desc": ProductModel.name.desc(),
}


@router.get("/products", response_model=ProductVariantListResponse)
async def get_products(
    db: Annotated[AsyncSession, Depends(get_db)],
    featured: bool = False,
    categories: Annotated[list[str] | None, Query()] = None,
    brands: Annotated[list[str] | None, Query()] = None,
    sizes: Annotated[list[str] | None, Query()] = None,
    materials: Annotated[list[str] | None, Query()] = None,
    colors: Annotated[list[str] | None, Query()] = None,
    sort: Annotated[str, Query()] = "newest",
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    filters = []

    smtm = (
        select(ProductVariantModel)
        .join(ProductModel)
        .options(
            selectinload(ProductVariantModel.images),
            joinedload(ProductVariantModel.material),
            joinedload(ProductVariantModel.size),
            joinedload(ProductVariantModel.color),
            joinedload(ProductVariantModel.product).options(
                selectinload(ProductModel.brand), selectinload(ProductModel.category)
            ),
        )
    )

    if featured:
        filters.append(
            ProductVariantModel.product.has(ProductModel.is_featured == True)
        )

    if categories:
        filters.append(
            ProductVariantModel.product.has(
                ProductModel.category.has(CategoryModel.slug.in_(categories))
            )
        )
    if brands:
        filters.append(
            ProductVariantModel.product.has(
                ProductModel.brand.has(BrandModel.slug.in_(brands))
            )
        )
    if sizes:
        filters.append(ProductVariantModel.size.has(ProductSizeModel.name.in_(sizes)))
    if materials:
        filters.append(
            ProductVariantModel.material.has(ProductMaterialModel.slug.in_(materials))
        )
    if colors:
        filters.append(
            ProductVariantModel.color.has(ProductColorModel.slug.in_(colors))
        )

    variants = await db.scalars(
        smtm.limit(limit)
        .offset(offset)
        .where(*filters)
        .order_by(sorting_options.get(sort, ProductModel.created_at.desc()))
    )
    total_items = (
        await db.scalar(select(func.count(ProductVariantModel.id)).where(*filters)) or 0
    )
    total_pages = math.ceil(total_items / limit)
    has_next = offset + limit < total_items
    has_previous = offset > 0
    return {
        "variants": variants.unique().all(),
        "pagination": {
            "total_items": total_items,
            "total_pages": total_pages,
            "current_page": (offset // limit) + 1,
            "has_next": has_next,
            "has_previous": has_previous,
        },
    }


@router.get("/products/filters", response_model=FiltersListResponse)
async def get_filters(db: Annotated[AsyncSession, Depends(get_db)]):
    sizes = await db.scalars(
        select(ProductSizeModel)
        .join(ProductVariantModel)
        .distinct()
        .order_by(ProductSizeModel.sort_order)
    )
    colors = await db.scalars(
        select(ProductColorModel).join(ProductVariantModel).distinct()
    )
    materials = await db.scalars(
        select(ProductMaterialModel).join(ProductVariantModel).distinct()
    )
    brands = await db.scalars(select(BrandModel).join(ProductModel).distinct())
    return {
        "sizes": sizes.all(),
        "colors": colors.all(),
        "materials": materials.all(),
        "brands": brands.all(),
    }


@router.get("/products/{product_slug}", response_model=ProductSchema)
async def get_product(product_slug: str, db: Annotated[AsyncSession, Depends(get_db)]):

    try:
        smtm = (
            select(ProductModel)
            .options(
                selectinload(ProductModel.variants).options(
                    selectinload(ProductVariantModel.images),
                    joinedload(ProductVariantModel.color),
                    joinedload(ProductVariantModel.material),
                    joinedload(ProductVariantModel.size),
                ),
                selectinload(ProductModel.category),
                selectinload(ProductModel.brand),
            )
            .where(ProductModel.slug == product_slug)
        )
        result = await db.execute(smtm)
        product = result.scalar_one_or_none()
    except SQLAlchemyError:
        raise HTTPException(500, "Error in the database")
    if not product:
        raise HTTPException(404, f"Product with slug: {product_slug} is not found")

    return product


@router.get("/categories", response_model=CategoryListResponse)
async def get_categories(db: Annotated[AsyncSession, Depends(get_db)]):

    categories = await db.execute(select(CategoryModel))

    return {"categories": categories.scalars().all()}


@router.get("/brands", response_model=BrandListResponse)
async def get_brands(db: Annotated[AsyncSession, Depends(get_db)]):

    brands = await db.scalars(select(BrandModel))

    return {"brands": brands.all()}
