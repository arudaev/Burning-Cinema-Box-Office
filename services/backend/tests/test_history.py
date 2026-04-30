from datetime import datetime

import pytest

from burningbackend.app.core.config import settings

BASE = f"/api/{settings.API_V1_STR}/history"

ORDER_PAYLOAD = {
    "timestamp": "2026-06-01T21:00:00",
    "total": 10.0,
    "isteam": False,
    "movie": "Test Movie",
    "cancellation": False,
    "products": [
        {"name": "Cola", "amount": 2, "price": 2.5, "category": "Drinks", "is_deposit": False, "vat_rate": 19.0},
        {"name": "Pfand", "amount": 2, "price": 1.0, "category": "Pfand", "is_deposit": True, "vat_rate": 19.0},
    ],
}


async def test_add_history_requires_auth(client):
    resp = await client.post(BASE + "/", json=ORDER_PAYLOAD)
    assert resp.status_code == 401


async def test_add_history_authenticated(client, auth_headers):
    resp = await client.post(BASE + "/", json=ORDER_PAYLOAD, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] == 10.0
    assert "transaction_id" in data


async def test_get_history_public(client, auth_headers):
    await client.post(BASE + "/", json=ORDER_PAYLOAD, headers=auth_headers)
    resp = await client.get(BASE + "/")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


async def test_total_excludes_pfand_when_flag_false(client, auth_headers):
    await client.post(BASE + "/", json=ORDER_PAYLOAD, headers=auth_headers)
    resp = await client.get(BASE + "/total?movie=Test Movie&pfand=false")
    assert resp.status_code == 200
    # total=10.0, Pfand: 2 x 1.0 = 2.0 deducted → 8.0
    assert resp.json() == pytest.approx(8.0)


async def test_total_includes_pfand_by_default(client, auth_headers):
    await client.post(BASE + "/", json=ORDER_PAYLOAD, headers=auth_headers)
    resp = await client.get(BASE + "/total?movie=Test Movie")
    assert resp.status_code == 200
    assert resp.json() == pytest.approx(10.0)


async def test_cancel_history_requires_auth(client, auth_headers):
    add = await client.post(BASE + "/", json=ORDER_PAYLOAD, headers=auth_headers)
    history_id = add.json()["data"]["_id"]
    resp = await client.post(BASE + f"/cancel/?_id={history_id}")
    assert resp.status_code == 401


async def test_cancel_history(client, auth_headers):
    add = await client.post(BASE + "/", json=ORDER_PAYLOAD, headers=auth_headers)
    history_id = add.json()["data"]["_id"]
    resp = await client.post(BASE + f"/cancel/?_id={history_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["cancellation"] is True
