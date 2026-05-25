from app import app, db, models
from flask import request
from sqlalchemy import select
from sqlalchemy.orm import selectinload


@app.get("/api/products")
def getProducts():
    
    products = db.session.scalars(select(models.Product)
                                  .options(selectinload(models.Product.variants)
                                           .selectinload(models.ProductVariant.images))
                                  ).all()
    
    return {
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "variants": [
                    {
                        "id": v.id,
                        "price": v.variant_price,
                        "stock": v.stock,
                        "is_available": v.is_available,
                        "color": {
                            "name": v.color.name,
                            "hex_code": v.color.hex_code,
                            "slug": v.material.slug,
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
                                "variant_id": img.variant_id
                            } for img in v.images
                        ]
                    } for v in p.variants
                ],
                "description": p.description,
                "short_description": p.short_description,
                "slug": p.slug,
                "thumbnail": request.host_url.rstrip("/") + "/static/images/" + p.thumbnail,
                "tags": p.tags,
                "is_featured": p.is_featured,
                "created_at": p.created_at,
                "gender": p.gender.value,
                "base_price": p.base_price,
                "category": p.category.name if p.category else None,
                "brand": p.brand.name if p.brand else None,
            }
            for p in products
        ]
    }