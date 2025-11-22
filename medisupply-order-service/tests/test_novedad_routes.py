import pytest
from datetime import datetime, timedelta


def test_create_novedad(client):
    """Test creating a novedad for an orden"""
    # First create an orden
    orden_data = {
        "fecha_entrega_estimada": (datetime.now() + timedelta(days=7)).isoformat(),
        "id_cliente": 1,
        "id_vendedor": 1,
        "estado": "ABIERTO"
    }
    orden_response = client.post("/api/v1/ordenes", json=orden_data)
    orden_id = orden_response.json()["id"]
    
    # Create novedad
    novedad_data = {
        "id_pedido": orden_id,
        "tipo": "DEVOLUCION",
        "descripcion": "Cliente rechazó el producto"
    }
    
    response = client.post("/api/v1/novedades", json=novedad_data)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["tipo"] == "DEVOLUCION"


def test_list_novedades(client):
    """Test listing all novedades"""
    response = client.get("/api/v1/novedades")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_novedad_by_id(client):
    """Test getting novedad by ID"""
    # Create orden and novedad
    orden_data = {
        "fecha_entrega_estimada": (datetime.now() + timedelta(days=7)).isoformat(),
        "id_cliente": 1,
        "id_vendedor": 1,
        "estado": "ABIERTO"
    }
    orden_response = client.post("/api/v1/ordenes", json=orden_data)
    orden_id = orden_response.json()["id"]
    
    novedad_data = {
        "id_pedido": orden_id,
        "tipo": "MAL_ESTADO",
        "descripcion": "Producto dañado"
    }
    create_response = client.post("/api/v1/novedades", json=novedad_data)
    novedad_id = create_response.json()["id"]
    
    # Get novedad
    get_response = client.get(f"/api/v1/novedades/{novedad_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == novedad_id


def test_get_novedades_by_orden(client):
    """Test getting novedades for a specific orden"""
    # Create orden
    orden_data = {
        "fecha_entrega_estimada": (datetime.now() + timedelta(days=7)).isoformat(),
        "id_cliente": 1,
        "id_vendedor": 1,
        "estado": "ABIERTO"
    }
    orden_response = client.post("/api/v1/ordenes", json=orden_data)
    orden_id = orden_response.json()["id"]
    
    # Create multiple novedades for this orden
    tipos = ["DEVOLUCION", "CANTIDAD_DIFERENTE"]
    for tipo in tipos:
        novedad_data = {
            "id_pedido": orden_id,
            "tipo": tipo,
            "descripcion": f"Novedad tipo {tipo}"
        }
        client.post("/api/v1/novedades", json=novedad_data)
    
    # Get novedades for orden
    response = client.get(f"/api/v1/novedades?id_pedido={orden_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_create_novedad_for_nonexistent_orden(client):
    """Test creating novedad for non-existent orden should fail"""
    novedad_data = {
        "id_pedido": 99999,
        "tipo": "DEVOLUCION",
        "descripcion": "Test"
    }
    
    response = client.post("/api/v1/novedades", json=novedad_data)
    # Should fail with 400 or 404
    assert response.status_code in [400, 404]

