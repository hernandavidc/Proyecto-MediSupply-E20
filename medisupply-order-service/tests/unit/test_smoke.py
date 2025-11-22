from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns expected structure"""
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert "message" in data
    assert "version" in data
    assert "health" in data
    assert data["health"] == "/order-healthz"


def test_health_endpoint():
    """Test health check endpoint"""
    r = client.get("/order-healthz")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data


def test_ordenes_list():
    """Test ordenes list endpoint returns 200"""
    r = client.get("/api/v1/ordenes")
    assert r.status_code == 200


def test_bodegas_list():
    """Test bodegas list endpoint returns 200"""
    r = client.get("/api/v1/bodegas")
    assert r.status_code == 200


def test_vehiculos_list():
    """Test vehiculos list endpoint returns 200"""
    r = client.get("/api/v1/vehiculos")
    assert r.status_code == 200

