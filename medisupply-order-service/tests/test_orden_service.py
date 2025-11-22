import pytest
from datetime import datetime, timedelta
from app.services.orden_service import OrdenService
from app.models.orden import EstadoOrden
from fastapi import HTTPException


def test_crear_orden(db_session):
    """Test creating a new orden"""
    orden_svc = OrdenService(db_session)
    
    orden_data = {
        "fecha_entrega_estimada": datetime.now() + timedelta(days=7),
        "id_cliente": 1,
        "id_vendedor": 1,
        "estado": EstadoOrden.ABIERTO
    }
    
    orden = orden_svc.crear_orden(orden_data)
    assert orden.id is not None
    assert orden.id_cliente == 1
    assert orden.id_vendedor == 1
    assert orden.estado == EstadoOrden.ABIERTO


def test_listar_ordenes(db_session):
    """Test listing all ordenes"""
    orden_svc = OrdenService(db_session)
    
    # Create two ordenes
    for i in range(2):
        orden_data = {
            "fecha_entrega_estimada": datetime.now() + timedelta(days=7+i),
            "id_cliente": i+1,
            "id_vendedor": i+1,
            "estado": EstadoOrden.ABIERTO
        }
        orden_svc.crear_orden(orden_data)
    
    ordenes = orden_svc.listar_ordenes()
    assert len(ordenes) >= 2


def test_obtener_orden(db_session):
    """Test getting a specific orden by ID"""
    orden_svc = OrdenService(db_session)
    
    orden_data = {
        "fecha_entrega_estimada": datetime.now() + timedelta(days=7),
        "id_cliente": 1,
        "id_vendedor": 1,
        "estado": EstadoOrden.ABIERTO
    }
    
    orden = orden_svc.crear_orden(orden_data)
    retrieved = orden_svc.obtener_orden(orden.id)
    
    assert retrieved.id == orden.id
    assert retrieved.id_cliente == orden.id_cliente


def test_obtener_orden_inexistente(db_session):
    """Test getting non-existent orden raises exception"""
    orden_svc = OrdenService(db_session)
    
    with pytest.raises(HTTPException) as exc_info:
        orden_svc.obtener_orden(99999)
    assert exc_info.value.status_code == 404


def test_actualizar_estado_orden(db_session):
    """Test updating orden status"""
    orden_svc = OrdenService(db_session)
    
    orden_data = {
        "fecha_entrega_estimada": datetime.now() + timedelta(days=7),
        "id_cliente": 1,
        "id_vendedor": 1,
        "estado": EstadoOrden.ABIERTO
    }
    
    orden = orden_svc.crear_orden(orden_data)
    
    # Update status
    actualizado = orden_svc.actualizar_estado(orden.id, {"estado": EstadoOrden.EN_ALISTAMIENTO})
    assert actualizado.estado == EstadoOrden.EN_ALISTAMIENTO


def test_filtrar_ordenes_por_cliente(db_session):
    """Test filtering ordenes by cliente_id"""
    orden_svc = OrdenService(db_session)
    
    # Create ordenes for different clients
    for cliente_id in [1, 1, 2]:
        orden_data = {
            "fecha_entrega_estimada": datetime.now() + timedelta(days=7),
            "id_cliente": cliente_id,
            "id_vendedor": 1,
            "estado": EstadoOrden.ABIERTO
        }
        orden_svc.crear_orden(orden_data)
    
    ordenes_cliente_1 = orden_svc.obtener_ordenes_por_cliente(1)
    assert len(ordenes_cliente_1) == 2
    
    ordenes_cliente_2 = orden_svc.obtener_ordenes_por_cliente(2)
    assert len(ordenes_cliente_2) == 1

