from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from app.models.pedido import Pedido
from app.models.vendedor import Vendedor
from app.models.product import Producto
from app.models.plan_venta import PlanVenta
from app.schemas.report_schema import (
    ReporteRequest, ReporteResponse, KPI,
    DesempenoVendedorRow, VentasPorRegionItem, ProductosCategoriaItem
)
from app.models.catalogs import Pais

class ReportService:
    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    def generar_reportes(self, filtros: ReporteRequest) -> ReporteResponse:
        ini, fin = self._rango_por_periodo(date.today(), filtros.periodo_tiempo)

        kpis, meta = self._kpis_globales(filtros, ini, fin)
        desempeno = self._desempeno_por_vendedor(filtros, ini, fin)
        ventas_zona = self._ventas_por_zona(filtros, ini, fin)
        productos_cat = self._productos_por_categoria(filtros, ini, fin)

        return ReporteResponse(
            kpis=kpis,
            desempeno_vendedores=desempeno,
            ventas_por_region=ventas_zona,
            productos_por_categoria=productos_cat,
            meta_objetivo_usd=meta,
            filtros_aplicados=filtros.dict()
        )

    # -------------------------
    def _rango_por_periodo(self, hoy, periodo):
        from calendar import monthrange
        if periodo == "MES_ACTUAL":
            ini = hoy.replace(day=1)
            fin = hoy.replace(day=monthrange(hoy.year, hoy.month)[1])
        else:
            ini = hoy.replace(day=1)
            fin = hoy
        return ini, fin

    # -------------------------
    def _kpis_globales(self, filtros, ini, fin):
        q = self.db.query(
            func.coalesce(func.sum(Pedido.valor_total_usd), 0),
            func.coalesce(func.count(Pedido.id), 0)
        ).filter(Pedido.fecha.between(ini, fin))

        if filtros.vendedor_id:
            q = q.filter(Pedido.vendedor_id == filtros.vendedor_id)
        if filtros.pais:
            q = q.join(Vendedor).filter(Vendedor.pais_id.in_(filtros.pais))

        ventas_totales, pedidos_totales = q.one()

        meta = self.db.query(func.sum(PlanVenta.meta_monetaria_usd)).scalar() or 100000
        cumplimiento = float(ventas_totales) / float(meta) if float(meta) > 0 else 0.0


        kpis = KPI(
            ventas_totales=float(ventas_totales),
            pedidos_mes=int(pedidos_totales),
            cumplimiento=round(cumplimiento, 2),
            tiempo_entrega_promedio_h=24.0
        )
        return kpis, meta

    # -------------------------
        # -------------------------
    def _desempeno_por_vendedor(self, filtros, ini, fin):
        q = self.db.query(
            Vendedor.id,
            Vendedor.nombre,
            Vendedor.pais,
            func.sum(Pedido.valor_total_usd).label("ventas"),
            func.count(Pedido.id).label("pedidos")
        ).join(Pedido, Pedido.vendedor_id == Vendedor.id)\
         .filter(Pedido.fecha.between(ini, fin))

        #  Si llega vendedor_id, solo ese vendedor
        if filtros.vendedor_id:
            q = q.filter(Vendedor.id == filtros.vendedor_id)

        q = q.group_by(Vendedor.id, Vendedor.nombre, Vendedor.pais).all()

        out = []
        for vid, nombre, pais, ventas, pedidos in q:
            estado = (
                "LOW" if ventas < 40000 else
                "WARN" if ventas < 60000 else
                "OK" if ventas < 80000 else
                "HIGH"
            )
            out.append(DesempenoVendedorRow(
                vendedor=nombre,
                pais=self._codigo_pais(pais),
                pedidos=int(pedidos),
                ventas_usd=float(ventas),
                estado=estado
            ))
        return out

    def _codigo_pais(self, id_pais: int) -> str:
        mapa = {1: "COL", 2: "MEX", 3: "PER", 4: "ECU"}
        return mapa.get(id_pais, "ND")


    # -------------------------
    def _ventas_por_zona(self, filtros, ini, fin):
        q = self.db.query(
            Vendedor.pais,
            func.sum(Pedido.valor_total_usd)
        ).join(Vendedor, Vendedor.id == Pedido.vendedor_id)\
         .filter(Pedido.fecha.between(ini, fin))\
         .group_by(Vendedor.pais)\
         .all()

        return [VentasPorRegionItem(zona=str(p), ventas_usd=float(v)) for p, v in q]

    # -------------------------
    def _productos_por_categoria(self, filtros, ini, fin):
        q = self.db.query(
            Producto.tipo_medicamento,
            func.sum(Pedido.cantidad),
            func.sum(Pedido.valor_total_usd)
        ).join(Producto, Producto.id == Pedido.producto_id)\
         .filter(Pedido.fecha.between(ini, fin))\
         .group_by(Producto.tipo_medicamento)\
         .all()

        total = sum(v or 0 for _, _, v in q)
        return [
            ProductosCategoriaItem(
                categoria=c or "Sin categoría",
                unidades=int(u or 0),
                ingresos_usd=float(v or 0),
                porcentaje=round((v / total * 100), 2) if total else 0
            )
            for c, u, v in q
        ]
