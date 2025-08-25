from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from url_shortener.orm import URL
from sqlalchemy.pool import NullPool

DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/postgres"

engine = create_async_engine(DATABASE_URL, echo=True, poolclass=NullPool)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    async with async_session() as session:
        yield session
