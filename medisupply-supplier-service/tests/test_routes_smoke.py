import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base

from app.api.v1 import proveedor_routes, producto_routes, plan_routes, vendedor_routes
from app.services.proveedor_service import ProveedorService
from app.services.product_service import ProductService
from app.services.vendedor_service import VendedorService
from app.services.plan_service import PlanService


import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base

from app.api.v1 import proveedor_routes, producto_routes, plan_routes, vendedor_routes
from app.services.proveedor_service import ProveedorService
from app.services.product_service import ProductService
from app.services.vendedor_service import VendedorService
from app.services.plan_service import PlanService


def test_route_functions_basic_flows(db_session):
    # create domain objects via services
    prov_svc = ProveedorService(db_session)
    proveedor = prov_svc.crear_proveedor({"razon_social": "PRoute", "paises_operacion": [1], "certificaciones_sanitarias": [1], "categorias_suministradas": [1]})

    vend_svc = VendedorService(db_session)
    vendedor = vend_svc.crear_vendedor({"nombre": "VRoute", "email": "vr@x.com", "pais": 1, "estado": "ACTIVO"})

    prod_svc = ProductService(db_session)
    producto = prod_svc.crear_producto({"sku": "SPR", "nombre_producto": "ProdR", "proveedor_id": proveedor.id, "valor_unitario_usd": 3.0, "certificaciones": [1]}, usuario_id=10)

    plan_svc = PlanService(db_session)
    plan = plan_svc.crear_plan({"vendedor_id": vendedor.id, "periodo": "Q2", "anio": 2025, "pais": 1, "productos_objetivo": [producto.id]}, usuario_id=11)

    # call list routes
    provs = proveedor_routes.list_proveedores(db=db_session)
    assert isinstance(provs, list)

    prods = producto_routes.list_productos(db=db_session)
    assert isinstance(prods, list)

    vends = vendedor_routes.list_vendedores(db=db_session)
    assert isinstance(vends, list)

    plans = plan_routes.list_planes(db=db_session)
    assert isinstance(plans, list)

    # call get routes for existing
    p = proveedor_routes.get_proveedor(proveedor.id, db=db_session)
    assert p.id == proveedor.id

    prod = producto_routes.get_producto(producto.id, db=db_session)
    assert prod.id == producto.id

    pl = plan_routes.get_plan(plan.id, db=db_session)
    assert pl.id == plan.id

    # non-existing should raise HTTPException
    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        proveedor_routes.get_proveedor(9999, db=db_session)
