from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert

from app.database import AsyncSessionLocal
from app.models.product import (
    BrandModel,
    CategoryModel,
    ProductImageModel,
    ProductModel,
    ProductVariantModel,
)
from app.utils.json_loader import load_json

PRODUCTS_FILE = Path(__file__).parent / "products.json"
products_data = load_json(PRODUCTS_FILE)


async def seed_products():

    async with AsyncSessionLocal() as session:
        categories = select(CategoryModel)
        categories = {
            category.slug.lower(): category.id
            for category in (await session.scalars(categories)).all()
        }

        brands = select(BrandModel)
        brands = {
            brand.slug.lower(): brand.id
            for brand in (await session.scalars(brands)).all()
        }

        products_to_insert = [
            {
                "name": item.get("name"),
                "short_description": item.get("short_description"),
                "description": item.get("description"),
                "tags": item.get("tags"),
                "gender": item.get("gender"),
                "base_price": item.get("base_price"),
                "category_id": categories.get(
                    "-".join(item["category"].lower().split(" "))
                ),
                "brand_id": brands.get("-".join(item["brand"].lower().split(" "))),
                "slug": item.get("slug"),
                "is_featured": False,
                "thumbnail": "",
            }
            for item in products_data
        ]

        await session.execute(
            insert(ProductModel).values(products_to_insert).on_conflict_do_nothing()
        )
        await session.commit()


async def reset_products():
    async with AsyncSessionLocal() as session:
        await session.execute(delete(ProductImageModel))
        await session.execute(delete(ProductVariantModel))
        await session.execute(delete(ProductModel))
        await session.commit()
