import asyncio

import pytest
from fastapi.testclient import TestClient

from app import health
from app.config import get_settings
from app.main import app


@pytest.fixture
def client(settings):
    app.dependency_overrides[get_settings] = lambda: settings
    yield TestClient(app)
    app.dependency_overrides.clear()


async def ok(_settings):
    return None


async def refused(_settings):
    raise ConnectionRefusedError


async def hangs(_settings):
    await asyncio.sleep(10)


def test_health_returns_ok_when_dependencies_respond(client, monkeypatch):
    monkeypatch.setattr(health, "CHECKS", {"database": ok, "queue": ok})

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {"database": "ok", "queue": "ok"}}


@pytest.mark.parametrize("broken", [refused, hangs])
def test_health_returns_503_when_a_dependency_fails(client, monkeypatch, broken):
    monkeypatch.setattr(health, "CHECKS", {"database": ok, "queue": broken})

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json()["checks"] == {"database": "ok", "queue": "error"}
