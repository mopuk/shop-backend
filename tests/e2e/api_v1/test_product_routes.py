import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.product import ProductVariantListResponse
from tests.factories.product import (
    BrandFactory,
    CategoryFactory,
    ProductColorFactory,
    ProductFactory,
    ProductMaterialFactory,
    ProductSizeFactory,
    ProductVariantFactory,
)


@pytest.mark.anyio
async def test_get_products(db_session: AsyncSession, async_client: AsyncClient):
    sizes = ProductSizeFactory.batch(5)
    colors = ProductColorFactory.batch(5)
    materials = ProductMaterialFactory.batch(5)
    ##images = ProductImageFactory.batch(5)
    categories = CategoryFactory.batch(5)
    brands = BrandFactory.batch(5)

    db_session.add_all(sizes + colors + materials + categories + brands)
    await db_session.flush()

    assert categories != []

    products = [
        ProductFactory.build(
            name="Nike Air Force",
            category_id=categories[i].id,
            brand_id=brands[i].id,
        )
        for i in range(5)
    ]

    db_session.add_all(products)
    await db_session.flush()

    variants = [
        ProductVariantFactory.build(
            product_id=products[i].id,
            color_id=colors[i].id,
            material_id=materials[i].id,
            size_id=sizes[i].id,
        )
        for i in range(5)
    ]

    db_session.add_all(variants)
    await db_session.flush()

    data = await async_client.get("/api/v1/products")
    fetched_variants = data.json()

    ProductVariantListResponse.model_validate(fetched_variants)

    assert len(fetched_variants["variants"]) == 5
    assert {v["id"] for v in fetched_variants["variants"]} == {v.id for v in variants}
