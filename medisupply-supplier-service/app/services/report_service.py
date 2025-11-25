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
        # Determinar rango de fechas: si es PERSONALIZADO, usar las fechas del request
        if filtros.periodo_tiempo == "PERSONALIZADO" and filtros.fecha_inicio and filtros.fecha_fin:
            ini, fin = filtros.fecha_inicio, filtros.fecha_fin
        else:
            ini, fin = self._rango_por_periodo(date.today(), filtros.periodo_tiempo)

        # Obtener órdenes una sola vez
        ordenes = self._obtener_ordenes_desde_api(ini, fin, filtros.vendedor_id)

        # Preparar lookups para evitar N+1 queries (se extrae a helper para reducir complejidad)
        productos_db, vendedores_db = self._build_lookups(ordenes)

        # Calcular solo los reportes solicitados para ahorrar trabajo
        tipos = set(filtros.tipo_reporte or [])

        kpis = KPI(ventas_totales=0.0, pedidos_mes=0, cumplimiento=0.0, tiempo_entrega_promedio_h=0.0)
        meta = None
        desempeno = None
        ventas_zona = None
        productos_cat = None

        if "CUMPLIMIENTO_METAS" in tipos or "DESEMPENO_VENDEDOR" in tipos:
            kpis, meta = self._kpis_globales(filtros, ordenes, productos_db)

        if "DESEMPENO_VENDEDOR" in tipos:
            desempeno = self._desempeno_por_vendedor(ordenes, productos_db, vendedores_db)

        if "VENTAS_POR_ZONA" in tipos:
            ventas_zona = self._ventas_por_zona(ordenes, productos_db, vendedores_db)

        if "VENTAS_POR_PRODUCTO" in tipos:
            productos_cat = self._productos_por_categoria(ordenes, productos_db)

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

    def _build_lookups(self, ordenes: List[Dict[str, Any]]):
        """Construye diccionarios lookup para productos y vendedores a partir de las órdenes."""
        product_ids = set()
        vendor_ids = set()
        for orden in ordenes:
            vid = orden.get("id_vendedor") or orden.get("vendedor_id")
            if vid:
                vendor_ids.add(vid)
            for producto_orden in orden.get("productos", []):
                pid = producto_orden.get("id_producto") or producto_orden.get("producto_id")
                if pid:
                    product_ids.add(pid)

        productos_db = {}
        if product_ids:
            prods = self.db.query(Producto).filter(Producto.id.in_(list(product_ids))).all()
            productos_db = {p.id: p for p in prods}

        vendedores_db = {}
        if vendor_ids:
            vends = self.db.query(Vendedor).filter(Vendedor.id.in_(list(vendor_ids))).all()
            vendedores_db = {v.id: v for v in vends}

        return productos_db, vendedores_db

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
                data = response.json()
                # Si la API devuelve lista vacía, caemos al fallback local
                if not data:
                    print("Order-service returned empty list, falling back to local pedidos table")
                    return self._obtener_ordenes_desde_db(fecha_desde, fecha_hasta, id_vendedor)
                return data
        except Exception as e:
            print(f"Error al obtener órdenes del order-service: {str(e)}")
            # Intentar fallback local antes de devolver lista vacía
            return self._obtener_ordenes_desde_db(fecha_desde, fecha_hasta, id_vendedor)

    def _obtener_ordenes_desde_db(self, fecha_desde: date, fecha_hasta: date, id_vendedor: int = None) -> List[Dict[str, Any]]:
        """Fallback: obtiene órdenes desde la tabla local `pedidos` y las transforma al formato esperado."""
        try:
            query = self.db.query(Pedido).filter(Pedido.estado == 'ENTREGADO')
            # Pedido.fecha es date; filtrar por rango inclusivo
            query = query.filter(Pedido.fecha >= fecha_desde, Pedido.fecha <= fecha_hasta)
            if id_vendedor:
                query = query.filter(Pedido.vendedor_id == id_vendedor)

            rows = query.all()
            ordenes = []
            for p in rows:
                orden = {
                    "id": p.id,
                    "id_vendedor": p.vendedor_id,
                    "productos": [
                        {"id_producto": p.producto_id, "cantidad": p.cantidad}
                    ],
                    # usar la fecha del pedido como creación y entrega estimada
                    "fecha_creacion": p.fecha.isoformat(),
                    "fecha_entrega_estimada": p.fecha.isoformat()
                }
                ordenes.append(orden)
            print(f"Fallback local: found {len(ordenes)} orden(es) in pedidos table")
            return ordenes
        except Exception as e:
            print(f"Error reading local pedidos table: {e}")
            return []
    
    # -------------------------
    def _calcular_tiempo_entrega_promedio(self, ordenes: List[Dict[str, Any]]) -> float:
        """Calcula el tiempo promedio de entrega en horas basándose en órdenes ENTREGADAS"""
        if not ordenes:
            return 0.0
        
        tiempos_entrega = []
        for orden in ordenes:
            try:
                # Parsear fechas (pueden venir en formato ISO con o sin 'Z')
                fecha_creacion_str = orden.get("fecha_creacion", "")
                # aceptar varias posibles keys
                fecha_entrega_str = orden.get("fecha_entrega_estimada", "") or orden.get("fecha_entrega", "")
                
                if not fecha_creacion_str or not fecha_entrega_str:
                    continue
                
                # Limpiar 'Z' al final si existe
                if fecha_creacion_str.endswith('Z'):
                    fecha_creacion_str = fecha_creacion_str[:-1]
                if fecha_entrega_str.endswith('Z'):
                    fecha_entrega_str = fecha_entrega_str[:-1]
                
                # Parsear a datetime
                fecha_creacion = datetime.fromisoformat(fecha_creacion_str)
                fecha_entrega = datetime.fromisoformat(fecha_entrega_str)
                
                # Calcular diferencia en horas
                diferencia = fecha_entrega - fecha_creacion
                horas = diferencia.total_seconds() / 3600
                
                if horas > 0:  # Solo considerar tiempos positivos
                    tiempos_entrega.append(horas)
            except Exception:
                # Si hay error parseando fechas, continuar con la siguiente orden
                continue
        
        # Retornar promedio o 0 si no hay datos válidos
        if tiempos_entrega:
            return round(sum(tiempos_entrega) / len(tiempos_entrega), 1)
        return 0.0
    
    # -------------------------
    def _calcular_valor_orden(self, orden: Dict[str, Any]) -> float:
        """Calcula el valor total de una orden basándose en sus productos"""
        valor_total = 0.0
        for producto_orden in orden.get("productos", []):
            # aceptar distintas keys en el payload
            pid = producto_orden.get("id_producto") or producto_orden.get("producto_id")
            cantidad = producto_orden.get("cantidad", 0)
            producto = None
            # intentar obtener producto desde DB local
            if pid:
                producto = self.db.query(Producto).filter(Producto.id == pid).first()

            if producto and producto.valor_unitario_usd:
                valor_total += float(producto.valor_unitario_usd) * cantidad
        
        return valor_total

    # -------------------------
    def _kpis_globales(self, filtros, ordenes: List[Dict[str, Any]], productos_lookup: Dict[int, Producto]):
        # Si hay filtro por país, filtrar por vendedores de ese país
        if filtros.pais:
            vendedores_pais = self.db.query(Vendedor.id).filter(
                Vendedor.pais_id.in_(filtros.pais)
            ).all()
            vendedor_ids = {v[0] for v in vendedores_pais}
            ordenes = [o for o in ordenes if (o.get("id_vendedor") or o.get("vendedor_id")) in vendedor_ids]

        # Calcular ventas totales usando lookup de productos
        ventas_totales = 0.0
        for orden in ordenes:
            for producto_orden in orden.get("productos", []):
                pid = producto_orden.get("id_producto") or producto_orden.get("producto_id")
                cantidad = producto_orden.get("cantidad", 0)
                prod = productos_lookup.get(pid) if productos_lookup else None
                if prod and prod.valor_unitario_usd:
                    ventas_totales += float(prod.valor_unitario_usd) * cantidad

        pedidos_totales = len(ordenes)

        # Calcular tiempo de entrega promedio real
        tiempo_entrega_promedio = self._calcular_tiempo_entrega_promedio(ordenes)

        # Calcular meta objetivo: si se filtró por vendedor, sumar solo sus planes;
        # si se filtró por país, sumar planes de ese país; sino sumar todas las metas.
        if getattr(filtros, 'vendedor_id', None):
            meta = self.db.query(func.sum(PlanVenta.meta_monetaria_usd)).filter(PlanVenta.vendedor_id == filtros.vendedor_id).scalar() or 0
        elif getattr(filtros, 'pais', None):
            # Si se pasaron múltiples paises, sumar planes cuyos pais estén en la lista
            meta = self.db.query(func.sum(PlanVenta.meta_monetaria_usd)).filter(PlanVenta.pais.in_(filtros.pais)).scalar() or 0
        else:
            meta = self.db.query(func.sum(PlanVenta.meta_monetaria_usd)).scalar() or 0
        if not meta:
            # fallback si no hay planes definidos
            meta = 100000
        cumplimiento = float(ventas_totales) / float(meta) if float(meta) > 0 else 0.0

        kpis = KPI(
            ventas_totales=float(ventas_totales),
            pedidos_mes=int(pedidos_totales),
            cumplimiento=round(cumplimiento, 2),
            tiempo_entrega_promedio_h=tiempo_entrega_promedio
        )
        return kpis, meta

    # -------------------------
    def _desempeno_por_vendedor(self, ordenes: List[Dict[str, Any]], productos_lookup: Dict[int, Producto], vendedores_lookup: Dict[int, Vendedor]):
        stats = self._agrupar_por_vendedor(ordenes, productos_lookup)

        out = []
        for vid, datos in stats.items():
            vendedor = vendedores_lookup.get(vid) or self.db.query(Vendedor).filter(Vendedor.id == vid).first()
            if not vendedor:
                continue

            ventas = datos["ventas"]

            # Intentar obtener meta asociada al vendedor (si PlanVenta tiene vendedor_id)
            meta_vendedor = None
            if hasattr(PlanVenta, 'vendedor_id'):
                meta_vendedor = self.db.query(func.sum(PlanVenta.meta_monetaria_usd)).filter(PlanVenta.vendedor_id == vid).scalar() or None

            # Determinar estado con lógica clara
            if meta_vendedor and meta_vendedor > 0:
                porcentaje = ventas / float(meta_vendedor)
                if porcentaje < 0.4:
                    estado = "LOW"
                elif porcentaje < 0.6:
                    estado = "WARN"
                elif porcentaje < 0.8:
                    estado = "OK"
                else:
                    estado = "HIGH"
            else:
                if ventas < 40000:
                    estado = "LOW"
                elif ventas < 60000:
                    estado = "WARN"
                elif ventas < 80000:
                    estado = "OK"
                else:
                    estado = "HIGH"

            out.append(DesempenoVendedorRow(
                vendedor=vendedor.nombre,
                pais=self._codigo_pais(vendedor.pais_id),
                pedidos=datos["pedidos"],
                ventas_usd=float(ventas),
                estado=estado
            ))
        return out

    def _agrupar_por_vendedor(self, ordenes: List[Dict[str, Any]], productos_lookup: Dict[int, Producto]):
        """Agrupa órdenes por vendedor y suma ventas/pedidos (usa productos_lookup)."""
        vendedor_stats = {}
        for orden in ordenes:
            vid = orden.get("id_vendedor") or orden.get("vendedor_id")
            if not vid:
                continue

            if vid not in vendedor_stats:
                vendedor_stats[vid] = {"ventas": 0.0, "pedidos": 0}

            ventas_orden = self._ventas_por_orden(orden, productos_lookup)
            vendedor_stats[vid]["ventas"] += ventas_orden
            vendedor_stats[vid]["pedidos"] += 1

        return vendedor_stats

    def _ventas_por_orden(self, orden: Dict[str, Any], productos_lookup: Dict[int, Producto]) -> float:
        """Suma el valor de los productos de una orden usando el lookup si está disponible."""
        total = 0.0
        for producto_orden in orden.get("productos", []):
            pid = producto_orden.get("id_producto") or producto_orden.get("producto_id")
            cantidad = producto_orden.get("cantidad", 0)
            prod = productos_lookup.get(pid) if productos_lookup else None
            if prod and prod.valor_unitario_usd:
                total += float(prod.valor_unitario_usd) * cantidad
        return total

    def _procesar_producto_para_categoria(self, producto_orden: Dict[str, Any], productos_lookup: Dict[int, Producto]):
        """Devuelve (categoria, unidades, ingresos) o None si no se puede procesar."""
        pid = producto_orden.get("id_producto") or producto_orden.get("producto_id")
        cantidad = producto_orden.get("cantidad", 0)
        if not pid:
            return None
        producto = productos_lookup.get(pid) if productos_lookup else None
        if not producto:
            producto = self.db.query(Producto).filter(Producto.id == pid).first()
            if not producto:
                return None

        categoria = producto.tipo_medicamento or getattr(producto, 'categoria', None) or "Sin categoría"
        ingresos = float(producto.valor_unitario_usd or 0) * cantidad
        return categoria, cantidad, ingresos

    def _codigo_pais(self, id_pais: int) -> str:
        mapa = {1: "COL", 2: "MEX", 3: "PER", 4: "ECU"}
        return mapa.get(id_pais, "ND")


    # -------------------------
    def _ventas_por_zona(self, ordenes: List[Dict[str, Any]], productos_lookup: Dict[int, Producto], vendedores_lookup: Dict[int, Vendedor]):
        # Agrupar por país del vendedor
        ventas_por_pais = {}
        for orden in ordenes:
            vid = orden.get("id_vendedor") or orden.get("vendedor_id")
            if not vid:
                continue

            vendedor = vendedores_lookup.get(vid) or self.db.query(Vendedor).filter(Vendedor.id == vid).first()
            if not vendedor:
                continue

            codigo_pais = self._codigo_pais(vendedor.pais_id)
            if codigo_pais not in ventas_por_pais:
                ventas_por_pais[codigo_pais] = 0.0

            # Calcular ventas por orden usando productos_lookup si está disponible
            for producto_orden in orden.get("productos", []):
                pid = producto_orden.get("id_producto") or producto_orden.get("producto_id")
                cantidad = producto_orden.get("cantidad", 0)
                prod = productos_lookup.get(pid) if productos_lookup else None
                if prod and prod.valor_unitario_usd:
                    ventas_por_pais[codigo_pais] += float(prod.valor_unitario_usd) * cantidad

        return [VentasPorRegionItem(zona=codigo, ventas_usd=float(ventas)) 
                for codigo, ventas in ventas_por_pais.items()]

    # -------------------------
    def _productos_por_categoria(self, ordenes: List[Dict[str, Any]], productos_lookup: Dict[int, Producto]):
        # Agrupar por categoría de producto
        categoria_stats = {}
        for orden in ordenes:
            for producto_orden in orden.get("productos", []):
                pid = producto_orden.get("id_producto") or producto_orden.get("producto_id")
                cantidad = producto_orden.get("cantidad", 0)
                producto = productos_lookup.get(pid) if productos_lookup else None
                if not producto:
                    # intentar buscar en DB si no está en lookup
                    if pid:
                        producto = self.db.query(Producto).filter(Producto.id == pid).first()
                    else:
                        continue

                categoria = producto.tipo_medicamento or getattr(producto, 'categoria', None) or "Sin categoría"
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
