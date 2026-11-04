import pytest
from httpx import AsyncClient

from app.schemas.product import ProductVariantSchema


@pytest.mark.anyio
async def test_get_products(async_client: AsyncClient):
    response = await async_client.get("/api/v1/products")

    assert response.status_code == 200

    data = response.json()

    assert set(data.keys()) == {"variants", "pagination"}
    assert data["variants"] == []
    assert data["pagination"] == {
        "total_items": 0,
        "total_pages": 0,
        "current_page": 1,
        "has_next": False,
        "has_previous": False,
    }

    for variant in data["variants"]:
        ProductVariantSchema.model_validate(variant)
