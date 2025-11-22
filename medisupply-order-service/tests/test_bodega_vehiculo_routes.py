import pytest


def test_create_bodega(client):
    """Test creating a bodega"""
    bodega_data = {
        "nombre": "Bodega Central",
        "direccion": "Av. Principal 123",
        "id_pais": 1,
        "ciudad": "Bogotá",
        "latitud": 4.60971,
        "longitud": -74.08175
    }
    
    response = client.post("/api/v1/bodegas", json=bodega_data)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["nombre"] == "Bodega Central"


def test_list_bodegas(client):
    """Test listing bodegas"""
    response = client.get("/api/v1/bodegas")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_bodega_by_id(client):
    """Test getting bodega by ID"""
    # Create bodega first
    bodega_data = {
        "nombre": "Bodega Norte",
        "direccion": "Calle 100 #20-30",
        "id_pais": 1,
        "ciudad": "Medellín"
    }
    
    create_response = client.post("/api/v1/bodegas", json=bodega_data)
    bodega_id = create_response.json()["id"]
    
    # Get bodega
    get_response = client.get(f"/api/v1/bodegas/{bodega_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == bodega_id


def test_create_vehiculo(client):
    """Test creating a vehiculo"""
    vehiculo_data = {
        "id_conductor": 1,
        "placa": "ABC123",
        "tipo": "CAMION"
    }
    
    response = client.post("/api/v1/vehiculos", json=vehiculo_data)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["placa"] == "ABC123"
    assert data["tipo"] == "CAMION"


def test_list_vehiculos(client):
    """Test listing vehiculos"""
    response = client.get("/api/v1/vehiculos")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_vehiculo_by_id(client):
    """Test getting vehiculo by ID"""
    # Create vehiculo first
    vehiculo_data = {
        "id_conductor": 2,
        "placa": "XYZ789",
        "tipo": "VAN"
    }
    
    create_response = client.post("/api/v1/vehiculos", json=vehiculo_data)
    vehiculo_id = create_response.json()["id"]
    
    # Get vehiculo
    get_response = client.get(f"/api/v1/vehiculos/{vehiculo_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == vehiculo_id
    assert data["tipo"] == "VAN"


def test_vehiculo_placa_unique(client):
    """Test that vehiculo placa must be unique"""
    vehiculo_data = {
        "id_conductor": 1,
        "placa": "UNIQUE123",
        "tipo": "CAMION"
    }
    
    # First creation should succeed
    response1 = client.post("/api/v1/vehiculos", json=vehiculo_data)
    assert response1.status_code == 201
    
    # Second creation with same placa should fail
    response2 = client.post("/api/v1/vehiculos", json=vehiculo_data)
    assert response2.status_code in [400, 409]  # Bad request or Conflict

