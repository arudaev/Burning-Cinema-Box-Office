import pytest

from burningbackend.app.core.config import settings

BASE = f"/api/{settings.API_V1_STR}/report"
MOVIES_BASE = f"/api/{settings.API_V1_STR}/movies"
HISTORY_BASE = f"/api/{settings.API_V1_STR}/history"

MOVIE_PAYLOAD = {
    "name": "Report Movie",
    "datetime": "2026-06-01T20:00:00",
    "room": "Kino 1",
}

ORDER_PAYLOAD = {
    "timestamp": "2026-06-01T21:00:00",
    "total": 5.0,
    "isteam": False,
    "movie": "Report Movie",
    "cancellation": False,
    "products": [
        {"name": "Ticket", "amount": 1, "price": 5.0, "category": "Tickets", "is_deposit": False, "vat_rate": 7.0},
    ],
}


async def test_report_requires_movie_or_date(client):
    resp = await client.get(BASE + "/report")
    assert resp.status_code == 422


async def test_report_by_movie(client, auth_headers):
    await client.post(MOVIES_BASE + "/", json=MOVIE_PAYLOAD, headers=auth_headers)
    await client.post(HISTORY_BASE + "/", json=ORDER_PAYLOAD, headers=auth_headers)
    resp = await client.get(BASE + "/report?movie=Report Movie")
    assert resp.status_code == 200
    assert "application/vnd.openxmlformats" in resp.headers["content-type"]


async def test_report_by_date_range(client, auth_headers):
    await client.post(MOVIES_BASE + "/", json=MOVIE_PAYLOAD, headers=auth_headers)
    await client.post(HISTORY_BASE + "/", json=ORDER_PAYLOAD, headers=auth_headers)
    resp = await client.get(BASE + "/report?start_date=2026-06-01T00:00:00&end_date=2026-06-02T00:00:00")
    assert resp.status_code == 200
    assert "application/vnd.openxmlformats" in resp.headers["content-type"]
