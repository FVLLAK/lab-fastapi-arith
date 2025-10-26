from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_add():
    r = client.post("/add", json={"a": 2, "b": 3})
    assert r.status_code == 200
    assert r.json()["result"] == 5


def test_sub():
    r = client.post("/sub", json={"a": 10, "b": 4})
    assert r.status_code == 200
    assert r.json()["result"] == 6


def test_mul():
    r = client.post("/mul", json={"a": 6, "b": 7})
    assert r.status_code == 200
    assert r.json()["result"] == 42


def test_div():
    r = client.post("/div", json={"a": 10, "b": 2})
    assert r.status_code == 200
    assert r.json()["result"] == 5


def test_div_by_zero():
    r = client.post("/div", json={"a": 10, "b": 0})
    assert r.status_code == 400
    assert "Division par zéro" in r.json()["detail"]
