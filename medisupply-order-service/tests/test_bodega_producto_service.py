import pytest
from datetime import datetime, timedelta
from app.services.bodega_producto_service import BodegaProductoService
from app.services.bodega_service import BodegaService
from app.schemas.bodega_producto_schema import BodegaProductoCreate, BodegaProductoUpdate
from app.schemas.bodega_schema import BodegaCreate


def test_crear_bodega_producto(db_session):
    """Test creating a new bodega_producto"""
    # Create bodega first
    bodega_svc = BodegaService(db_session)
    bodega_data = BodegaCreate(
        nombre="Bodega Test",
        direccion="Calle 100",
        id_pais=1,
        ciudad="Bogotá"
    )
    bodega = bodega_svc.crear_bodega(bodega_data)
    
    # Create bodega_producto
    bp_svc = BodegaProductoService(db_session)
    bp_data = BodegaProductoCreate(
        id_bodega=bodega.id,
        id_producto=1,
        lote="LOTE001",
        cantidad=100,
        dias_alistamiento=2
    )
    
    bp = bp_svc.crear_bodega_producto(bp_data)
    assert bp.id_bodega == bodega.id
    assert bp.id_producto == 1
    assert bp.lote == "LOTE001"
    assert bp.cantidad == 100


def test_listar_bodega_productos(db_session):
    """Test listing all bodega_productos"""
    # Create bodega
    bodega_svc = BodegaService(db_session)
    bodega_data = BodegaCreate(
        nombre="Bodega Test",
        direccion="Calle 100",
        id_pais=1,
        ciudad="Bogotá"
    )
    bodega = bodega_svc.crear_bodega(bodega_data)
    
    # Create multiple bodega_productos
    bp_svc = BodegaProductoService(db_session)
    for i in range(3):
        bp_data = BodegaProductoCreate(
            id_bodega=bodega.id,
            id_producto=i+1,
            lote=f"LOTE{i:03d}",
            cantidad=50 + i*10,
            dias_alistamiento=2
        )
        bp_svc.crear_bodega_producto(bp_data)
    
    bps = bp_svc.listar_bodega_productos()
    assert len(bps) >= 3


def test_listar_bodega_productos_con_filtros(db_session):
    """Test filtering bodega_productos"""
    # Create bodega
    bodega_svc = BodegaService(db_session)
    bodega_data = BodegaCreate(
        nombre="Bodega Filtro",
        direccion="Av. Test",
        id_pais=1,
        ciudad="Medellín"
    )
    bodega = bodega_svc.crear_bodega(bodega_data)
    
    # Create bodega_productos
    bp_svc = BodegaProductoService(db_session)
    bp_data = BodegaProductoCreate(
        id_bodega=bodega.id,
        id_producto=100,
        lote="LOTE_SPECIAL",
        cantidad=200,
        dias_alistamiento=3
    )
    bp_svc.crear_bodega_producto(bp_data)
    
    # Filter by bodega
    bps = bp_svc.listar_bodega_productos(id_bodega=bodega.id)
    assert len(bps) >= 1
    
    # Filter by producto
    bps = bp_svc.listar_bodega_productos(id_producto=100)
    assert len(bps) >= 1
    
    # Filter by lote
    bps = bp_svc.listar_bodega_productos(lote="LOTE_SPECIAL")
    assert len(bps) >= 1


def test_listar_por_bodega(db_session):
    """Test listing productos for a specific bodega"""
    # Create bodega
    bodega_svc = BodegaService(db_session)
    bodega_data = BodegaCreate(
        nombre="Bodega Especifica",
        direccion="Calle Especial",
        id_pais=1,
        ciudad="Cali"
    )
    bodega = bodega_svc.crear_bodega(bodega_data)
    
    # Create bodega_productos
    bp_svc = BodegaProductoService(db_session)
    for i in range(2):
        bp_data = BodegaProductoCreate(
            id_bodega=bodega.id,
            id_producto=200+i,
            lote=f"LOTE_BOD{i}",
            cantidad=30,
            dias_alistamiento=1
        )
        bp_svc.crear_bodega_producto(bp_data)
    
    bps = bp_svc.listar_por_bodega(bodega.id)
    assert len(bps) == 2


