import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.services.product_service import ProductService
from app.services.proveedor_service import ProveedorService


def test_crear_producto_success(db_session):
    prov_svc = ProveedorService(db_session)
    proveedor = prov_svc.crear_proveedor({"razon_social": "Prov1", "paises_operacion": [1], "certificaciones_sanitarias": [1], "categorias_suministradas": [1]})
    prod_svc = ProductService(db_session)
    producto = prod_svc.crear_producto({"sku": "S1", "nombre_producto": "P1", "proveedor_id": proveedor.id, "valor_unitario_usd": 10.0, "certificaciones": [1]}, usuario_id=2)
    assert producto.id is not None


def test_crear_producto_raises_when_proveedor_missing(db_session):
    prod_svc = ProductService(db_session)
    with pytest.raises(ValueError):
        prod_svc.crear_producto({"sku": "Sx", "nombre_producto": "PX", "proveedor_id": 999, "valor_unitario_usd": 1.0, "certificaciones": []})


def test_crear_producto_cert_mismatch(db_session):
    prov_svc = ProveedorService(db_session)
    proveedor = prov_svc.crear_proveedor({"razon_social": "Prov2", "paises_operacion": [1], "certificaciones_sanitarias": [2], "categorias_suministradas": [1]})
    prod_svc = ProductService(db_session)
    # product requires cert 1 but provider has cert 2 -> mismatch
    with pytest.raises(ValueError):
        prod_svc.crear_producto({"sku": "S2", "nombre_producto": "P2", "proveedor_id": proveedor.id, "valor_unitario_usd": 5.0, "certificaciones": [1]})
