import pytest
from datetime import datetime, timedelta
from app.services.orden_service import OrdenService
from app.services.vehiculo_service import VehiculoService
from app.models.orden import EstadoOrden


@pytest.mark.integration
def test_orden_with_vehiculo_integration(integration_db):
    """Test creating orden with assigned vehiculo"""
    # Create vehiculo first
    vehiculo_svc = VehiculoService(integration_db)
    vehiculo_data = {
        "id_conductor": 1,
        "placa": "ABC123",
        "tipo": "CAMION"
    }
    vehiculo = vehiculo_svc.crear_vehiculo(vehiculo_data)
    
    # Create orden with vehiculo
    orden_svc = OrdenService(integration_db)
    orden_data = {
        "fecha_entrega_estimada": datetime.now() + timedelta(days=7),
        "id_vehiculo": vehiculo.id,
        "id_cliente": 1,
        "id_vendedor": 1,
        "estado": EstadoOrden.EN_REPARTO
    }
    orden = orden_svc.crear_orden(orden_data)
    
    assert orden.id_vehiculo == vehiculo.id
    assert orden.estado == EstadoOrden.EN_REPARTO
    
    # Verify relationship
    retrieved_orden = orden_svc.obtener_orden(orden.id)
    assert retrieved_orden.vehiculo is not None
    assert retrieved_orden.vehiculo.placa == "ABC123"


@pytest.mark.integration
def test_orden_lifecycle_integration(integration_db):
    """Test full orden lifecycle from ABIERTO to ENTREGADO"""
    orden_svc = OrdenService(integration_db)
    
    # Create orden in ABIERTO state
    orden_data = {
        "fecha_entrega_estimada": datetime.now() + timedelta(days=7),
        "id_cliente": 1,
        "id_vendedor": 1,
        "estado": EstadoOrden.ABIERTO
    }
    orden = orden_svc.crear_orden(orden_data)
    assert orden.estado == EstadoOrden.ABIERTO
    
    # Move to POR_ALISTAR
    orden = orden_svc.actualizar_estado(orden.id, {"estado": EstadoOrden.POR_ALISTAR})
    assert orden.estado == EstadoOrden.POR_ALISTAR
    
    # Move to EN_ALISTAMIENTO
    orden = orden_svc.actualizar_estado(orden.id, {"estado": EstadoOrden.EN_ALISTAMIENTO})
    assert orden.estado == EstadoOrden.EN_ALISTAMIENTO
    
    # Move to EN_REPARTO
    orden = orden_svc.actualizar_estado(orden.id, {"estado": EstadoOrden.EN_REPARTO})
    assert orden.estado == EstadoOrden.EN_REPARTO
    
    # Move to ENTREGADO
    orden = orden_svc.actualizar_estado(orden.id, {"estado": EstadoOrden.ENTREGADO})
    assert orden.estado == EstadoOrden.ENTREGADO

