import pytest
from app.services.bodega_service import BodegaService
from app.schemas.bodega_schema import BodegaCreate, BodegaUpdate


def test_crear_bodega(db_session):
    """Test creating a new bodega"""
    bodega_svc = BodegaService(db_session)
    
    bodega_data = BodegaCreate(
        nombre="Bodega Central",
        direccion="Calle 100 # 10-20",
        id_pais=1,
        ciudad="Bogotá"
    )
    
    bodega = bodega_svc.crear_bodega(bodega_data)
    assert bodega.id is not None
    assert bodega.nombre == "Bodega Central"
    assert bodega.ciudad == "Bogotá"


def test_listar_bodegas(db_session):
    """Test listing all bodegas"""
    bodega_svc = BodegaService(db_session)
    
    # Create multiple bodegas
    for i in range(3):
        bodega_data = BodegaCreate(
            nombre=f"Bodega {i}",
            direccion=f"Dirección {i}",
            id_pais=1,
            ciudad=f"Ciudad {i}"
        )
        bodega_svc.crear_bodega(bodega_data)
    
    bodegas = bodega_svc.listar_bodegas()
    assert len(bodegas) >= 3


def test_obtener_bodega(db_session):
    """Test getting a specific bodega by ID"""
    bodega_svc = BodegaService(db_session)
    
    bodega_data = BodegaCreate(
        nombre="Bodega Norte",
        direccion="Av. Norte 50",
        id_pais=1,
        ciudad="Medellín"
    )
    
    bodega = bodega_svc.crear_bodega(bodega_data)
    retrieved = bodega_svc.obtener_bodega(bodega.id)
    
    assert retrieved.id == bodega.id
    assert retrieved.nombre == "Bodega Norte"


def test_obtener_bodega_inexistente(db_session):
    """Test getting non-existent bodega returns None"""
    bodega_svc = BodegaService(db_session)
    
    result = bodega_svc.obtener_bodega(99999)
    assert result is None


def test_actualizar_bodega(db_session):
    """Test updating bodega"""
    bodega_svc = BodegaService(db_session)
    
    bodega_data = BodegaCreate(
        nombre="Bodega Sur",
        direccion="Calle 10 Sur",
        id_pais=1,
        ciudad="Cali"
    )
    
    bodega = bodega_svc.crear_bodega(bodega_data)
    
    # Update
    update_data = BodegaUpdate(nombre="Bodega Sur Actualizada", ciudad="Cali Updated")
    actualizado = bodega_svc.actualizar_bodega(bodega.id, update_data)
    
    assert actualizado.nombre == "Bodega Sur Actualizada"
    assert actualizado.ciudad == "Cali Updated"


def test_actualizar_bodega_inexistente(db_session):
    """Test updating non-existent bodega returns None"""
    bodega_svc = BodegaService(db_session)
    
    update_data = BodegaUpdate(nombre="No Existe")
    result = bodega_svc.actualizar_bodega(99999, update_data)
    
    assert result is None


def test_eliminar_bodega(db_session):
    """Test deleting bodega"""
    bodega_svc = BodegaService(db_session)
    
    bodega_data = BodegaCreate(
        nombre="Bodega a Eliminar",
        direccion="Dirección temporal",
        id_pais=1,
        ciudad="Ciudad"
    )
    
    bodega = bodega_svc.crear_bodega(bodega_data)
    bodega_id = bodega.id
    
    # Delete
    result = bodega_svc.eliminar_bodega(bodega_id)
    assert result is True
    
    # Verify it's gone
    deleted = bodega_svc.obtener_bodega(bodega_id)
    assert deleted is None


def test_eliminar_bodega_inexistente(db_session):
    """Test deleting non-existent bodega returns False"""
    bodega_svc = BodegaService(db_session)
    
    result = bodega_svc.eliminar_bodega(99999)
    assert result is False

