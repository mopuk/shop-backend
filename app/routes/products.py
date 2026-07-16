from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.models.product import ProductModel, ProductMaterialModel, ProductColorModel, ProductImageModel, ProductSizeModel, ProductVariantModel, CategoryModel, BrandModel
from app.database import get_db

router = APIRouter(
    prefix="/api/v1",
    tags=["products"]
    )


@router.get("/products")
async def get_products(db: Annotated[AsyncSession, Depends(get_db)]):
    
    smtm = select(ProductVariantModel).join(ProductModel).options(
                                        selectinload(ProductVariantModel.product),
                                        selectinload(ProductVariantModel.images),
                                        selectinload(ProductVariantModel.size),
                                        selectinload(ProductVariantModel.color),
                                        selectinload(ProductVariantModel.material),
                                    )
    variants = await db.execute(smtm)
    return {
    "variants": variants.scalars().all()
}

    
@router.get("/products/featured")
async def get_featured_products(db: Annotated[AsyncSession, Depends(get_db)]):

    smtm = select(ProductModel).options(
            selectinload(ProductModel.variants)
            .selectinload(ProductVariantModel.images),
            selectinload(ProductModel.variants)
            .selectinload(ProductVariantModel.color),
            selectinload(ProductModel.variants)
            .selectinload(ProductVariantModel.size),
            selectinload(ProductModel.variants)
            .selectinload(ProductVariantModel.material),
            selectinload(ProductModel.category),
            selectinload(ProductModel.brand),
        ).where(ProductModel.is_featured == True)

    products = await db.execute(smtm)
    return {
        "products": products.scalars().all()
    }

@router.get("/products/{product_slug}")
async def get_product(product_slug: str, db: Annotated[AsyncSession, Depends(get_db)]):
    
    try:
        smtm = select(ProductModel).options(
                selectinload(ProductModel.variants)
                    .selectinload(ProductVariantModel.images),

                selectinload(ProductModel.variants)
                    .selectinload(ProductVariantModel.color),

                selectinload(ProductModel.variants)
                    .selectinload(ProductVariantModel.size),

                selectinload(ProductModel.variants)
                    .selectinload(ProductVariantModel.material),

                selectinload(ProductModel.category),
                selectinload(ProductModel.brand),
            ).where(ProductModel.slug == product_slug)
        result = await db.execute(smtm)
        product = result.scalar_one_or_none()
    except SQLAlchemyError:
        raise HTTPException(500, "Error in the database")
    if not product:
        raise HTTPException(404, f"Product with slug: {product_slug} is not found")
        
    return product

@router.get("/categories")
async def get_categories(db: Annotated[AsyncSession, Depends(get_db)]):
    
    categories = await db.execute(select(CategoryModel))

    return {
        "categories": categories.scalars().all()
    }
    
@router.get("/categories/{category_slug}")
async def get_products_by_category(category_slug: str, db: Annotated[AsyncSession, Depends(get_db)]):
    
    smtm = select(ProductVariantModel).join(ProductModel).join(CategoryModel).options(
                                        selectinload(ProductVariantModel.product),
                                        selectinload(ProductVariantModel.images),
                                        selectinload(ProductVariantModel.size),
                                        selectinload(ProductVariantModel.color),
                                        selectinload(ProductVariantModel.material)
                                    ).where(CategoryModel.slug == category_slug)
    variants = await db.execute(smtm)
    return {
    "variants": variants.scalars().all()
}

@router.get("/brands")
async def get_brands(db: Annotated[AsyncSession, Depends(get_db)]):
    
    brands = await db.execute(select(BrandModel))

    return {
        "brands": brands.scalars().all()
    }

@router.get("/brands/{brand_slug}/products")
async def get_products_by_brand(brand_slug: str, db: Annotated[AsyncSession, Depends(get_db)]):

    smtm = select(ProductVariantModel).join(ProductModel).join(BrandModel).options(
                selectinload(ProductVariantModel.product),
                selectinload(ProductVariantModel.images),
                selectinload(ProductVariantModel.size),
                selectinload(ProductVariantModel.color),
                selectinload(ProductVariantModel.material),
            ).where(BrandModel.slug == brand_slug)
    
    variants = await db.execute(smtm)
    return {
        "variants": variants.scalars().all()
    }
