from pathlib import Path

from sqlalchemy import delete, select, tuple_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.product import (
    ProductColorModel,
    ProductMaterialModel,
    ProductModel,
    ProductSizeModel,
    ProductVariantModel,
)
from app.utils.json_loader import load_json

VARIANTS_PATH = Path(__file__).parent / "variants.json"
variants_data = load_json(VARIANTS_PATH)


async def get_references(session: AsyncSession):
    product_slugs = [variant["product_slug"] for variant in variants_data]
    color_slugs = [variant["color_slug"] for variant in variants_data]
    material_slugs = [variant["material_slug"] for variant in variants_data]
    size_names = [variant["size_name"] for variant in variants_data]
    products = await session.scalars(
        select(ProductModel).where(ProductModel.slug.in_(product_slugs))
    )
    colors = await session.scalars(
        select(ProductColorModel).where(ProductColorModel.slug.in_(color_slugs))
    )
    materials = await session.scalars(
        select(ProductMaterialModel).where(
            ProductMaterialModel.slug.in_(material_slugs)
        )
    )
    sizes = await session.scalars(
        select(ProductSizeModel).where(ProductSizeModel.name.in_(size_names))
    )
    product_ids = {product.slug: product.id for product in products.all()}
    color_ids = {color.slug: color.id for color in colors}
    material_ids = {material.slug: material.id for material in materials}
    size_ids = {size.name: size.id for size in sizes}

    return {
        "product_ids": product_ids,
        "color_ids": color_ids,
        "material_ids": material_ids,
        "size_ids": size_ids,
    }


async def seed_variants():
    async with AsyncSessionLocal() as session:
        references = await get_references(session)

        product_ids = references["product_ids"]
        color_ids = references["color_ids"]
        material_ids = references["material_ids"]
        size_ids = references["size_ids"]

        variants_to_insert = [
            {
                "variant_price": variant["variant_price"],
                "stock": variant["stock"],
                "is_available": variant["is_available"],
                "product_id": product_ids[variant["product_slug"]],
                "color_id": color_ids[variant["color_slug"]],
                "material_id": material_ids[variant["material_slug"]],
                "size_id": size_ids[variant["size_name"]],
                "thumbnail": None,
            }
            for variant in variants_data
        ]

        await session.execute(
            insert(ProductVariantModel)
            .values(variants_to_insert)
            .on_conflict_do_nothing()
        )

        await session.commit()


async def reset_variants():
    async with AsyncSessionLocal() as session:
        references = await get_references(session)

        product_ids = references["product_ids"]
        color_ids = references["color_ids"]
        material_ids = references["material_ids"]
        size_ids = references["size_ids"]

        variant_keys = [
            (
                product_ids[variant["product_slug"]],
                color_ids[variant["color_slug"]],
                material_ids[variant["material_slug"]],
                size_ids[variant["size_name"]],
            )
            for variant in variants_data
        ]
        await session.execute(
            delete(ProductVariantModel).where(
                tuple_(
                    ProductVariantModel.product_id,
                    ProductVariantModel.color_id,
                    ProductVariantModel.material_id,
                    ProductVariantModel.size_id,
                ).in_(variant_keys)
            )
        )

        await session.commit()
