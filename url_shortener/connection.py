from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlalchemy.pool import NullPool
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi

DATABASE_URL = "postgresql+asyncpg://postgres:password@postgres:5432/postgres"
MONGO_URI = "mongodb://root:example@mongodb:27017"


engine = create_async_engine(DATABASE_URL, echo=True, poolclass=NullPool)

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
