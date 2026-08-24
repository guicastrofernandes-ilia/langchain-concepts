from datetime import date

from httpx import AsyncClient


def make_payload(**overrides):
    payload = {
        "artist": "The Beatles",
        "album": "Abbey Road",
        "year": 1969,
        "genre": "rock",
        "label": "Apple",
        "condition": "mint",
        "tracks": [{"title": "Come Together", "duration": "4:20"}],
    }
    payload.update(overrides)
    return payload


async def create_record(client: AsyncClient, **overrides):
    resp = await client.post("/records", json=make_payload(**overrides))
    assert resp.status_code == 201, resp.text
    return resp.json()


# --- T5: Create + Retrieve ---


async def test_create_record(client):
    payload = make_payload()
    resp = await client.post("/records", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    assert body["artist"] == payload["artist"]
    assert body["album"] == payload["album"]
    assert "created_at" in body


async def test_create_record_missing_artist(client):
    payload = make_payload()
    del payload["artist"]
    resp = await client.post("/records", json=payload)
    assert resp.status_code == 422
    assert "detail" in resp.json()


async def test_create_record_missing_album(client):
    payload = make_payload()
    del payload["album"]
    resp = await client.post("/records", json=payload)
    assert resp.status_code == 422
    assert "detail" in resp.json()


async def test_create_record_duplicate(client):
    await create_record(client)
    resp = await client.post("/records", json=make_payload())
    assert resp.status_code == 409


async def test_retrieve_record_by_id(client):
    created = await create_record(client)
    resp = await client.get(f"/records/{created['id']}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == created["id"]
    assert body["artist"] == "The Beatles"
    assert body["album"] == "Abbey Road"


async def test_retrieve_record_not_found(client):
    resp = await client.get("/records/999999")
    assert resp.status_code == 404


# --- T6: Update + Delete ---


async def test_update_record(client):
    created = await create_record(client)
    resp = await client.put(
        f"/records/{created['id']}",
        json=make_payload(album="Let It Be", label="Apple Corps"),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["album"] == "Let It Be"
    assert body["label"] == "Apple Corps"


async def test_update_record_not_found(client):
    resp = await client.put("/records/999999", json=make_payload())
    assert resp.status_code == 404


async def test_update_record_duplicate(client):
    await create_record(client)
    second = await create_record(client, artist="Pink Floyd", album="Dark Side of the Moon")
    resp = await client.put(
        f"/records/{second['id']}",
        json=make_payload(artist="The Beatles", album="Abbey Road"),
    )
    assert resp.status_code == 409


async def test_delete_record(client):
    created = await create_record(client)
    resp = await client.delete(f"/records/{created['id']}")
    assert resp.status_code == 204
    get_resp = await client.get(f"/records/{created['id']}")
    assert get_resp.status_code == 404


async def test_delete_record_not_found(client):
    resp = await client.delete("/records/999999")
    assert resp.status_code == 404


# --- T7: List with pagination ---


async def test_list_records(client):
    await create_record(client)
    await create_record(client, artist="Pink Floyd", album="Dark Side of the Moon")
    resp = await client.get("/records")
    assert resp.status_code == 200
    body = resp.json()
    assert set(body.keys()) == {"items", "total", "limit", "offset"}
    assert body["total"] == 2
    assert len(body["items"]) == 2
    assert body["limit"] == 50
    assert body["offset"] == 0


async def test_list_empty(client):
    resp = await client.get("/records")
    assert resp.status_code == 200
    body = resp.json()
    assert body["items"] == []
    assert body["total"] == 0


async def test_list_limit_clamp(client):
    for i in range(120):
        await create_record(client, artist=f"Artist {i}", album=f"Album {i}")
    resp = await client.get("/records", params={"limit": 200})
    assert resp.status_code == 200
    body = resp.json()
    assert body["limit"] == 100
    assert len(body["items"]) == 100
    assert body["total"] == 120


async def test_list_offset(client):
    for i in range(5):
        await create_record(client, artist=f"Artist {i}", album=f"Album {i}")
    resp = await client.get("/records", params={"offset": 2})
    assert resp.status_code == 200
    body = resp.json()
    assert body["offset"] == 2
    assert len(body["items"]) == 3
    assert body["total"] == 5


# --- T8: Search by artist, album, genre ---


async def test_search_by_artist(client):
    await create_record(client)
    await create_record(client, artist="Pink Floyd", album="Dark Side of the Moon")
    resp = await client.get("/records", params={"artist": "BEAT"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["artist"] == "The Beatles"


async def test_search_by_album(client):
    await create_record(client)
    await create_record(client, artist="Pink Floyd", album="Dark Side of the Moon")
    resp = await client.get("/records", params={"album": "abbey"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["album"] == "Abbey Road"


async def test_search_by_genre(client):
    await create_record(client)
    await create_record(client, artist="Miles Davis", album="Kind of Blue", genre="jazz")
    resp = await client.get("/records", params={"genre": "ROCK"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["genre"] == "rock"


async def test_search_combined(client):
    await create_record(client)
    await create_record(client, artist="The Beatles", album="Let It Be", genre="rock")
    await create_record(client, artist="The Beatles", album="Revolver", genre="pop")
    resp = await client.get("/records", params={"artist": "beat", "genre": "rock"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 2


# --- T9: Filter by year and condition ---


async def test_filter_by_year(client):
    await create_record(client)
    await create_record(client, artist="The Clash", album="London Calling", year=1980)
    resp = await client.get("/records", params={"year": 1980})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["year"] == 1980


async def test_filter_by_condition(client):
    await create_record(client)
    await create_record(client, artist="Nirvana", album="Nevermind", condition="good")
    resp = await client.get("/records", params={"condition": "mint"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["condition"] == "mint"


async def test_filter_combined(client):
    await create_record(client)
    await create_record(client, artist="The Clash", album="London Calling", year=1980, genre="punk")
    resp = await client.get("/records", params={"year": 1980, "genre": "punk"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["album"] == "London Calling"


# --- T10: Error handlers and edge cases ---


async def test_error_future_year(client):
    resp = await client.post("/records", json=make_payload(year=date.today().year + 5))
    assert resp.status_code == 422


async def test_error_year_below_1900(client):
    resp = await client.post("/records", json=make_payload(year=1899))
    assert resp.status_code == 422


async def test_error_invalid_condition(client):
    resp = await client.post("/records", json=make_payload(condition="pristine"))
    assert resp.status_code == 422


async def test_error_track_empty_title(client):
    resp = await client.post(
        "/records",
        json=make_payload(tracks=[{"title": "   ", "duration": "3:00"}]),
    )
    assert resp.status_code == 422


async def test_error_response_format(client):
    resp = await client.post("/records", json=make_payload(artist=""))
    assert resp.status_code == 422
    body = resp.json()
    assert "detail" in body
    assert isinstance(body["detail"], list)
    assert any("msg" in err for err in body["detail"])


async def test_db_unavailable_handler_registered(client):
    from record_catalog.main import create_app

    app = create_app()
    from sqlalchemy.exc import OperationalError

    assert OperationalError in app.exception_handlers
