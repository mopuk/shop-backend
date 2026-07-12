from app import models
from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload, Session
from typing import Annotated

router = APIRouter(
    prefix="/api/v1",
    tags=["products"]
    )


@router.get("/products")
def getProducts(db: Annotated[Session, Depends(get_db)]):
    
    variants = db.scalars(select(models.ProductVariant)
                                  .join(models.Product)
                                    .options(
                                        selectinload(models.ProductVariant.product),
                                        selectinload(models.ProductVariant.images),
                                        selectinload(models.ProductVariant.size),
                                        selectinload(models.ProductVariant.color),
                                        selectinload(models.ProductVariant.material),
                                    )).all()
    
    return {
    "variants": variants
}

    
@router.get("/products/featured")
def getFeaturedProducts(db: Annotated[Session, Depends(get_db)]):

    products = db.scalars(
        select(models.Product)
        .options(
            selectinload(models.Product.variants)
                .selectinload(models.ProductVariant.images),

            selectinload(models.Product.variants)
                .selectinload(models.ProductVariant.color),

            selectinload(models.Product.variants)
                .selectinload(models.ProductVariant.size),

            selectinload(models.Product.variants)
                .selectinload(models.ProductVariant.material),

            selectinload(models.Product.category),
            selectinload(models.Product.brand),
        )
        .where(models.Product.is_featured == True)
    ).all()

    return {
        "products": products
    }

@router.get("/products/{product_slug}")
def getProduct(product_slug, db: Annotated[Session, Depends(get_db)]):
    
    try:
        product = db.scalar(
            select(models.Product)
            .options(
                selectinload(models.Product.variants)
                    .selectinload(models.ProductVariant.images),

                selectinload(models.Product.variants)
                    .selectinload(models.ProductVariant.color),

                selectinload(models.Product.variants)
                    .selectinload(models.ProductVariant.size),

                selectinload(models.Product.variants)
                    .selectinload(models.ProductVariant.material),

                selectinload(models.Product.category),
                selectinload(models.Product.brand),
            )
            .where(models.Product.slug == product_slug)
        )
    except SQLAlchemyError:
        raise HTTPException(500, "Error in the database")
    if not product:
        raise HTTPException(404, f"Product with slug: {product_slug} is not found")
        
    return product

@router.get("/categories")
def getCategories(db: Annotated[Session, Depends(get_db)]):
    
    categories = db.scalars(select(models.Category)).all()

    return {
        "categories": categories
    }
    
@router.get("/categories/{category}")
def getProductsByCategory(category: str, db: Annotated[Session, Depends(get_db)]):
    
    variants = db.scalars(select(models.ProductVariant)
                                  .join(models.Product)
                                  .join(models.Category)
                                    .options(
                                        selectinload(models.ProductVariant.product),
                                        selectinload(models.ProductVariant.images),
                                        selectinload(models.ProductVariant.size),
                                        selectinload(models.ProductVariant.color),
                                        selectinload(models.ProductVariant.material)
                                    )
                                    .where(models.Category.slug == category)).all()
    
    return {
    "variants": variants
}

@router.get("/brands")
def getBrands(db: Annotated[Session, Depends(get_db)]):
    
    brands = db.scalars(select(models.Brand)).all()

    return {
        "brands": brands
    }

@router.get("/brands/{brand}/products")
def getProductsByBrand(brand: str, db: Annotated[Session, Depends(get_db)]):

    variants = db.scalars(
        select(models.ProductVariant)
        .join(models.Product)
        .join(models.Brand)
        .options(
            selectinload(models.ProductVariant.product),
            selectinload(models.ProductVariant.images),
            selectinload(models.ProductVariant.size),
            selectinload(models.ProductVariant.color),
            selectinload(models.ProductVariant.material),
        )
        .where(models.Brand.slug == brand)
    ).all()

    return {
        "variants": variants
    }
