import pytest
from datetime import datetime, timedelta


def test_create_orden_producto_via_api(client, db_session):
    """Test creating orden_producto through API"""
    # First create an orden
    orden_data = {
        "fecha_entrega_estimada": (datetime.now() + timedelta(days=7)).isoformat(),
        "id_cliente": 1,
        "id_vendedor": 1,
        "estado": "ABIERTO",
        "productos": []
    }
    orden_response = client.post("/api/v1/ordenes", json=orden_data)
    assert orden_response.status_code == 201
    orden_id = orden_response.json()["id"]
    
    # Create orden_producto
    orden_producto_data = {
        "id_orden": orden_id,
        "id_producto": 100,
        "cantidad": 5
    }
    
    response = client.post("/api/v1/orden-productos", json=orden_producto_data)
    assert response.status_code == 201
    data = response.json()
    assert data["id_orden"] == orden_id
    assert data["id_producto"] == 100
    assert data["cantidad"] == 5


def test_list_orden_productos_via_api(client, db_session):
    """Test listing orden_productos through API"""
    # Create orden first
    orden_data = {
        "fecha_entrega_estimada": (datetime.now() + timedelta(days=7)).isoformat(),
        "id_cliente": 1,
        "id_vendedor": 1,
        "estado": "ABIERTO",
        "productos": []
    }
    orden_response = client.post("/api/v1/ordenes", json=orden_data)
    orden_id = orden_response.json()["id"]
    
    # Create some orden_productos
    for i in range(3):
        orden_producto_data = {
            "id_orden": orden_id,
            "id_producto": 100 + i,
            "cantidad": 5 + i
        }
        client.post("/api/v1/orden-productos", json=orden_producto_data)
    
    # List all
    response = client.get("/api/v1/orden-productos")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3


def test_list_productos_by_orden(client, db_session):
    """Test listing productos for a specific orden"""
    # Create orden
    orden_data = {
        "fecha_entrega_estimada": (datetime.now() + timedelta(days=7)).isoformat(),
        "id_cliente": 1,
        "id_vendedor": 1,
        "estado": "ABIERTO",
        "productos": []
    }
    orden_response = client.post("/api/v1/ordenes", json=orden_data)
    orden_id = orden_response.json()["id"]
    
    # Create orden_productos
    for i in range(2):
        orden_producto_data = {
            "id_orden": orden_id,
            "id_producto": 200 + i,
            "cantidad": 10 + i
        }
        client.post("/api/v1/orden-productos", json=orden_producto_data)
    
    # Get productos for this orden
    response = client.get(f"/api/v1/orden-productos/orden/{orden_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    for item in data:
        assert item["id_orden"] == orden_id


def test_get_orden_producto_by_id(client, db_session):
    """Test getting specific orden_producto by orden_id and producto_id"""
    # Create orden
    orden_data = {
        "fecha_entrega_estimada": (datetime.now() + timedelta(days=7)).isoformat(),
        "id_cliente": 1,
        "id_vendedor": 1,
        "estado": "ABIERTO",
        "productos": []
    }
    orden_response = client.post("/api/v1/ordenes", json=orden_data)
    orden_id = orden_response.json()["id"]
    
    # Create orden_producto
    producto_id = 300
    orden_producto_data = {
        "id_orden": orden_id,
        "id_producto": producto_id,
        "cantidad": 15
    }
    client.post("/api/v1/orden-productos", json=orden_producto_data)
    
    # Get specific orden_producto
    response = client.get(f"/api/v1/orden-productos/{orden_id}/{producto_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id_orden"] == orden_id
    assert data["id_producto"] == producto_id
    assert data["cantidad"] == 15


def test_get_nonexistent_orden_producto(client):
    """Test getting non-existent orden_producto returns 404"""
    response = client.get("/api/v1/orden-productos/99999/99999")
    assert response.status_code == 404


def test_update_orden_producto(client, db_session):
    """Test updating orden_producto quantity"""
    # Create orden
    orden_data = {
        "fecha_entrega_estimada": (datetime.now() + timedelta(days=7)).isoformat(),
        "id_cliente": 1,
        "id_vendedor": 1,
        "estado": "ABIERTO",
        "productos": []
    }
    orden_response = client.post("/api/v1/ordenes", json=orden_data)
    orden_id = orden_response.json()["id"]
    
    # Create orden_producto
    producto_id = 400
    orden_producto_data = {
        "id_orden": orden_id,
        "id_producto": producto_id,
        "cantidad": 20
    }
    client.post("/api/v1/orden-productos", json=orden_producto_data)
    
    # Update cantidad
    update_data = {"cantidad": 50}
    response = client.put(f"/api/v1/orden-productos/{orden_id}/{producto_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["cantidad"] == 50


def test_delete_orden_producto(client, db_session):
    """Test deleting orden_producto"""
    # Create orden
    orden_data = {
        "fecha_entrega_estimada": (datetime.now() + timedelta(days=7)).isoformat(),
        "id_cliente": 1,
        "id_vendedor": 1,
        "estado": "ABIERTO",
        "productos": []
    }
    orden_response = client.post("/api/v1/ordenes", json=orden_data)
    orden_id = orden_response.json()["id"]
    
    # Create orden_producto
    producto_id = 500
    orden_producto_data = {
        "id_orden": orden_id,
        "id_producto": producto_id,
        "cantidad": 25
    }
    client.post("/api/v1/orden-productos", json=orden_producto_data)
    
    # Delete
    response = client.delete(f"/api/v1/orden-productos/{orden_id}/{producto_id}")
    assert response.status_code == 204
    
    # Verify it's gone
    get_response = client.get(f"/api/v1/orden-productos/{orden_id}/{producto_id}")
    assert get_response.status_code == 404

