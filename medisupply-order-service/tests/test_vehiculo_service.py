import pytest
from app.services.vehiculo_service import VehiculoService
from app.schemas.vehiculo_schema import VehiculoCreate, VehiculoUpdate


def test_crear_vehiculo(db_session):
    """Test creating a new vehiculo"""
    vehiculo_svc = VehiculoService(db_session)
    
    vehiculo_data = VehiculoCreate(
        id_conductor=1,
        placa="ABC123",
        tipo="CAMION"
    )
    
    vehiculo = vehiculo_svc.crear_vehiculo(vehiculo_data)
    assert vehiculo.id is not None
    assert vehiculo.placa == "ABC123"
    assert vehiculo.tipo == "CAMION"


def test_listar_vehiculos(db_session):
    """Test listing all vehiculos"""
    vehiculo_svc = VehiculoService(db_session)
    
    # Create multiple vehiculos
    for i in range(3):
        vehiculo_data = VehiculoCreate(
            id_conductor=i + 1,
            placa=f"VEH{i:03d}",
            tipo="CAMION"
        )
        vehiculo_svc.crear_vehiculo(vehiculo_data)
    
    vehiculos = vehiculo_svc.listar_vehiculos()
    assert len(vehiculos) >= 3


def test_obtener_vehiculo(db_session):
    """Test getting a specific vehiculo by ID"""
    vehiculo_svc = VehiculoService(db_session)
    
    vehiculo_data = VehiculoCreate(
        id_conductor=10,
        placa="XYZ789",
        tipo="VAN"
    )
    
    vehiculo = vehiculo_svc.crear_vehiculo(vehiculo_data)
    retrieved = vehiculo_svc.obtener_vehiculo(vehiculo.id)
    
    assert retrieved.id == vehiculo.id
    assert retrieved.placa == "XYZ789"


def test_obtener_vehiculo_inexistente(db_session):
    """Test getting non-existent vehiculo returns None"""
    vehiculo_svc = VehiculoService(db_session)
    
    result = vehiculo_svc.obtener_vehiculo(99999)
    assert result is None


def test_actualizar_vehiculo(db_session):
    """Test updating vehiculo"""
    vehiculo_svc = VehiculoService(db_session)
    
    vehiculo_data = VehiculoCreate(
        id_conductor=20,
        placa="UPD001",
        tipo="CAMION"
    )
    
    vehiculo = vehiculo_svc.crear_vehiculo(vehiculo_data)
    
    # Update
    update_data = VehiculoUpdate(placa="UPD999", tipo="VAN")
    actualizado = vehiculo_svc.actualizar_vehiculo(vehiculo.id, update_data)
    
    assert actualizado.placa == "UPD999"
    assert actualizado.tipo == "VAN"


def test_actualizar_vehiculo_inexistente(db_session):
    """Test updating non-existent vehiculo returns None"""
    vehiculo_svc = VehiculoService(db_session)
    
    update_data = VehiculoUpdate(placa="NOEXIST")
    result = vehiculo_svc.actualizar_vehiculo(99999, update_data)
    
    assert result is None


def test_eliminar_vehiculo(db_session):
    """Test deleting vehiculo"""
    vehiculo_svc = VehiculoService(db_session)
    
    vehiculo_data = VehiculoCreate(
        id_conductor=30,
        placa="DEL001",
        tipo="CAMION"
    )
    
    vehiculo = vehiculo_svc.crear_vehiculo(vehiculo_data)
    vehiculo_id = vehiculo.id
    
    # Delete
    result = vehiculo_svc.eliminar_vehiculo(vehiculo_id)
    assert result is True
    
    # Verify it's gone
    deleted = vehiculo_svc.obtener_vehiculo(vehiculo_id)
    assert deleted is None


def test_eliminar_vehiculo_inexistente(db_session):
    """Test deleting non-existent vehiculo returns False"""
    vehiculo_svc = VehiculoService(db_session)
    
    result = vehiculo_svc.eliminar_vehiculo(99999)
    assert result is False


def test_listar_vehiculos_con_filtro_conductor(db_session):
    """Test filtering vehiculos by conductor"""
    vehiculo_svc = VehiculoService(db_session)
    
    # Create vehiculos for different conductors with unique placas
    import time
    for i, conductor_id in enumerate([100, 100, 200]):
        vehiculo_data = VehiculoCreate(
            id_conductor=conductor_id,
            placa=f"COND{conductor_id}-{i}",
            tipo="CAMION"
        )
        vehiculo_svc.crear_vehiculo(vehiculo_data)
    
    # Filter by conductor 100
    vehiculos = vehiculo_svc.listar_vehiculos(id_conductor=100)
    # Should have at least 2 vehiculos for conductor 100
    assert len([v for v in vehiculos if v.id_conductor == 100]) >= 2

