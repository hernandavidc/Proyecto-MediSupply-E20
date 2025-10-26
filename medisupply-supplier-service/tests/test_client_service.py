import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.services.client_service import ClientService
from app.services.vendedor_service import VendedorService
from app.models.client import Cliente


def test_get_clients_by_vendor_returns_only_assigned(db_session):
    # create two vendors
    vend_service = VendedorService(db_session)
    v1 = vend_service.crear_vendedor({"nombre": "V1", "email": "v1@x.com", "pais": 1, "estado": "ACTIVO"})
    v2 = vend_service.crear_vendedor({"nombre": "V2", "email": "v2@x.com", "pais": 1, "estado": "ACTIVO"})

    # insert clients directly (seed-like)
    clients = [
        Cliente(vendedor_id=v1.id, institucion_nombre=f'Inst A{i}', direccion='Addr A', contacto_principal='Cont A')
        for i in range(3)
    ] + [
        Cliente(vendedor_id=v2.id, institucion_nombre=f'Inst B{i}', direccion='Addr B', contacto_principal='Cont B')
        for i in range(2)
    ]
    db_session.add_all(clients)
    db_session.commit()

    service = ClientService(db_session)
    res_v1 = service.get_clients_by_vendor(vendedor_id=v1.id)
    res_v2 = service.get_clients_by_vendor(vendedor_id=v2.id)

    assert len(res_v1) == 3
    assert all(c.vendedor_id == v1.id for c in res_v1)
    assert len(res_v2) == 2
