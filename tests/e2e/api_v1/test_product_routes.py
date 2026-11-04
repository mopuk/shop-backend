import pytest
from httpx import AsyncClient

from app.schemas.product import (
    BrandListResponse,
    CategoryListResponse,
    FiltersListResponse,
    ProductSchema,
    ProductVariantListResponse,
)


@pytest.mark.anyio
async def test_root_endpoint(async_client: AsyncClient):
    response = await async_client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Backend"}


@pytest.mark.anyio
async def test_get_products(async_client: AsyncClient, catalog):
    response = await async_client.get("/api/v1/products")

    assert response.status_code == 200
    data = ProductVariantListResponse.model_validate(response.json())
    assert len(data.variants) == 3
    assert data.pagination.total_items == 3
    assert data.pagination.total_pages == 1
    assert data.pagination.current_page == 1
    assert not data.pagination.has_next
    assert not data.pagination.has_previous


@pytest.mark.anyio
async def test_get_products_filters_and_sorting(async_client: AsyncClient, catalog):
    response = await async_client.get(
        "/api/v1/products",
        params=[
            ("categories", "category-1"),
            ("brands", "brand-1"),
            ("sizes", "Size 1"),
            ("materials", "material-1"),
            ("colors", "color-1"),
            ("sort", "price_desc"),
        ],
    )

    assert response.status_code == 200
    data = ProductVariantListResponse.model_validate(response.json())
    assert [variant.product.slug for variant in data.variants] == ["product-1"]
    assert data.pagination.total_items == 1


@pytest.mark.anyio
async def test_get_products_featured_and_pagination(
    async_client: AsyncClient, catalog
):
    featured = await async_client.get("/api/v1/products", params={"featured": True})
    page = await async_client.get(
        "/api/v1/products", params={"sort": "name_asc", "limit": 1, "offset": 1}
    )

    assert featured.status_code == 200
    assert [item["product"]["slug"] for item in featured.json()["variants"]] == [
        "product-0"
    ]
    assert page.status_code == 200
    paginated = ProductVariantListResponse.model_validate(page.json())
    assert len(paginated.variants) == 1
    assert paginated.variants[0].product.slug == "product-1"
    assert paginated.pagination.total_items == 3
    assert paginated.pagination.total_pages == 3
    assert paginated.pagination.current_page == 2
    assert paginated.pagination.has_next
    assert paginated.pagination.has_previous


@pytest.mark.anyio
async def test_product_metadata_and_detail_endpoints(
    async_client: AsyncClient, catalog
):
    categories = await async_client.get("/api/v1/categories")
    brands = await async_client.get("/api/v1/brands")
    filters = await async_client.get("/api/v1/products/filters")
    product = await async_client.get("/api/v1/products/product-0")

    assert CategoryListResponse.model_validate(categories.json())
    assert BrandListResponse.model_validate(brands.json())
    assert FiltersListResponse.model_validate(filters.json())
    assert [item["slug"] for item in categories.json()["categories"]] == [
        "category-0",
        "category-1",
        "category-2",
    ]
    assert [item["slug"] for item in brands.json()["brands"]] == [
        "brand-0",
        "brand-1",
        "brand-2",
    ]
    assert len(filters.json()["sizes"]) == 3
    assert product.status_code == 200
    product_data = ProductSchema.model_validate(product.json())
    assert product_data.slug == "product-0"
    assert len(product_data.variants) == 1
    assert product_data.variants[0].images[0].alt_text == "Product image 0"


@pytest.mark.anyio
async def test_get_product_returns_404_for_unknown_slug(
    async_client: AsyncClient,
):
    response = await async_client.get("/api/v1/products/not-a-product")

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Product with slug: not-a-product is not found"
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("params", "expected_status"),
    [
        ({"offset": -1}, 422),
        ({"limit": 0}, 422),
        ({"limit": 101}, 422),
    ],
)
async def test_get_products_validates_pagination(
    async_client: AsyncClient, params: dict[str, int], expected_status: int
):
    response = await async_client.get("/api/v1/products", params=params)

    assert response.status_code == expected_status
