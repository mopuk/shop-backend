from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.community.postgres import PostgresContainer

from app.app import app
from app.database import Base, get_db

TEST_DATABASE_URI = "sqlite+aiosqlite:///:memory:"

postgres_container = PostgresContainer()


@pytest.fixture(scope="session", autouse=True)
def setup_testcontainers():
    with postgres_container:
        sync_url = postgres_container.get_connection_url(driver="psycopg2")
        async_url = postgres_container.get_connection_url(driver="asyncpg")

        sync_engine = create_engine(sync_url, echo=False)
        with sync_engine.begin() as conn:
            Base.metadata.create_all(conn)

        sync_engine.dispose()

        yield async_url


@pytest.fixture(scope="session", autouse=True)
def async_db_engine(setup_testcontainers: str):
    async_engine = create_async_engine(setup_testcontainers, echo=False)

    yield async_engine

    async_engine.sync_engine.dispose()


@pytest.fixture(autouse=True)
async def db_session(async_db_engine):
    session_maker = async_sessionmaker(bind=async_db_engine, expire_on_commit=False)
    async with session_maker() as session, session.begin():
        yield session
        await session.rollback()


@pytest.fixture
async def async_client(db_session) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

    app.dependency_overrides.clear()
