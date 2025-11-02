from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.catalogs import Pais
from app.models.vendedor import Vendedor
from app.models.product import Producto
from app.models.client import Cliente
from app.models.pedido import Pedido
from app.models.plan_venta import PlanVenta
from app.api.v1.report_routes import consultar_reportes
from app.schemas.report_schema import ReporteRequest


def setup_inmemory_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_report_route_function_direct_call():
    db = setup_inmemory_db()
    try:
        p = Pais(nombre='Colombia')
        db.add(p)
        db.commit()
        db.refresh(p)

        v = Vendedor(nombre='VTest2', email='vt2@example.com', pais=p.id)
        db.add(v)
        db.commit()
        db.refresh(v)

        prod = Producto(sku='SKU2', nombre_producto='Prod2', proveedor_id=1, valor_unitario_usd=50.0)
        db.add(prod)
        db.commit()
        db.refresh(prod)

        c = Cliente(vendedor_id=v.id, institucion_nombre='Inst2')
        db.add(c)
        db.commit()
        db.refresh(c)

        today = date.today()
        ped = Pedido(vendedor_id=v.id, cliente_id=c.id, producto_id=prod.id, fecha=today, cantidad=2, valor_total_usd=200.0)
        db.add(ped)
        db.commit()

        plan = PlanVenta(vendedor_id=v.id, periodo='MES_ACTUAL', anio=today.year, pais=p.id, productos_objetivo=[prod.id], meta_monetaria_usd=1000.0)
        db.add(plan)
        db.commit()

        payload = ReporteRequest(vendedor_id=None, pais=[p.id], zona_geografica=[], periodo_tiempo='MES_ACTUAL', tipo_reporte=['DESEMPENO_VENDEDOR'])
        resp = consultar_reportes(payload=payload, db=db)

        # La función devuelve un ReporteResponse Pydantic (o similar)
        assert resp.kpis.ventas_totales == 200.0
        assert len(resp.desempeno_vendedores) >= 1
    finally:
        db.close()
