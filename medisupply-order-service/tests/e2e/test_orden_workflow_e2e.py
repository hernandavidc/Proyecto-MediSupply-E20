import pytest
from datetime import datetime, timedelta


@pytest.mark.e2e
def test_complete_orden_workflow(e2e_client):
    """Test complete workflow: create bodega, vehiculo, and orden"""
    
    # 1. Create bodega
    bodega_data = {
        "nombre": "Bodega Principal",
        "direccion": "Av. Central 100",
        "id_pais": 1,
        "ciudad": "Bogotá"
    }
    bodega_response = e2e_client.post("/api/v1/bodegas", json=bodega_data)
    assert bodega_response.status_code == 201
    bodega_id = bodega_response.json()["id"]
    
    # 2. Create vehiculo
    vehiculo_data = {
        "id_conductor": 1,
        "placa": "E2E001",
        "tipo": "CAMION"
    }
    vehiculo_response = e2e_client.post("/api/v1/vehiculos", json=vehiculo_data)
    assert vehiculo_response.status_code == 201
    vehiculo_id = vehiculo_response.json()["id_vehiculo"]
    
    # 3. Create orden
    orden_data = {
        "fecha_entrega_estimada": (datetime.now() + timedelta(days=7)).isoformat(),
        "id_vehiculo": vehiculo_id,
        "id_cliente": 1,
        "id_vendedor": 1,
        "estado": "ABIERTO",
        "productos": []
    }
    orden_response = e2e_client.post("/api/v1/ordenes", json=orden_data)
    assert orden_response.status_code == 201
    orden_id = orden_response.json()["id"]
    
    # 4. Get orden and verify it has vehiculo assigned
    get_orden_response = e2e_client.get(f"/api/v1/ordenes/{orden_id}")
    assert get_orden_response.status_code == 200
    orden_data = get_orden_response.json()
    assert orden_data["id_vehiculo"] == vehiculo_id
    
    # 5. Create novedad for the orden
    novedad_data = {
        "id_pedido": orden_id,
        "tipo": "CANTIDAD_DIFERENTE",
        "descripcion": "Cliente solicitó 5 unidades adicionales"
    }
    novedad_response = e2e_client.post("/api/v1/novedades", json=novedad_data)
    assert novedad_response.status_code == 201
    novedad_id = novedad_response.json()["id"]
    
    # 6. Get novedades for the orden
    novedades_response = e2e_client.get(f"/api/v1/novedades?id_pedido={orden_id}")
    assert novedades_response.status_code == 200
    novedades = novedades_response.json()
    assert len(novedades) >= 1
    assert any(n["id"] == novedad_id for n in novedades)


@pytest.mark.e2e
def test_orden_filtering_e2e(e2e_client):
    """Test filtering ordenes by different criteria"""
    
    # Create multiple ordenes for different clients and vendors
    ordenes_data = [
        {"id_cliente": 1, "id_vendedor": 1, "estado": "ABIERTO", "productos": []},
        {"id_cliente": 1, "id_vendedor": 2, "estado": "EN_ALISTAMIENTO", "productos": []},
        {"id_cliente": 2, "id_vendedor": 1, "estado": "ABIERTO", "productos": []},
    ]
    
    created_ids = []
    for orden_data in ordenes_data:
        full_data = {
            "fecha_entrega_estimada": (datetime.now() + timedelta(days=7)).isoformat(),
            **orden_data
        }
        response = e2e_client.post("/api/v1/ordenes", json=full_data)
        assert response.status_code == 201
        created_ids.append(response.json()["id"])
    
    # Filter by cliente_id=1
    cliente_response = e2e_client.get("/api/v1/ordenes?id_cliente=1")
    assert cliente_response.status_code == 200
    cliente_ordenes = cliente_response.json()
    assert len([o for o in cliente_ordenes if o["id_cliente"] == 1]) >= 2
    
    # Filter by vendedor_id=1
    vendedor_response = e2e_client.get("/api/v1/ordenes?id_vendedor=1")
    assert vendedor_response.status_code == 200
    vendedor_ordenes = vendedor_response.json()
    assert len([o for o in vendedor_ordenes if o["id_vendedor"] == 1]) >= 2
    
    # Filter by estado=ABIERTO
    estado_response = e2e_client.get("/api/v1/ordenes?estado=ABIERTO")
    assert estado_response.status_code == 200
    estado_ordenes = estado_response.json()
    assert len([o for o in estado_ordenes if o["estado"] == "ABIERTO"]) >= 2
