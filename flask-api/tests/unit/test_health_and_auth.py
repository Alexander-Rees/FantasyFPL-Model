from unittest.mock import patch

import pytest


@pytest.fixture
def client():
    with patch("app_with_db.get_db_connection", return_value=None):
        with patch("app_with_db.get_redis_client", return_value=None):
            from app_with_db import app

            app.config["TESTING"] = True
            with app.test_client() as test_client:
                yield test_client


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "ok"
    assert "response_time_ms" in body


def test_secret_key_comes_from_env(client):
    from app_with_db import app

    assert app.config["SECRET_KEY"] == "test-jwt-secret-not-for-production-use"


def test_internal_token_rejected(client):
    response = client.post(
        "/api/optimize",
        json={"budget": 100, "players": []},
        headers={"X-Internal-Token": "wrong-token"},
    )
    assert response.status_code == 401
    assert "Token" in response.get_json().get("message", "")
