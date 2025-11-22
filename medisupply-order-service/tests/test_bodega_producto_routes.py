import pytest
from app.services.bodega_service import BodegaService
from app.schemas.bodega_schema import BodegaCreate


def test_create_bodega_producto_via_api(client, db_session):
    """Test creating bodega_producto through API"""
    # Create bodega first
    bodega_svc = BodegaService(db_session)
    bodega_data = BodegaCreate(
        nombre="Bodega API",
        direccion="Calle API",
        id_pais=1,
        ciudad="Bogotá"
    )
    bodega = bodega_svc.crear_bodega(bodega_data)
    
    # Create bodega_producto
    bp_data = {
        "id_bodega": bodega.id,
        "id_producto": 1000,
        "lote": "LOTE_API_001",
        "cantidad": 100,
        "dias_alistamiento": 2
    }
    
    response = client.post("/api/v1/bodega-productos/", json=bp_data)
    assert response.status_code == 201
    data = response.json()
    assert data["id_bodega"] == bodega.id
    assert data["id_producto"] == 1000
    assert data["lote"] == "LOTE_API_001"


def test_list_bodega_productos_via_api(client, db_session):
    """Test listing bodega_productos through API"""
    response = client.get("/api/v1/bodega-productos/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_bodega_productos_with_filters(client):
    """Test filtering bodega_productos via API"""
    # Create bodega via API
    bodega_data = {
        "nombre": "Bodega Filter API",
        "direccion": "Calle Filter",
        "id_pais": 1,
        "ciudad": "Medellín"
    }
    bodega_response = client.post("/api/v1/bodegas/", json=bodega_data)
    bodega = bodega_response.json()
    bodega_id = bodega["id"]
    
    # Create bodega_producto
    bp_data = {
        "id_bodega": bodega_id,
        "id_producto": 2000,
        "lote": "LOTE_FILTER",
        "cantidad": 50,
        "dias_alistamiento": 1
    }
    client.post("/api/v1/bodega-productos/", json=bp_data)
    
    # Filter by bodega
    response = client.get(f"/api/v1/bodega-productos/?id_bodega={bodega_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    
    # Filter by producto
    response = client.get("/api/v1/bodega-productos/?id_producto=2000")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_list_productos_by_bodega(client, db_session):
    """Test listing productos for a specific bodega"""
    # Create bodega
    bodega_svc = BodegaService(db_session)
    bodega_data = BodegaCreate(
        nombre="Bodega Specific",
        direccion="Calle Specific",
        id_pais=1,
        ciudad="Cali"
    )
    bodega = bodega_svc.crear_bodega(bodega_data)
    
    # Create bodega_productos
    for i in range(2):
        bp_data = {
            "id_bodega": bodega.id,
            "id_producto": 3000 + i,
            "lote": f"LOTE_SPEC_{i}",
            "cantidad": 30 + i*10,
            "dias_alistamiento": 2
        }
        client.post("/api/v1/bodega-productos", json=bp_data)
    
    # Get productos for this bodega
    response = client.get(f"/api/v1/bodega-productos/bodega/{bodega.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_get_bodega_producto_by_composite_key(client, db_session):
    """Test getting specific bodega_producto by composite key"""
    # Create bodega
    bodega_svc = BodegaService(db_session)
    bodega_data = BodegaCreate(
        nombre="Bodega Get Key",
        direccion="Calle Get Key",
        id_pais=1,
        ciudad="Bogotá"
    )
    bodega = bodega_svc.crear_bodega(bodega_data)
    
    # Create bodega_producto
    bp_data = {
        "id_bodega": bodega.id,
        "id_producto": 4000,
        "lote": "LOTE_KEY",
        "cantidad": 75,
        "dias_alistamiento": 3
    }
    client.post("/api/v1/bodega-productos", json=bp_data)
    
    # Get specific bodega_producto
    response = client.get(f"/api/v1/bodega-productos/{bodega.id}/{4000}/LOTE_KEY")
    assert response.status_code == 200
    data = response.json()
    assert data["id_bodega"] == bodega.id
    assert data["id_producto"] == 4000
    assert data["lote"] == "LOTE_KEY"


def test_get_nonexistent_bodega_producto(client):
    """Test getting non-existent bodega_producto returns 404"""
    response = client.get("/api/v1/bodega-productos/99999/99999/NOEXISTE")
    assert response.status_code == 404


def test_update_bodega_producto(client, db_session):
    """Test updating bodega_producto"""
    # Create bodega
    bodega_svc = BodegaService(db_session)
    bodega_data = BodegaCreate(
        nombre="Bodega Update API",
        direccion="Calle Update API",
        id_pais=1,
        ciudad="Bogotá"
    )
    bodega = bodega_svc.crear_bodega(bodega_data)
    
    # Create bodega_producto
    bp_data = {
        "id_bodega": bodega.id,
        "id_producto": 5000,
        "lote": "LOTE_UPDATE",
        "cantidad": 100,
        "dias_alistamiento": 2
    }
    client.post("/api/v1/bodega-productos", json=bp_data)
    
    # Update
    update_data = {"cantidad": 200, "dias_alistamiento": 5}
    response = client.put(
        f"/api/v1/bodega-productos/{bodega.id}/{5000}/LOTE_UPDATE",
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["cantidad"] == 200
    assert data["dias_alistamiento"] == 5


def test_update_nonexistent_bodega_producto(client):
    """Test updating non-existent bodega_producto returns 404"""
    update_data = {"cantidad": 999}
    response = client.put(
        "/api/v1/bodega-productos/99999/99999/NOEXISTE",
        json=update_data
    )
    assert response.status_code == 404


def test_delete_bodega_producto(client, db_session):
    """Test deleting bodega_producto"""
    # Create bodega
    bodega_svc = BodegaService(db_session)
    bodega_data = BodegaCreate(
        nombre="Bodega Delete API",
        direccion="Calle Delete API",
        id_pais=1,
        ciudad="Bogotá"
    )
    bodega = bodega_svc.crear_bodega(bodega_data)
    
    # Create bodega_producto
    bp_data = {
        "id_bodega": bodega.id,
        "id_producto": 6000,
        "lote": "LOTE_DELETE",
        "cantidad": 50,
        "dias_alistamiento": 1
    }
    client.post("/api/v1/bodega-productos", json=bp_data)
    
    # Delete
    response = client.delete(f"/api/v1/bodega-productos/{bodega.id}/{6000}/LOTE_DELETE")
    assert response.status_code == 204
    
    # Verify it's gone
    get_response = client.get(f"/api/v1/bodega-productos/{bodega.id}/{6000}/LOTE_DELETE")
    assert get_response.status_code == 404


def test_delete_nonexistent_bodega_producto(client):
    """Test deleting non-existent bodega_producto returns 404"""
    response = client.delete("/api/v1/bodega-productos/99999/99999/NOEXISTE")
    assert response.status_code == 404


def test_list_bodega_productos_with_coordinates(client):
    """Test listing bodega_productos with GPS coordinates for delivery forecast"""
    # Create bodega with coordinates via API
    bodega_data = {
        "nombre": "Bodega con GPS API",
        "direccion": "Calle GPS API",
        "id_pais": 1,
        "ciudad": "Bogotá",
        "latitud": 4.7110,
        "longitud": -74.0721
    }
    bodega_response = client.post("/api/v1/bodegas/", json=bodega_data)
    bodega = bodega_response.json()
    bodega_id = bodega["id"]
    
    # Create bodega_producto
    bp_data = {
        "id_bodega": bodega_id,
        "id_producto": 7000,
        "lote": "LOTE_GPS",
        "cantidad": 80,
        "dias_alistamiento": 2
    }
    client.post("/api/v1/bodega-productos/", json=bp_data)
    
    # List with coordinates (should include pronostico_entrega)
    response = client.get(
        f"/api/v1/bodega-productos/?id_bodega={bodega_id}&latitud=4.6097&longitud=-74.0817"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["pronostico_entrega"] is not None

