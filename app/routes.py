from app import app, db, models
from flask import request
from sqlalchemy import select
from sqlalchemy.orm import selectinload


@app.get("/api/products")
def getProducts():
    
    variants = db.session.scalars(select(models.ProductVariant)
    .options(
        selectinload(models.ProductVariant.product),
        selectinload(models.ProductVariant.images),
        selectinload(models.ProductVariant.size),
        selectinload(models.ProductVariant.color),
        selectinload(models.ProductVariant.material),
    )).all()
    
    return {
    "variants": [
        {
            "id": v.id,
            "price": v.variant_price,
            "stock": v.stock,
            "is_available": v.is_available,

            "product": {
                "id": v.product.id,
                "name": v.product.name,
                "slug": v.product.slug,
                "short_description": v.product.short_description,
                "description": v.product.description,
                "thumbnail": request.host_url.rstrip("/") + "/static/images/" + v.product.thumbnail,
                "tags": v.product.tags,
                "is_featured": v.product.is_featured,
                "created_at": v.product.created_at,
                "gender": v.product.gender.value,
                "base_price": v.product.base_price,
                "category": v.product.category.name if v.product.category else None,
                "brand": v.product.brand.name if v.product.brand else None,
            },

            "color": {
                "name": v.color.name,
                "hex_code": v.color.hex_code,
                "slug": v.color.slug,
            },

            "size": {
                "name": v.size.name,
                "sort_order": v.size.sort_order,
            },

            "material": {
                "name": v.material.name,
                "slug": v.material.slug,
            },

            "images": [
                {
                    "id": img.id,
                    "url": request.host_url.rstrip("/") + "/static/images/" + img.url,
                    "alt_text": img.alt_text,
                    "sort_order": img.sort_order,
                    "variant_id": img.variant_id,
                }
                for img in v.images
            ],
        }
        for v in variants
    ]
}