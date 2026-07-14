import os
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


engine = create_async_engine(os.getenv("DATABASE_URI") or "postgresql+asyncpg://local_user:local_password@10.255.255.254:5432/shop_db")
AsyncSessionLocal = async_sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session