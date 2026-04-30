"""Shared test fixtures. Uses mongomock-motor so no real MongoDB is needed."""
import os

# Must be set before any burningbackend import so Settings() can instantiate.
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("DEBUG", "true")  # bypass the production password validator

import pytest
from beanie import init_beanie
from httpx import AsyncClient, ASGITransport
from mongomock_motor import AsyncMongoMockClient

from burningbackend.app.core.config import settings
from burningbackend.app.core.security import get_password_hash
from burningbackend.app.models import gather_documents
from burningbackend.app.models.user import User


@pytest.fixture(autouse=True)
async def init_db():
    client = AsyncMongoMockClient()
    await init_beanie(database=client["testdb"], document_models=gather_documents())
    yield
    # mongomock resets state per client instantiation — no teardown needed


@pytest.fixture
async def admin_user(init_db) -> User:
    user = User(
        username="admin",
        email="admin@test.com",
        hashed_password=get_password_hash("testpassword"),
        is_superuser=True,
    )
    await user.insert()
    return user


@pytest.fixture
async def auth_token(admin_user) -> str:
    from burningbackend.app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            f"/api/{settings.API_V1_STR}/auth/token",
            data={"username": "admin", "password": "testpassword"},
        )
    return resp.json()["access_token"]


@pytest.fixture
async def client(init_db):
    from burningbackend.app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture
async def auth_headers(auth_token) -> dict:
    return {"Authorization": f"Bearer {auth_token}"}
