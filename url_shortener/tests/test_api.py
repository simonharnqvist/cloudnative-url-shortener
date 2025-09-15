import pytest
from httpx import AsyncClient
import os
from url_shortener.api import app

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
