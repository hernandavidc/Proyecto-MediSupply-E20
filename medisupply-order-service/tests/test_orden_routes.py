import pytest
from datetime import datetime, timedelta


def test_create_orden_via_api(client):
    """Test creating orden through API"""
    orden_data = {
        "fecha_entrega_estimada": (datetime.now() + timedelta(days=7)).isoformat(),
        "id_cliente": 1,
        "id_vendedor": 1,
        "estado": "ABIERTO"
    }
    
    response = client.post("/api/v1/ordenes", json=orden_data)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["id_cliente"] == 1


def test_list_ordenes_via_api(client):
    """Test listing ordenes through API"""
    response = client.get("/api/v1/ordenes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_orden_by_id(client):
    """Test getting specific orden by ID"""
    # First create an orden
    orden_data = {
        "fecha_entrega_estimada": (datetime.now() + timedelta(days=7)).isoformat(),
        "id_cliente": 1,
        "id_vendedor": 1,
        "estado": "ABIERTO"
    }
    
    create_response = client.post("/api/v1/ordenes", json=orden_data)
    assert create_response.status_code == 201
    orden_id = create_response.json()["id"]
    
    # Get the orden
    get_response = client.get(f"/api/v1/ordenes/{orden_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == orden_id


def test_get_nonexistent_orden(client):
    """Test getting non-existent orden returns 404"""
    response = client.get("/api/v1/ordenes/99999")
    assert response.status_code == 404


def test_update_orden_estado(client):
    """Test updating orden status"""
    # Create orden
    orden_data = {
        "fecha_entrega_estimada": (datetime.now() + timedelta(days=7)).isoformat(),
        "id_cliente": 1,
        "id_vendedor": 1,
        "estado": "ABIERTO"
    }
    
    create_response = client.post("/api/v1/ordenes", json=orden_data)
    orden_id = create_response.json()["id"]
    
    # Update estado
    update_data = {"estado": "EN_ALISTAMIENTO"}
    update_response = client.patch(f"/api/v1/ordenes/{orden_id}", json=update_data)
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["estado"] == "EN_ALISTAMIENTO"


def test_filter_ordenes_by_cliente(client):
    """Test filtering ordenes by cliente_id"""
    # Create ordenes for different clients
    for cliente_id in [1, 1, 2]:
        orden_data = {
            "fecha_entrega_estimada": (datetime.now() + timedelta(days=7)).isoformat(),
            "id_cliente": cliente_id,
            "id_vendedor": 1,
            "estado": "ABIERTO"
        }
        client.post("/api/v1/ordenes", json=orden_data)
    
    # Filter by cliente_id=1
    response = client.get("/api/v1/ordenes?id_cliente=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    for orden in data:
        assert orden["id_cliente"] == 1

