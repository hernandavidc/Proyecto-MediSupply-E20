from pydantic import BaseModel, Field, validator
from datetime import date
from typing import List, Optional, Literal, Dict

PeriodoTiempo = Literal["MES_ACTUAL", "TRIMESTRE_ACTUAL", "ANIO_ACTUAL", "PERSONALIZADO"]
TipoReporte = Literal["DESEMPENO_VENDEDOR", "VENTAS_POR_PRODUCTO", "CUMPLIMIENTO_METAS", "VENTAS_POR_ZONA"]

ZonasPermitidas = {"Norte", "Centro", "Sur"}  # Ajustable

class ReporteRequest(BaseModel):
    vendedor_id: Optional[int] = Field(None, description="Opcional: filtra por vendedor")
    pais: List[int] = Field(default_factory=list, description="IDs de países (multi-select)")
    zona_geografica: List[str] = Field(default_factory=list, description="Zonas (multi-select)")
    periodo_tiempo: PeriodoTiempo
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    categoria_producto: List[str] = Field(default_factory=list)
    tipo_reporte: List[TipoReporte] = Field(..., min_items=1)

    # Validaciones de HU
    @validator("zona_geografica", each_item=True)
    def _validar_zonas(cls, z):
        if z not in ZonasPermitidas:
            raise ValueError(f"zona_geografica inválida: {z}")
        return z

    @validator("fecha_fin")
    def _validar_fechas(cls, fin, values):
        periodo = values.get("periodo_tiempo")
        ini = values.get("fecha_inicio")
        if periodo == "PERSONALIZADO":
            if not ini or not fin:
                raise ValueError("Debe indicar fecha_inicio y fecha_fin para periodo PERSONALIZADO")
            if fin <= ini:
                raise ValueError("fecha_fin debe ser mayor a fecha_inicio")
            # rango máximo 2 años
            delta = (fin - ini).days
            if delta > 366 * 2:
                raise ValueError("El rango de fechas no puede superar 2 años")
        return fin

    @validator("tipo_reporte")
    def _minimo_un_reporte(cls, tipos):
        if not tipos:
            raise ValueError("Debe seleccionar al menos un tipo de reporte")
        return tipos

    @validator("pais")
    def _al_menos_un_filtro_de_segmento(cls, paises, values):
        vendedor_id = values.get("vendedor_id")
        zonas = values.get("zona_geografica") or []
        if not vendedor_id and not paises and not zonas:
            raise ValueError("Debe seleccionar al menos un filtro: vendedor, país o zona_geografica")
        return paises


# ----- Responses -----

class KPI(BaseModel):
    ventas_totales: float
    pedidos_mes: int
    cumplimiento: float  # 0..1
    tiempo_entrega_promedio_h: float

class DesempenoVendedorRow(BaseModel):
    vendedor: str
    pais: str
    pedidos: int
    ventas_usd: float
    estado: Literal["OK", "WARN", "HIGH", "LOW"]

class VentasPorRegionItem(BaseModel):
    zona: str
    ventas_usd: float

class ProductosCategoriaItem(BaseModel):
    categoria: str
    unidades: int
    ingresos_usd: float
    porcentaje: float

class ReporteResponse(BaseModel):
    kpis: KPI
    desempeno_vendedores: Optional[List[DesempenoVendedorRow]] = None
    ventas_por_region: Optional[List[VentasPorRegionItem]] = None
    productos_por_categoria: Optional[List[ProductosCategoriaItem]] = None
    # opcionalmente puedes incluir "historial_pedidos" si luego agregas esa vista
    meta_objetivo_usd: Optional[float] = None  # para mostrar la meta usada en KPIs
    filtros_aplicados: Dict[str, object]
