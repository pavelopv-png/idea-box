import pytest
from fastapi.testclient import TestClient

from app_final import app, ideas


@pytest.fixture
def client():
    ideas.clear()
    with TestClient(app) as test_client:
        yield test_client
    ideas.clear()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version(client):
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": "1.0.0"}


def test_create_idea(client):
    response = client.post(
        "/ideas",
        json={"title": "Планировка квартиры", "description": "Под привычки жильцов"},
    )
    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "title": "Планировка квартиры",
        "description": "Под привычки жильцов",
    }


def test_list_ideas(client):
    assert client.get("/ideas").json() == []
    created = client.post("/ideas", json={"title": "Первая идея"}).json()
    response = client.get("/ideas")
    assert response.status_code == 200
    assert response.json() == [created]


def test_get_idea(client):
    created = client.post("/ideas", json={"title": "Первая идея"}).json()
    response = client.get(f"/ideas/{created['id']}")
    assert response.status_code == 200
    assert response.json() == created


def test_idea_not_found(client):
    response = client.get("/ideas/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Идея не найдена"}


@pytest.mark.parametrize("title", ["", "   "])
def test_blank_title(client, title):
    response = client.post("/ideas", json={"title": title})
    assert response.status_code == 422
    assert client.get("/ideas").json() == []


def test_strip_title(client):
    response = client.post("/ideas", json={"title": "  Новая идея  "})
    assert response.status_code == 201
    assert response.json()["title"] == "Новая идея"
