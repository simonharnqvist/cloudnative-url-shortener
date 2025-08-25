from fastapi import Depends, FastAPI, HTTPException
from typing import Annotated
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
import random
import string
from sqlalchemy import select
from contextlib import asynccontextmanager

from connection import get_session, engine
from orm import URL

SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


def generate_random_code(k: int = 6) -> str:
    """Generate random string of length k"""
    return "".join("".join(random.choices(string.ascii_uppercase + string.digits, k=k)))


@app.post("/")
async def post_url(url: URL, session: SessionDep):
    url.short_url = generate_random_code()
    session.add(url)
    await session.commit()
    await session.refresh(url)
    return url


@app.get("/{short_url}")
async def get_url(short_url: str, session: SessionDep):
    result = await session.exec(select(URL).where(URL.short_url == short_url))
    url = result.scalar_one_or_none()

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    return url
