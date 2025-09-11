from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
import random
import string
from sqlalchemy import select
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_fastapi_instrumentator.metrics import (
    requests,
    latency,
    request_size,
    response_size,
)
from datetime import datetime, timezone
from url_shortener.connection import (
    get_session,
    engine,
    logs_collection,
    lifespan,
)
from url_shortener.orm import URL
from urllib.parse import urlparse
import logging
from url_shortener.auth import verify_api_token

logging.basicConfig(level=logging.DEBUG)

SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


app = FastAPI(lifespan=lifespan)
Instrumentator().add(requests()).add(latency()).add(request_size()).add(
    response_size()
).instrument(app)

security = HTTPBasic()


def generate_random_code(k: int = 6) -> str:
    """Generate random string of length k"""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=k))


def ensure_url_scheme(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme:
        return "http://" + url
    return url


@app.post("/")
async def post_url(url: URL, session: SessionDep):
    url.short_url = generate_random_code()
    session.add(url)
    await session.commit()
    await session.refresh(url)
    return url


@app.get("/metrics", include_in_schema=False)
async def get_metrics(_=Depends(verify_api_token)):
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/logs", include_in_schema=False)
async def get_logs(_=Depends(verify_api_token)):
    logs_cursor = logs_collection.find({})
    logs = await logs_cursor.to_list(length=100)
    for log in logs:
        log["_id"] = str(log["_id"])
    return logs


@app.get("/{short_url}")
async def get_url(short_url: str, session: SessionDep, request: Request):
    redis_client = request.app.state.redis_client

    cached_url = await redis_client.get(short_url)
    if cached_url:
        return RedirectResponse(url=cached_url, status_code=303)

    result = await session.execute(select(URL).where(URL.short_url == short_url))
    url: URL | None = result.scalar_one_or_none()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    elif not isinstance(url, URL):
        raise HTTPException(
            status_code=500, detail=f"URL type invalid - not URL object but {type(url)}"
        )
    elif not isinstance(url.original_url, str):
        raise HTTPException(status_code=500, detail="URL type invalid - not string")

    client_ip = request.client.host

    await logs_collection.insert_one(
        {
            "short_code": short_url,
            "ip": client_ip,
            "timestamp": datetime.now(timezone.utc),
            "user_agent": request.headers.get("user-agent"),
        }
    )

    await redis_client.set(short_url, url.original_url, ex=3600)
    redirect_target = ensure_url_scheme(url.original_url)
    return RedirectResponse(url=redirect_target, status_code=303)
