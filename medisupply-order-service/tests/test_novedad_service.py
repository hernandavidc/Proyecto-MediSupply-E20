import pytest
from datetime import datetime, timedelta
from app.services.novedad_orden_service import NovedadOrdenService
from app.services.orden_service import OrdenService
from app.schemas.novedad_orden_schema import NovedadOrdenCreate, NovedadOrdenUpdate
from app.schemas.orden_schema import OrdenCreate


def test_crear_novedad_orden(db_session):
    """Test creating a new novedad"""
    # Create orden first
    orden_svc = OrdenService(db_session)
    orden_data = OrdenCreate(
        fecha_entrega_estimada=datetime.now() + timedelta(days=7),
        id_cliente=1,
        id_vendedor=1,
        estado="ABIERTO",
        productos=[]
    )
    orden = orden_svc.crear_orden(orden_data)
    
    # Create novedad
    novedad_svc = NovedadOrdenService(db_session)
    novedad_data = NovedadOrdenCreate(
        id_pedido=orden.id,
        tipo="DEVOLUCION",
        descripcion="Producto defectuoso"
    )
    
    novedad = novedad_svc.crear_novedad(novedad_data)
    assert novedad.id is not None
    assert novedad.id_pedido == orden.id
    assert novedad.tipo == "DEVOLUCION"


def test_listar_novedades(db_session):
    """Test listing all novedades"""
    # Create orden
    orden_svc = OrdenService(db_session)
    orden_data = OrdenCreate(
        fecha_entrega_estimada=datetime.now() + timedelta(days=7),
        id_cliente=1,
        id_vendedor=1,
        estado="ABIERTO",
        productos=[]
    )
    orden = orden_svc.crear_orden(orden_data)
    
    # Create multiple novedades
    novedad_svc = NovedadOrdenService(db_session)
    for i in range(3):
        novedad_data = NovedadOrdenCreate(
            id_pedido=orden.id,
            tipo="CANTIDAD_DIFERENTE",
            descripcion=f"Novedad {i}"
        )
        novedad_svc.crear_novedad(novedad_data)
    
    novedades = novedad_svc.listar_novedades()
    assert len(novedades) >= 3


def test_obtener_novedad(db_session):
    """Test getting a specific novedad by ID"""
    # Create orden
    orden_svc = OrdenService(db_session)
    orden_data = OrdenCreate(
        fecha_entrega_estimada=datetime.now() + timedelta(days=7),
        id_cliente=1,
        id_vendedor=1,
        estado="ABIERTO",
        productos=[]
    )
    orden = orden_svc.crear_orden(orden_data)
    
    # Create novedad
    novedad_svc = NovedadOrdenService(db_session)
    novedad_data = NovedadOrdenCreate(
        id_pedido=orden.id,
        tipo="PRODUCTO_NO_COINCIDE",
        descripcion="Error en el pedido"
    )
    
    novedad = novedad_svc.crear_novedad(novedad_data)
    retrieved = novedad_svc.obtener_novedad(novedad.id)
    
    assert retrieved.id == novedad.id
    assert retrieved.descripcion == "Error en el pedido"


def test_obtener_novedad_inexistente(db_session):
    """Test getting non-existent novedad returns None"""
    novedad_svc = NovedadOrdenService(db_session)
    
    result = novedad_svc.obtener_novedad(99999)
    assert result is None


def test_actualizar_novedad(db_session):
    """Test updating novedad"""
    # Create orden
    orden_svc = OrdenService(db_session)
    orden_data = OrdenCreate(
        fecha_entrega_estimada=datetime.now() + timedelta(days=7),
        id_cliente=1,
        id_vendedor=1,
        estado="ABIERTO",
        productos=[]
    )
    orden = orden_svc.crear_orden(orden_data)
    
    # Create novedad
    novedad_svc = NovedadOrdenService(db_session)
    novedad_data = NovedadOrdenCreate(
        id_pedido=orden.id,
        tipo="MAL_ESTADO",
        descripcion="Original"
    )
    
    novedad = novedad_svc.crear_novedad(novedad_data)
    
    # Update
    update_data = NovedadOrdenUpdate(descripcion="Actualizada")
    actualizado = novedad_svc.actualizar_novedad(novedad.id, update_data)
    
    assert actualizado.descripcion == "Actualizada"


def test_actualizar_novedad_inexistente(db_session):
    """Test updating non-existent novedad returns None"""
    novedad_svc = NovedadOrdenService(db_session)
    
    update_data = NovedadOrdenUpdate(descripcion="No existe")
    result = novedad_svc.actualizar_novedad(99999, update_data)
    
    assert result is None


def test_eliminar_novedad(db_session):
    """Test deleting novedad"""
    # Create orden
    orden_svc = OrdenService(db_session)
    orden_data = OrdenCreate(
        fecha_entrega_estimada=datetime.now() + timedelta(days=7),
        id_cliente=1,
        id_vendedor=1,
        estado="ABIERTO",
        productos=[]
    )
    orden = orden_svc.crear_orden(orden_data)
    
    # Create novedad
    novedad_svc = NovedadOrdenService(db_session)
    novedad_data = NovedadOrdenCreate(
        id_pedido=orden.id,
        tipo="DEVOLUCION",
        descripcion="A eliminar"
    )
    
    novedad = novedad_svc.crear_novedad(novedad_data)
    novedad_id = novedad.id
    
    # Delete
    result = novedad_svc.eliminar_novedad(novedad_id)
    assert result is True
    
    # Verify it's gone
    deleted = novedad_svc.obtener_novedad(novedad_id)
    assert deleted is None


def test_eliminar_novedad_inexistente(db_session):
    """Test deleting non-existent novedad returns False"""
    novedad_svc = NovedadOrdenService(db_session)
    
    result = novedad_svc.eliminar_novedad(99999)
    assert result is False


def test_listar_novedades_por_pedido(db_session):
    """Test filtering novedades by pedido"""
    # Create two ordenes
    orden_svc = OrdenService(db_session)
    orden1_data = OrdenCreate(
        fecha_entrega_estimada=datetime.now() + timedelta(days=7),
        id_cliente=1,
        id_vendedor=1,
        estado="ABIERTO",
        productos=[]
    )
    orden1 = orden_svc.crear_orden(orden1_data)
    
    orden2_data = OrdenCreate(
        fecha_entrega_estimada=datetime.now() + timedelta(days=7),
        id_cliente=2,
        id_vendedor=1,
        estado="ABIERTO",
        productos=[]
    )
    orden2 = orden_svc.crear_orden(orden2_data)
    
    # Create novedades for different ordenes
    novedad_svc = NovedadOrdenService(db_session)
    for i in range(2):
        novedad_data = NovedadOrdenCreate(
            id_pedido=orden1.id,
            tipo="DEVOLUCION",
            descripcion=f"Novedad orden1 {i}"
        )
        novedad_svc.crear_novedad(novedad_data)
    
    novedad_data = NovedadOrdenCreate(
        id_pedido=orden2.id,
        tipo="MAL_ESTADO",
        descripcion="Novedad orden2"
    )
    novedad_svc.crear_novedad(novedad_data)
    
    # Filter by orden1
    novedades_orden1 = novedad_svc.listar_por_orden(orden1.id)
    assert len(novedades_orden1) == 2
    
    # Filter by orden2
    novedades_orden2 = novedad_svc.listar_por_orden(orden2.id)
    assert len(novedades_orden2) == 1

