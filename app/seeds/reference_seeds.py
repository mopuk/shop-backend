from pathlib import Path

from sqlalchemy.dialects.postgresql import insert

from app.database import AsyncSessionLocal
from app.models.product import (
    BrandModel,
    CategoryModel,
    ProductColorModel,
    ProductMaterialModel,
    ProductSizeModel,
)
from app.utils.json_loader import load_json

REFERENCES_FILE = Path(__file__).parent / "references.json"


async def seed_references():
    references_data = load_json(REFERENCES_FILE)

    async with AsyncSessionLocal() as session:
        sizes_to_insert = [
            {
                "name": size.get("name"),
                "sort_order": size.get("sort_order"),
            }
            for size in references_data.get("sizes", [])
        ]

        colors_to_insert = [
            {
                "name": color.get("name"),
                "hex_code": color.get("hex_code"),
                "slug": color.get("slug"),
            }
            for color in references_data.get("colors", [])
        ]

        materials_to_insert = [
            {
                "name": material.get("name"),
                "slug": material.get("slug"),
            }
            for material in references_data.get("materials", [])
        ]

        categories_to_insert = [
            {
                "name": category.get("name"),
                "slug": category.get("slug"),
                "parent_id": category.get("parent_id"),
                "image_url": category.get("image_url"),
            }
            for category in references_data.get("categories", [])
        ]

        brands_to_insert = [
            {
                "name": brand.get("name"),
                "slug": brand.get("slug"),
            }
            for brand in references_data.get("brands", [])
        ]

        sizes_stmt = (
            insert(ProductSizeModel).values(sizes_to_insert).on_conflict_do_nothing()
        )
        colors_stmt = (
            insert(ProductColorModel).values(colors_to_insert).on_conflict_do_nothing()
        )
        materials_stmt = (
            insert(ProductMaterialModel)
            .values(materials_to_insert)
            .on_conflict_do_nothing()
        )
        categories_stmt = (
            insert(CategoryModel).values(categories_to_insert).on_conflict_do_nothing()
        )
        brands_stmt = (
            insert(BrandModel).values(brands_to_insert).on_conflict_do_nothing()
        )

        await session.execute(sizes_stmt)
        await session.execute(colors_stmt)
        await session.execute(materials_stmt)
        await session.execute(categories_stmt)
        await session.execute(brands_stmt)

        await session.commit()
