from app import app, models
from flask import request, abort
from sqlalchemy import select
from sqlalchemy.orm import selectinload, Session
from typing import Annotated
from fastapi import Depends, HTTPException
from app.schemas import *
from app.database import get_db

  
@app.get("/")
def Home():
    return "Hello"

@app.get("/api//v1/products")
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

   
@app.get("/api/v1/products/featured")
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
    
@app.get("/api/v1/products/{product_slug}")
def getProduct(product_slug: str, db: Annotated[Session, Depends(get_db)]):
    
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
    
    if not product:
        raise HTTPException(404, f"Product with product slug: {product_slug} not found")
        
    return product
    
@app.get("/api/v1/categories/{category}")
def getProductsByCategory(category: str, db: Annotated[Session, Depends(get_db)]):
    
    variants = db.scalars(select(models.ProductVariant)
                                  .join(models.Product)
                                  .join(models.Category)
                                    .options(
                                        selectinload(models.ProductVariant.product),
                                        selectinload(models.ProductVariant.images),
                                        selectinload(models.ProductVariant.size),
                                        selectinload(models.ProductVariant.color),
                                        selectinload(models.ProductVariant.material),
                                    )
                                    .where(models.Category.slug == category)).all()
    
    return {
    "variants": variants,
    "category": category
}
    
@app.get("/api/v1/brands/{brand}/products")
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
        "variants": variants,
        "brand": brand
    }
 