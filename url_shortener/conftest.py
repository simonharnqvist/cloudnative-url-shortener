import pytest_asyncio
from httpx import AsyncClient
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import ASGITransport
from api import app
from asgi_lifespan import LifespanManager

pytest_plugins = ("pytest_asyncio",)

from connection import engine, async_session


@pytest_asyncio.fixture(name="session")
async def session_fixture():
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def prepare_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    yield


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with LifespanManager(app):
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


@pytest_asyncio.fixture(autouse=True)
async def clear_redis():
    # Access Redis client safely from app.state
    await app.state.redis_client.flushdb()
    yield
    await app.state.redis_client.flushdb()
