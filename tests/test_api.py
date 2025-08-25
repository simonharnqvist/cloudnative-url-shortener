import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_short_url(client: AsyncClient):
    response = await client.post("/", json={"original_url": "https://example.com"})
    assert response.status_code == 200
    assert response.json()["original_url"] == "https://example.com"


@pytest.mark.asyncio
async def test_create_original_url(client: AsyncClient):
    response_post = await client.post("/", json={"original_url": "https://example.com"})
    short_url = response_post.json()["short_url"]
    response_get = await client.get(f"/{short_url}")
    assert response_get.status_code == 200
    assert response_get.json()["original_url"] == "https://example.com"


@pytest.mark.asyncio
async def test_get_url_not_found(client: AsyncClient):
    response = await client.get("/NONEXIST")
    assert response.status_code == 404
    assert response.json()["detail"] == "URL not found"
