import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.services.product_service import ProductService
from app.services.proveedor_service import ProveedorService


import pytest
from app.services.product_service import ProductService
from app.services.proveedor_service import ProveedorService


def test_listar_productos_and_get_not_found(db_session):
    prod_svc = ProductService(db_session)
    # initially empty
    assert prod_svc.listar_productos() == []
    # create provider & product
    prov = ProveedorService(db_session).crear_proveedor({"razon_social": "PP", "paises_operacion": [1], "certificaciones_sanitarias": [1], "categorias_suministradas": [1]})
    prod = prod_svc.crear_producto({"sku": "LS1", "nombre_producto": "LP", "proveedor_id": prov.id, "valor_unitario_usd": 2.5, "certificaciones": [1]}, usuario_id=5)
    listed = prod_svc.listar_productos()
    assert len(listed) == 1
    # get non-existent
    assert prod_svc.obtener_producto(9999) is None


def test_crear_producto_with_date_serialization(db_session):
    from datetime import date
    prov = ProveedorService(db_session).crear_proveedor({"razon_social": "PDate", "paises_operacion": [1], "certificaciones_sanitarias": [1], "categorias_suministradas": [1]})
    prod_svc = ProductService(db_session)
    condiciones = {"fecha_inspeccion": date.today()}
    producto = prod_svc.crear_producto({"sku": "SDT", "nombre_producto": "PD", "proveedor_id": prov.id, "valor_unitario_usd": 4.5, "certificaciones": [1], "condiciones": condiciones}, usuario_id=2)
    assert producto.id is not None
