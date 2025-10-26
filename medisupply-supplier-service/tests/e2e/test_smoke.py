import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.smoke
def test_paises():
    r = client.get("/api/v1/paises")
    assert r.status_code == 200


@pytest.mark.smoke
def test_proveedores_list():
    r = client.get("/api/v1/proveedores")
    assert r.status_code == 200
