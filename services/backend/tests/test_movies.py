from datetime import datetime

import pytest

from burningbackend.app.core.config import settings

BASE = f"/api/{settings.API_V1_STR}/movies"

MOVIE_PAYLOAD = {
    "name": "Test Movie",
    "datetime": "2026-06-01T20:00:00",
    "room": "Kino 1",
}


async def test_get_movies_public(client):
    resp = await client.get(BASE + "/")
    assert resp.status_code == 200


async def test_add_movie_requires_auth(client):
    resp = await client.post(BASE + "/", json=MOVIE_PAYLOAD)
    assert resp.status_code == 401


async def test_add_movie_authenticated(client, auth_headers):
    resp = await client.post(BASE + "/", json=MOVIE_PAYLOAD, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == "Test Movie"
    assert resp.json()["data"]["active"] is True


async def test_get_movie_by_name(client, auth_headers):
    await client.post(BASE + "/", json=MOVIE_PAYLOAD, headers=auth_headers)
    resp = await client.get(BASE + "/name/Test Movie")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Test Movie"


async def test_update_movie_requires_auth(client, auth_headers):
    add = await client.post(BASE + "/", json=MOVIE_PAYLOAD, headers=auth_headers)
    movie_id = add.json()["data"]["_id"]
    resp = await client.put(BASE + f"/{movie_id}", json={"room": "Kino 2"})
    assert resp.status_code == 401


async def test_soft_delete_sets_active_false(client, auth_headers):
    add = await client.post(BASE + "/", json=MOVIE_PAYLOAD, headers=auth_headers)
    movie_id = add.json()["data"]["_id"]
    resp = await client.delete(BASE + f"/{movie_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["active"] is False


async def test_deleted_movie_excluded_from_list(client, auth_headers):
    add = await client.post(BASE + "/", json=MOVIE_PAYLOAD, headers=auth_headers)
    movie_id = add.json()["data"]["_id"]
    await client.delete(BASE + f"/{movie_id}", headers=auth_headers)
    resp = await client.get(BASE + "/")
    names = [m["name"] for m in resp.json()]
    assert "Test Movie" not in names
