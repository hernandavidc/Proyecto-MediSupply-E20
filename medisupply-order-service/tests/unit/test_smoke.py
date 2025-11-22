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
    """Test health check endpoint - may return different structures"""
    r = client.get("/order-healthz")
    # Health check can be 200 (healthy) or 503 (DB not available in test env)
    assert r.status_code in [200, 503]
    data = r.json()
    # Can have either 'status' directly or inside 'detail'
    assert "status" in data or ("detail" in data and "status" in data["detail"])