def test_obtener_bodega_producto(db_session):
    """Test getting specific bodega_producto"""
    # Create bodega
    bodega_svc = BodegaService(db_session)
    bodega_data = BodegaCreate(
        nombre="Bodega Get",
        direccion="Calle Get",
        id_pais=1,
        ciudad="Bogotá"
    )
    bodega = bodega_svc.crear_bodega(bodega_data)
    
    # Create bodega_producto
    bp_svc = BodegaProductoService(db_session)
    bp_data = BodegaProductoCreate(
        id_bodega=bodega.id,
        id_producto=300,
        lote="LOTE_GET",
        cantidad=150,
        dias_alistamiento=2
    )
    bp = bp_svc.crear_bodega_producto(bp_data)
    
    # Get it
    retrieved = bp_svc.obtener_bodega_producto(bodega.id, 300, "LOTE_GET")
    assert retrieved is not None
    assert retrieved.cantidad == 150


def test_obtener_bodega_producto_inexistente(db_session):
    """Test getting non-existent bodega_producto returns None"""
    bp_svc = BodegaProductoService(db_session)
    result = bp_svc.obtener_bodega_producto(99999, 99999, "NOEXISTE")
    assert result is None


def test_actualizar_bodega_producto(db_session):
    """Test updating bodega_producto"""
    # Create bodega
    bodega_svc = BodegaService(db_session)
    bodega_data = BodegaCreate(
        nombre="Bodega Update",
        direccion="Calle Update",
        id_pais=1,
        ciudad="Bogotá"
    )
    bodega = bodega_svc.crear_bodega(bodega_data)
    
    # Create bodega_producto
    bp_svc = BodegaProductoService(db_session)
    bp_data = BodegaProductoCreate(
        id_bodega=bodega.id,
        id_producto=400,
        lote="LOTE_UPD",
        cantidad=100,
        dias_alistamiento=2
    )
    bp = bp_svc.crear_bodega_producto(bp_data)
    
    # Update
    update_data = BodegaProductoUpdate(cantidad=250, dias_alistamiento=5)
    actualizado = bp_svc.actualizar_bodega_producto(bodega.id, 400, "LOTE_UPD", update_data)
    assert actualizado.cantidad == 250
    assert actualizado.dias_alistamiento == 5


def test_actualizar_bodega_producto_inexistente(db_session):
    """Test updating non-existent bodega_producto returns None"""
    bp_svc = BodegaProductoService(db_session)
    update_data = BodegaProductoUpdate(cantidad=999)
    result = bp_svc.actualizar_bodega_producto(99999, 99999, "NOEXISTE", update_data)
    assert result is None


def test_eliminar_bodega_producto(db_session):
    """Test deleting bodega_producto"""
    # Create bodega
    bodega_svc = BodegaService(db_session)
    bodega_data = BodegaCreate(
        nombre="Bodega Delete",
        direccion="Calle Delete",
        id_pais=1,
        ciudad="Bogotá"
    )
    bodega = bodega_svc.crear_bodega(bodega_data)
    
    # Create bodega_producto
    bp_svc = BodegaProductoService(db_session)
    bp_data = BodegaProductoCreate(
        id_bodega=bodega.id,
        id_producto=500,
        lote="LOTE_DEL",
        cantidad=75,
        dias_alistamiento=1
    )
    bp = bp_svc.crear_bodega_producto(bp_data)
    
    # Delete
    result = bp_svc.eliminar_bodega_producto(bodega.id, 500, "LOTE_DEL")
    assert result is True
    
    # Verify it's gone
    deleted = bp_svc.obtener_bodega_producto(bodega.id, 500, "LOTE_DEL")
    assert deleted is None


