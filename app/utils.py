from flask import request

def serialize_variant(variant):
    return {
        "id": variant.id,
        "price": float(variant.variant_price),
        "stock": variant.stock,
        "is_available": variant.is_available,

        "color": serialize_color(variant.color),

        "size": serialize_size(variant.size),

        "material": serialize_material(variant.material),

        "images": [
            serialize_image(img)
            for img in variant.images
        ],
        "product": serialize_product(variant.product, include_variants=False)
    }


def serialize_product(product, include_variants=True):
    return {
        "id": product.id,
        "name": product.name,
        "slug": product.slug,
        "short_description": product.short_description,
        "description": product.description,
        "thumbnail": image_url(product.thumbnail),
        "tags": product.tags,
        "is_featured": product.is_featured,
        "created_at": product.created_at.isoformat(),
        "gender": product.gender.value,
        "base_price": float(product.base_price),
        "category": serialize_category(product.category) if product.category else None,
        "brand": serialize_brand(product.brand) if product.brand else None,

        "variants": (
            [serialize_variant(v) for v in product.variants]
            if include_variants
            else []
        ),
    }
    
def image_url(path: str) -> str:
    return request.host_url.rstrip("/") + "/static/images/" + path


def serialize_brand(brand):
    return {
        "id": brand.id,
        "name": brand.name,
        "slug": brand.slug,
    }


def serialize_category(category, include_children=False):
    return {
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "parent_id": category.parent_id,

        "children": (
            [serialize_category(child) for child in category.children]
            if include_children
            else None
        ),
    }


def serialize_color(color):
    return {
        "id": color.id,
        "name": color.name,
        "hex_code": color.hex_code,
        "slug": color.slug,
    }


def serialize_material(material):
    return {
        "id": material.id,
        "name": material.name,
        "slug": material.slug,
    }


def serialize_size(size):
    return {
        "id": size.id,
        "name": size.name,
        "sort_order": size.sort_order,
    }


def serialize_image(image):
    return {
        "id": image.id,
        "url": image_url(image.url),
        "alt_text": image.alt_text,
        "sort_order": image.sort_order,
        "variant_id": image.variant_id,
    }
