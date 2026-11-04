import os
from collections.abc import AsyncGenerator
from decimal import Decimal
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles

os.environ["DATABASE_URI"] = "sqlite+aiosqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-with-at-least-32-bytes"
os.environ["STRIPE_SECRET_KEY"] = "sk_test_placeholder"
os.environ["STRIPE_PUBLISHABLE_KEY"] = "pk_test_placeholder"
os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_test_placeholder"

from app.app import app
from app.database import Base, get_db
from app.enums import Role, TargetGroup
from app.models.product import (
    BrandModel,
    CategoryModel,
    ProductColorModel,
    ProductImageModel,
    ProductMaterialModel,
    ProductModel,
    ProductSizeModel,
    ProductVariantModel,
)
from app.models.user import UserModel
from app.services.auth import create_access_token


@compiles(ARRAY, "sqlite")
def compile_postgresql_array_for_sqlite(type_, compiler, **kwargs):
    return "JSON"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def async_db_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture
async def db_session(async_db_engine):
    session_factory = async_sessionmaker(bind=async_db_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest.fixture
async def async_client(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as client:
            yield client
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override


@pytest.fixture
async def catalog(db_session: AsyncSession) -> list[dict[str, Any]]:
    entries = []
    for index in range(3):
        category = CategoryModel(
            name=f"Category {index}",
            slug=f"category-{index}",
            image_url=f"https://example.com/category-{index}.jpg",
        )
        brand = BrandModel(name=f"Brand {index}", slug=f"brand-{index}")
        size = ProductSizeModel(name=f"Size {index}", sort_order=index + 1)
        color = ProductColorModel(
            name=f"Color {index}",
            hex_code=f"#{index:06x}",
            slug=f"color-{index}",
        )
        material = ProductMaterialModel(
            name=f"Material {index}", slug=f"material-{index}"
        )
        product = ProductModel(
            name=f"Product {index}",
            description=f"Description {index}",
            short_description=f"Short {index}",
            slug=f"product-{index}",
            thumbnail=f"https://example.com/product-{index}.jpg",
            tags=None,
            is_featured=index == 0,
            gender=TargetGroup.unisex,
            base_price=Decimal(f"{20 + index}.00"),
            category=category,
            brand=brand,
        )
        variant = ProductVariantModel(
            variant_price=Decimal(f"{20 + index}.00"),
            stock=10,
            is_available=True,
            product=product,
            color=color,
            material=material,
            size=size,
            thumbnail=f"https://example.com/variant-{index}.jpg",
        )
        image = ProductImageModel(
            url=f"https://example.com/image-{index}.jpg",
            alt_text=f"Product image {index}",
            sort_order=1,
            variant=variant,
        )
        db_session.add_all(
            [category, brand, size, color, material, product, variant, image]
        )
        entries.append(
            {
                "category": category,
                "brand": brand,
                "size": size,
                "color": color,
                "material": material,
                "product": product,
                "variant": variant,
                "image": image,
            }
        )

    await db_session.flush()
    return entries


@pytest.fixture
async def active_user(db_session: AsyncSession) -> UserModel:
    user = UserModel(
        username="test-customer",
        email="test-customer@example.com",
        hashed_password="not-used-by-token-auth",
        is_active=True,
        role=Role.customer,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
def authenticated_headers(active_user: UserModel) -> dict[str, str]:
    token = create_access_token({"sub": str(active_user.id)})
    return {"Authorization": f"Bearer {token}"}
