import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from fastapi import HTTPException

from app.api.v1 import proveedor_routes, producto_routes, plan_routes, vendedor_routes


def test_route_get_not_found_raises(db_session):
    with pytest.raises(HTTPException):
        proveedor_routes.get_proveedor(9999, db=db_session)
    with pytest.raises(HTTPException):
        producto_routes.get_producto(9999, db=db_session)
    with pytest.raises(HTTPException):
        plan_routes.get_plan(9999, db=db_session)
    with pytest.raises(HTTPException):
        vendedor_routes.get_vendedor(9999, db=db_session)

def test_delete_routes_not_found_raise(db_session):
    # delete vendedor not found
    with pytest.raises(HTTPException):
        vendedor_routes.delete_vendedor(9999, db=db_session)
    # delete plan not found
    with pytest.raises(HTTPException):
        plan_routes.delete_plan(9999, db=db_session)


import asyncio


@pytest.mark.asyncio
async def test_create_routes_raise_http_on_service_errors(db_session):
    # create producto via route should return HTTPException when provider missing
    from app.schemas.product_schema import ProductoCreate
    bad_payload = ProductoCreate(sku='S1', nombre_producto='X', proveedor_id=9999, valor_unitario_usd=1.0)
    with pytest.raises(HTTPException):
        await producto_routes.create_producto(bad_payload, db=db_session)

    # create plan via route should raise when products missing (service will detect missing products)
    from app.schemas.plan_schema import PlanCreate
    payload = PlanCreate(vendedor_id=1, periodo='Q1', anio=2025, pais=1, productos_objetivo=[9999])
    with pytest.raises(HTTPException):
        plan_routes.create_plan(payload, db=db_session)