def test_eliminar_bodega_producto_inexistente(db_session):
    """Test deleting non-existent bodega_producto returns False"""
    bp_svc = BodegaProductoService(db_session)
    result = bp_svc.eliminar_bodega_producto(99999, 99999, "NOEXISTE")
    assert result is False


def test_calcular_distancia_haversine(db_session):
    """Test Haversine distance calculation"""
    bp_svc = BodegaProductoService(db_session)
    
    # Bogotá (4.7110, -74.0721) to Medellín (6.2442, -75.5812)
    # Distance should be approximately 240 km
    distancia = bp_svc._calcular_distancia_haversine(4.7110, -74.0721, 6.2442, -75.5812)
    assert 200 < distancia < 300  # Rough check


def test_calcular_pronostico_entrega(db_session):
    """Test delivery forecast calculation"""
    bp_svc = BodegaProductoService(db_session)
    
    # Test with 100 km distance and 2 days of preparation
    # At 20 km/h, 100 km = 5 hours
    # 2 days = 48 hours
    # Total = 53 hours from now
    fecha_inicio = datetime.now()
    fecha_entrega = bp_svc._calcular_pronostico_entrega(
        lat_origen=4.7110,
        lon_origen=-74.0721,
        lat_bodega=4.6097,  # ~11 km away
        lon_bodega=-74.0817,
        dias_alistamiento=2
    )
    
    # Check that delivery is in the future
    assert fecha_entrega > fecha_inicio
    # Should be roughly 48-50 hours from now
    diferencia_horas = (fecha_entrega - fecha_inicio).total_seconds() / 3600
    assert 45 < diferencia_horas < 55


def test_listar_con_pronostico_entrega(db_session):
    """Test listing with delivery forecast calculation"""
    # Create bodega with coordinates
    bodega_svc = BodegaService(db_session)
    bodega_data = BodegaCreate(
        nombre="Bodega con GPS",
        direccion="Calle GPS",
        id_pais=1,
        ciudad="Bogotá",
        latitud=4.7110,
        longitud=-74.0721
    )
    bodega = bodega_svc.crear_bodega(bodega_data)
    
    # Create bodega_producto
    bp_svc = BodegaProductoService(db_session)
    bp_data = BodegaProductoCreate(
        id_bodega=bodega.id,
        id_producto=600,
        lote="LOTE_GPS",
        cantidad=50,
        dias_alistamiento=3
    )
    bp_svc.crear_bodega_producto(bp_data)
    
    # List with coordinates (should calculate pronostico_entrega)
    bps = bp_svc.listar_bodega_productos(
        id_bodega=bodega.id,
        latitud=4.6097,
        longitud=-74.0817
    )
    
    assert len(bps) >= 1
    assert bps[0]["pronostico_entrega"] is not None
    assert isinstance(bps[0]["pronostico_entrega"], datetime)


def test_listar_sin_pronostico_entrega(db_session):
    """Test listing without delivery forecast (no coordinates)"""
    # Create bodega without coordinates
    bodega_svc = BodegaService(db_session)
    bodega_data = BodegaCreate(
        nombre="Bodega sin GPS",
        direccion="Calle sin GPS",
        id_pais=1,
        ciudad="Cali"
    )
    bodega = bodega_svc.crear_bodega(bodega_data)
    
    # Create bodega_producto
    bp_svc = BodegaProductoService(db_session)
    bp_data = BodegaProductoCreate(
        id_bodega=bodega.id,
        id_producto=700,
        lote="LOTE_NOGPS",
        cantidad=25,
        dias_alistamiento=1
    )
    bp_svc.crear_bodega_producto(bp_data)
    
    # List without coordinates (no pronostico_entrega)
    bps = bp_svc.listar_bodega_productos(id_bodega=bodega.id)
    
    assert len(bps) >= 1
    assert bps[0]["pronostico_entrega"] is None

