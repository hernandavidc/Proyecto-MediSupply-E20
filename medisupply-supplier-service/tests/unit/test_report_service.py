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
from app.services.report_service import ReportService
from app.schemas.report_schema import ReporteRequest


def setup_inmemory_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_report_service_kpis_basic():
    db = setup_inmemory_db()
    try:
        # seed minimal data
        p = Pais(nombre='Colombia')
        db.add(p)
        db.commit()
        db.refresh(p)

        v = Vendedor(nombre='VTest', email='vt@example.com', pais=p.id)
        db.add(v)
        db.commit()
        db.refresh(v)

        prod = Producto(sku='SKU1', nombre_producto='Prod1', proveedor_id=1, valor_unitario_usd=100.0)
        db.add(prod)
        db.commit()
        db.refresh(prod)

        c = Cliente(vendedor_id=v.id, institucion_nombre='Inst1')
        db.add(c)
        db.commit()
        db.refresh(c)

        today = date.today()
        ped = Pedido(vendedor_id=v.id, cliente_id=c.id, producto_id=prod.id, fecha=today, cantidad=1, valor_total_usd=1000.0)
        db.add(ped)
        db.commit()

        plan = PlanVenta(vendedor_id=v.id, periodo='MES_ACTUAL', anio=today.year, pais=p.id, productos_objetivo=[prod.id], meta_monetaria_usd=500.0)
        db.add(plan)
        db.commit()

        # ejecutar servicio
        svc = ReportService(db)
        req = ReporteRequest(vendedor_id=None, pais=[p.id], zona_geografica=[], periodo_tiempo='MES_ACTUAL', tipo_reporte=['DESEMPENO_VENDEDOR'])
        resp = svc.generar_reportes(req)

        assert resp.kpis.ventas_totales == 1000.0
        assert resp.kpis.pedidos_mes == 1
        assert isinstance(resp.desempeno_vendedores, list)
        assert len(resp.desempeno_vendedores) >= 1
    finally:
        db.close()