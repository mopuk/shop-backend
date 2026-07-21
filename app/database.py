import os
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


engine = create_async_engine(
    os.getenv("DATABASE_URI") or "postgresql+asyncpg://mopuk:moriktop8@localhost:5432/shop_db"
)
AsyncSessionLocal = async_sessionmaker(bind=engine,  expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session