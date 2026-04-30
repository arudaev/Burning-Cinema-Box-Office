import pytest
from httpx import AsyncClient, ASGITransport

from burningbackend.app.core.config import settings


async def _client():
    from burningbackend.app.main import app
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


async def test_login_success(admin_user):
    async with await _client() as c:
        resp = await c.post(
            f"/api/{settings.API_V1_STR}/auth/token",
            data={"username": "admin", "password": "testpassword"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


async def test_login_wrong_password(admin_user):
    async with await _client() as c:
        resp = await c.post(
            f"/api/{settings.API_V1_STR}/auth/token",
            data={"username": "admin", "password": "wrong"},
        )
    assert resp.status_code == 401


async def test_login_unknown_user():
    async with await _client() as c:
        resp = await c.post(
            f"/api/{settings.API_V1_STR}/auth/token",
            data={"username": "nobody", "password": "x"},
        )
    assert resp.status_code == 401


async def test_refresh_with_valid_token(auth_token):
    async with await _client() as c:
        resp = await c.post(
            f"/api/{settings.API_V1_STR}/auth/refresh",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


async def test_refresh_with_invalid_token():
    async with await _client() as c:
        resp = await c.post(
            f"/api/{settings.API_V1_STR}/auth/refresh",
            headers={"Authorization": "Bearer notavalidtoken"},
        )
    assert resp.status_code == 401
