import pytest
from httpx import AsyncClient
import os
from url_shortener.api import app
from dotenv import load_dotenv
from conftest import redis_client

load_dotenv("./url_shortener/.env")
API_TOKEN = os.getenv("API_TOKEN")
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}
assert API_TOKEN, "API_TOKEN is not set in environment"


@pytest.mark.asyncio
async def test_create_short_url(client: AsyncClient):
    response = await client.post("/", json={"original_url": "https://example.com"})
    assert response.status_code == 200
    assert response.json()["original_url"] == "https://example.com"


@pytest.mark.asyncio
async def test_get_original_url(client: AsyncClient):
    response_post = await client.post("/", json={"original_url": "https://example.com"})
    short_url = response_post.json()["short_url"]
    response_get = await client.get(f"/{short_url}")
    assert response_get.status_code == 303


@pytest.mark.asyncio
async def test_get_url_not_found(client: AsyncClient):
    response = await client.get("/NONEXIST")
    assert response.status_code == 404
    assert response.json()["detail"] == "URL not found"


@pytest.mark.asyncio
async def test_url_is_cached_after_lookup(client, redis_client):
    response = await client.post("/", json={"original_url": "https://www.google.com"})
    assert response.status_code == 200

    short_code = response.json()["short_url"]
    print(short_code)

    get1 = await client.get(f"/{short_code}")
    assert get1.status_code == 303
    # assert get1.json()["original_url"] == "https://www.google.com"
    # assert get1.json()["source"] == "db"

    cached = await redis_client.get(short_code)
    assert cached == "https://www.google.com"

    get2 = await client.get(f"/{short_code}")
    assert get2.status_code == 303
    # assert get2.json()["original_url"] == "https://www.google.com"
    # assert get2.json()["source"] == "cache"


@pytest.mark.asyncio
async def test_metrics_without_token(client: AsyncClient):
    response = await client.get("/metrics")
    assert response.status_code == 401
    assert "Missing" in response.json().get(
        "detail", ""
    ) or "Invalid" in response.json().get("detail", "")


@pytest.mark.asyncio
async def test_metrics_with_token(client: AsyncClient):
    response = await client.get("/metrics", headers=HEADERS)
    assert response.status_code == 200
    # The prometheus metrics endpoint returns plain text content
    assert "text/plain" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_logs_without_token(client: AsyncClient):
    response = await client.get("/logs")
    assert response.status_code == 401
    assert "Missing" in response.json().get(
        "detail", ""
    ) or "Invalid" in response.json().get("detail", "")


async def test_logs_with_token(client: AsyncClient):
    response = await client.get("/logs", headers=HEADERS)
    print("Status code:", response.status_code)
    print("Response content:", response.text)
    assert response.status_code == 200, f"Unexpected status: {response.status_code}"
    data = response.json()
    print("Response JSON type:", type(data))
    assert isinstance(data, list), f"Expected list but got {type(data)}"
