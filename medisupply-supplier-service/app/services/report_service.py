from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime
import httpx
from typing import List, Dict, Any
from app.core.config import settings
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
        self.order_service_url = settings.ORDER_SERVICE_URL

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
    def _obtener_ordenes_desde_api(self, fecha_desde: date, fecha_hasta: date, id_vendedor: int = None) -> List[Dict[str, Any]]:
        """Obtiene órdenes del order-service mediante API REST - solo órdenes ENTREGADAS"""
        try:
            # Convertir dates a datetime para el API
            fecha_desde_dt = datetime.combine(fecha_desde, datetime.min.time())
            fecha_hasta_dt = datetime.combine(fecha_hasta, datetime.max.time())
            
            # Construir URL del endpoint interno
            url = f"{self.order_service_url}/internal/v1/ordenes"
            params = {
                "fecha_desde": fecha_desde_dt.isoformat(),
                "fecha_hasta": fecha_hasta_dt.isoformat(),
                "estado": "ENTREGADO",  # Solo órdenes entregadas para reportes
                "limit": 1000  # Ajustar según necesidades
            }
            
            if id_vendedor:
                params["id_vendedor"] = id_vendedor
            
            # Hacer la llamada HTTP con header de autenticación interna
            headers = {
                "X-Internal-Service-Key": settings.INTERNAL_SERVICE_KEY
            }
            with httpx.Client(timeout=30.0, follow_redirects=True) as client:
                response = client.get(url, params=params, headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Error al obtener órdenes del order-service: {str(e)}")
            return []
    
    # -------------------------
    def _calcular_valor_orden(self, orden: Dict[str, Any]) -> float:
        """Calcula el valor total de una orden basándose en sus productos"""
        valor_total = 0.0
        for producto_orden in orden.get("productos", []):
            # Obtener el precio del producto desde la BD local
            producto = self.db.query(Producto).filter(
                Producto.id == producto_orden["id_producto"]
            ).first()
            
            if producto and producto.valor_unitario_usd:
                cantidad = producto_orden["cantidad"]
                valor_total += float(producto.valor_unitario_usd) * cantidad
        
        return valor_total

    # -------------------------
    def _kpis_globales(self, filtros, ini, fin):
        # Obtener órdenes desde order-service
        ordenes = self._obtener_ordenes_desde_api(ini, fin, filtros.vendedor_id)
        
        # Si hay filtro por país, filtrar por vendedores de ese país
        if filtros.pais:
            vendedores_pais = self.db.query(Vendedor.id).filter(
                Vendedor.pais_id.in_(filtros.pais)
            ).all()
            vendedor_ids = {v[0] for v in vendedores_pais}
            ordenes = [o for o in ordenes if o.get("id_vendedor") in vendedor_ids]
        
        # Calcular ventas totales
        ventas_totales = sum(self._calcular_valor_orden(orden) for orden in ordenes)
        pedidos_totales = len(ordenes)
        
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
    def _desempeno_por_vendedor(self, filtros, ini, fin):
        # Obtener órdenes desde order-service
        ordenes = self._obtener_ordenes_desde_api(ini, fin, filtros.vendedor_id)
        
        # Agrupar por vendedor
        vendedor_stats = {}
        for orden in ordenes:
            vid = orden.get("id_vendedor")
            if not vid:
                continue
            
            if vid not in vendedor_stats:
                vendedor_stats[vid] = {"ventas": 0.0, "pedidos": 0}
            
            vendedor_stats[vid]["ventas"] += self._calcular_valor_orden(orden)
            vendedor_stats[vid]["pedidos"] += 1
        
        # Enriquecer con información de vendedores
        out = []
        for vid, stats in vendedor_stats.items():
            vendedor = self.db.query(Vendedor).filter(Vendedor.id == vid).first()
            if not vendedor:
                continue
            
            ventas = stats["ventas"]
            estado = (
                "LOW" if ventas < 40000 else
                "WARN" if ventas < 60000 else
                "OK" if ventas < 80000 else
                "HIGH"
            )
            out.append(DesempenoVendedorRow(
                vendedor=vendedor.nombre,
                pais=self._codigo_pais(vendedor.pais_id),
                pedidos=stats["pedidos"],
                ventas_usd=float(ventas),
                estado=estado
            ))
        return out

    def _codigo_pais(self, id_pais: int) -> str:
        mapa = {1: "COL", 2: "MEX", 3: "PER", 4: "ECU"}
        return mapa.get(id_pais, "ND")


    # -------------------------
    def _ventas_por_zona(self, filtros, ini, fin):
        # Obtener órdenes desde order-service
        ordenes = self._obtener_ordenes_desde_api(ini, fin, filtros.vendedor_id)
        
        # Agrupar por país del vendedor
        ventas_por_pais = {}
        for orden in ordenes:
            vid = orden.get("id_vendedor")
            if not vid:
                continue
            
            vendedor = self.db.query(Vendedor).filter(Vendedor.id == vid).first()
            if not vendedor:
                continue
            
            codigo_pais = self._codigo_pais(vendedor.pais_id)
            if codigo_pais not in ventas_por_pais:
                ventas_por_pais[codigo_pais] = 0.0
            
            ventas_por_pais[codigo_pais] += self._calcular_valor_orden(orden)
        
        return [VentasPorRegionItem(zona=codigo, ventas_usd=float(ventas)) 
                for codigo, ventas in ventas_por_pais.items()]

    # -------------------------
    def _productos_por_categoria(self, filtros, ini, fin):
        # Obtener órdenes desde order-service
        ordenes = self._obtener_ordenes_desde_api(ini, fin, filtros.vendedor_id)
        
        # Agrupar por categoría de producto
        categoria_stats = {}
        for orden in ordenes:
            for producto_orden in orden.get("productos", []):
                pid = producto_orden["id_producto"]
                cantidad = producto_orden["cantidad"]
                
                # Obtener información del producto
                producto = self.db.query(Producto).filter(Producto.id == pid).first()
                if not producto:
                    continue
                
                categoria = producto.tipo_medicamento or "Sin categoría"
                valor = float(producto.valor_unitario_usd or 0) * cantidad
                
                if categoria not in categoria_stats:
                    categoria_stats[categoria] = {"unidades": 0, "ingresos": 0.0}
                
                categoria_stats[categoria]["unidades"] += cantidad
                categoria_stats[categoria]["ingresos"] += valor
        
        total = sum(stats["ingresos"] for stats in categoria_stats.values())
        return [
            ProductosCategoriaItem(
                categoria=c,
                unidades=int(stats["unidades"]),
                ingresos_usd=float(stats["ingresos"]),
                porcentaje=round((stats["ingresos"] / total * 100), 2) if total else 0
            )
            for c, stats in categoria_stats.items()
        ]
