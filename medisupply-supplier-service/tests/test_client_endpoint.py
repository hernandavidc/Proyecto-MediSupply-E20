from app.api.v1.vendedor_routes import get_clientes_por_vendedor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.vendedor import Vendedor
from app.models.client import Cliente


def test_get_clients_route_function_returns_clients():
    # unit test: call the route function directly using an in-memory DB session
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        # create vendor and clients
        v = Vendedor(nombre='VTest', email='vt@x.com', pais=1)
        db.add(v)
        db.commit()
        db.refresh(v)
        db.add_all([
            Cliente(vendedor_id=v.id, institucion_nombre='C1', direccion='D1', contacto_principal='P1'),
            Cliente(vendedor_id=v.id, institucion_nombre='C2', direccion='D2', contacto_principal='P2'),
        ])
        db.commit()

        # call the route function directly
        result = get_clientes_por_vendedor(vendedor_id=v.id, skip=0, limit=100, db=db)
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(hasattr(c, 'institucion_nombre') for c in result)
    finally:
        db.close()
