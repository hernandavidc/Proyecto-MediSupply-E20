import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.services.proveedor_service import ProveedorService


def test_eliminar_proveedor_success(db_session):
    svc = ProveedorService(db_session)
    p = svc.crear_proveedor({"razon_social": "ToDelete", "paises_operacion": [1], "certificaciones_sanitarias": [1], "categorias_suministradas": [1]})
    # should delete without errors when no products
    svc.eliminar_proveedor(p)
    assert svc.obtener_proveedor(p.id) is None

def test_listar_y_obtener_proveedor_not_found(db_session):
    svc = ProveedorService(db_session)
    # listar en vacío
    items = svc.listar_proveedores()
    assert isinstance(items, list)
    # obtener inexistente
    assert svc.obtener_proveedor(99999) is None
