import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_endpoint(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_get_history_unauthorized(async_client: AsyncClient):
    # Should fail without authentication
    response = await async_client.get("/history")
    assert response.status_code == 401
