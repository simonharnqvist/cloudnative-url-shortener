from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlalchemy.pool import NullPool
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import os
from redis import asyncio as aioredis
from fastapi import FastAPI

load_dotenv(".env")

POSTGRES_URI = os.getenv("POSTGRES_URI")
MONGO_URI = os.getenv("MONGO_URI")
REDIS_URI = os.getenv("REDIS_URI")

engine = create_async_engine(POSTGRES_URI, echo=True, poolclass=NullPool)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    async with async_session() as session:
        yield session


client = AsyncIOMotorClient(MONGO_URI, server_api=ServerApi("1"))
db = client["url_shortener"]
logs_collection = db["access_logs"]


@asynccontextmanager
async def lifespan(app: FastAPI):

    app.state.redis_client = aioredis.from_url(
        REDIS_URI, encoding="utf-8", decode_responses=True
    )

    yield

    await app.state.redis_client.close()
