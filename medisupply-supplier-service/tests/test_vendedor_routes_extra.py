import pytest
from app.api.v1 import vendedor_routes
from app.schemas.vendedor_schema import VendedorCreate


def test_create_get_delete_vendedor_route(db_session):
    payload = VendedorCreate(nombre='VV', email='vv@x.com', pais=1, estado='ACTIVO')
    v = vendedor_routes.create_vendedor(payload, db=db_session)
    assert v.id is not None
    got = vendedor_routes.get_vendedor(v.id, db=db_session)
    assert got.id == v.id
    # delete
    res = vendedor_routes.delete_vendedor(v.id, db=db_session)
    assert res is None
