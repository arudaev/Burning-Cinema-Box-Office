from datetime import datetime, timedelta

import pytest

from burningbackend.app.core.config import settings
from burningbackend.app.models.movie import Movie

BASE = f"/api/{settings.API_V1_STR}/reservation"
MOVIES_BASE = f"/api/{settings.API_V1_STR}/movies"

RESERVATION_PAYLOAD = {
    "timestamp": "2026-06-01T19:00:00",
    "movie": "Test Movie",
    "seat_number": 7,
    "email": "test@example.com",
    "scanned": False,
    "retention_until": "2026-07-01T20:00:00",
}

MOVIE_PAYLOAD = {
    "name": "Test Movie",
    "datetime": "2026-06-01T20:00:00",
    "room": "Kino 1",
}


async def test_add_reservation_requires_auth(client):
    resp = await client.post(BASE + "/reservation/add", json=RESERVATION_PAYLOAD)
    assert resp.status_code == 401


async def test_add_reservation_sets_retention_until(client, auth_headers):
    await client.post(MOVIES_BASE + "/", json=MOVIE_PAYLOAD, headers=auth_headers)
    resp = await client.post(BASE + "/reservation/add", json=RESERVATION_PAYLOAD, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    # retention_until = movie.datetime (2026-06-01T20:00) + 30 days
    expected = datetime(2026, 7, 1, 20, 0, 0)
    actual = datetime.fromisoformat(data["retention_until"].replace("Z", "+00:00")).replace(tzinfo=None)
    assert actual == expected


async def test_scan_reservation(client, auth_headers):
    await client.post(MOVIES_BASE + "/", json=MOVIE_PAYLOAD, headers=auth_headers)
    add = await client.post(BASE + "/reservation/add", json=RESERVATION_PAYLOAD, headers=auth_headers)
    res_id = add.json()["data"]["_id"]

    resp = await client.post(BASE + f"/reservation/scan/{res_id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["scanned"] is True
    assert data["scan_timestamp"] is not None


async def test_scan_already_scanned_returns_400(client, auth_headers):
    await client.post(MOVIES_BASE + "/", json=MOVIE_PAYLOAD, headers=auth_headers)
    add = await client.post(BASE + "/reservation/add", json=RESERVATION_PAYLOAD, headers=auth_headers)
    res_id = add.json()["data"]["_id"]

    await client.post(BASE + f"/reservation/scan/{res_id}", headers=auth_headers)
    resp = await client.post(BASE + f"/reservation/scan/{res_id}", headers=auth_headers)
    assert resp.status_code == 400


async def test_scan_requires_auth(client, auth_headers):
    await client.post(MOVIES_BASE + "/", json=MOVIE_PAYLOAD, headers=auth_headers)
    add = await client.post(BASE + "/reservation/add", json=RESERVATION_PAYLOAD, headers=auth_headers)
    res_id = add.json()["data"]["_id"]
    resp = await client.post(BASE + f"/reservation/scan/{res_id}")
    assert resp.status_code == 401
