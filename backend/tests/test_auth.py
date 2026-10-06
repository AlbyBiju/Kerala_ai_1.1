import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from app.core.config import settings

@pytest.mark.asyncio
async def test_auth_valid_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/auth/login", json={"username": settings.TEAM_USERNAME, "password": settings.TEAM_PASSWORD})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_auth_invalid_credentials():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/auth/login", json={"username": "wrong", "password": "bad"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

@pytest.mark.asyncio
async def test_protected_endpoint_without_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/shipments")
        assert response.status_code == 401 or response.status_code == 403
