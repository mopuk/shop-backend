from app import app, db, models
from flask import request, abort
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.utils import serialize_product, serialize_variant

@app.get("/")
def Home():
    return "Backend"

@app.get("/api/products")
def getProducts():
    
    variants = db.session.scalars(select(models.ProductVariant)
                                  .join(models.Product)
                                    .options(
                                        selectinload(models.ProductVariant.product),
                                        selectinload(models.ProductVariant.images),
                                        selectinload(models.ProductVariant.size),
                                        selectinload(models.ProductVariant.color),
                                        selectinload(models.ProductVariant.material),
                                    )).all()
    
    return {
    "variants": [
        serialize_variant(v)
        for v in variants
    ]
}
    
@app.get("/api/products/<string:productSlug>")
def getProduct(productSlug):
    
    product = db.session.scalar(
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
        .where(models.Product.slug == productSlug)
    )
    
    if not product:
        abort(404)
        
    return {
        "product": serialize_product(product)
    }
    
@app.get("/api/categories/<string:category>")
def getProductsByCategory(category):
    
    variants = db.session.scalars(select(models.ProductVariant)
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
    "variants": [
        serialize_variant(v) for v in variants
    ]
}
    
@app.get("/api/brands/<string:brand>/products")
def getProductsByBrand(brand):

    variants = db.session.scalars(
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
        "variants": [
        serialize_variant(v) for v in variants
        ]
    }
    
@app.get("/api/products/featured")
def getFeaturedProducts():

    products = db.session.scalars(
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
        "products": [
            serialize_product(product)
            for product in products
        ]
    }