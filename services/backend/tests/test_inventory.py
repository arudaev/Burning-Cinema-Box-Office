import pytest

from burningbackend.app.core.config import settings

BASE = f"/api/{settings.API_V1_STR}/inventory"

ITEM_PAYLOAD = {
    "name": "Cola",
    "amount": 10,
    "price": 2.5,
    "price_team": 1.5,
    "category": "Drinks",
    "vat_rate": 19.0,
    "is_deposit": False,
    "requires_deposit": True,
}


async def test_get_inventory_public(client):
    resp = await client.get(BASE + "/")
    assert resp.status_code == 200


async def test_add_inventory_requires_auth(client):
    resp = await client.post(BASE + "/", json=ITEM_PAYLOAD)
    assert resp.status_code == 401


async def test_add_inventory_authenticated(client, auth_headers):
    resp = await client.post(BASE + "/", json=ITEM_PAYLOAD, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["name"] == "Cola"
    assert data["vat_rate"] == 19.0
    assert data["requires_deposit"] is True


async def test_sold_guard_insufficient_stock(client, auth_headers):
    add = await client.post(BASE + "/", json=ITEM_PAYLOAD, headers=auth_headers)
    item_id = add.json()["data"]["_id"]
    resp = await client.put(BASE + f"/sold/{item_id}?amount=999", headers=auth_headers)
    assert resp.status_code == 422


async def test_sold_decrements_stock(client, auth_headers):
    add = await client.post(BASE + "/", json=ITEM_PAYLOAD, headers=auth_headers)
    item_id = add.json()["data"]["_id"]
    resp = await client.put(BASE + f"/sold/{item_id}?amount=3", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["amount"] == 7
    assert resp.json()["data"]["amount_sold"] == 3


async def test_delete_inventory_requires_auth(client, auth_headers):
    add = await client.post(BASE + "/", json=ITEM_PAYLOAD, headers=auth_headers)
    item_id = add.json()["data"]["_id"]
    resp = await client.delete(BASE + f"/{item_id}")
    assert resp.status_code == 401
