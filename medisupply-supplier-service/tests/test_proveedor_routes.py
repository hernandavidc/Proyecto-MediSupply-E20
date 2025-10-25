import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.api.v1 import proveedor_routes
from app.schemas.proveedor_schema import ProveedorCreate, ProveedorUpdate
from fastapi import HTTPException
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.api.v1 import proveedor_routes
from app.schemas.proveedor_schema import ProveedorCreate, ProveedorUpdate
from fastapi import HTTPException


def test_create_get_update_delete_proveedor_route(db_session):
    payload = ProveedorCreate(razon_social='R1', paises_operacion=[1], certificaciones_sanitarias=[1], categorias_suministradas=[1])
    # create
    p = proveedor_routes.create_proveedor(payload, db=db_session)
    assert p.id is not None

    # get
    got = proveedor_routes.get_proveedor(p.id, db=db_session)
    assert got.id == p.id

    # update
    upd = ProveedorUpdate(razon_social='R1 Updated')
    updated = proveedor_routes.update_proveedor(p.id, upd, db=db_session)
    assert updated.razon_social == 'R1 Updated'

    # delete (no products)
    res = proveedor_routes.delete_proveedor(p.id, db=db_session)
    assert res is None


def test_delete_proveedor_blocked_by_product(db_session):
    # create provider and product via services to simulate existing product
    from app.services.proveedor_service import ProveedorService
    from app.services.product_service import ProductService
    prov = ProveedorService(db_session).crear_proveedor({"razon_social": "PBlock", "paises_operacion": [1], "certificaciones_sanitarias": [1], "categorias_suministradas": [1]})
    prod = ProductService(db_session).crear_producto({"sku": "SBK", "nombre_producto": "PBK", "proveedor_id": prov.id, "valor_unitario_usd": 1.0, "certificaciones": [1]}, usuario_id=1)
    with pytest.raises(HTTPException):
        proveedor_routes.delete_proveedor(prov.id, db=db_session)
