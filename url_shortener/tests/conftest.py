import os
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel
from asgi_lifespan import LifespanManager
import redis.asyncio as redis

from url_shortener.api import app
from url_shortener.connection import engine, async_session

# Use Docker service hostnames, NOT localhost
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 15))

POSTGRES_URI = os.getenv("POSTGRES_URI")
MONGO_URI = os.getenv("MONGO_URI")


@pytest_asyncio.fixture(scope="function")
async def redis_client():
    """
    Fixture to provide Redis client connected to the Redis service container.
    """
    client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True,
    )
    await client.flushdb()
    yield client
    await client.flushdb()
    await client.close()


@pytest_asyncio.fixture(name="session")
async def session_fixture():
    """
    Provides a fresh SQLModel session.
    """
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function", autouse=True)
async def prepare_test_db():
    """
    Recreates all DB tables before each test.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    yield


@pytest_asyncio.fixture(scope="function")
async def client():
    """
    Creates an HTTPX test client with FastAPI lifespan support.
    """
    transport = ASGITransport(app=app)
    async with LifespanManager(app):
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


@pytest_asyncio.fixture(autouse=True)
async def clear_redis(redis_client):
    """
    Flush Redis before and after each test.
    """
    await redis_client.flushdb()
    yield
    await redis_client.flushdb()
