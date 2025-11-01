from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Index
from sqlalchemy.sql import func
from app.core.database import Base

class ReportMetric(Base):
    """
    Tabla auxiliar con métricas agregadas por vendedor, país, zona, categoría y fecha.
    Esta tabla puede ser poblada por un ETL, otro servicio, o cargas dummy para pruebas.
    """
    __tablename__ = "ventas_metricas"

    id = Column(Integer, primary_key=True, index=True)

    vendedor_id = Column(Integer, nullable=False, index=True)
    pais_id = Column(Integer, nullable=False, index=True)          # FK lógica a paises.id
    zona_geografica = Column(String(50), nullable=True, index=True)  # Norte | Centro | Sur (u otras)
    categoria_producto = Column(String(120), nullable=True, index=True)

    # Periodización
    periodo = Column(String(20), nullable=False)  # p.ej. "Q1", "Q2", "M03", "CUSTOM"
    fecha = Column(Date, nullable=False, index=True)

    # Métricas
    pedidos = Column(Integer, nullable=False, default=0)
    ventas_usd = Column(Numeric(14, 2), nullable=False, default=0.00)
    tiempo_entrega_horas = Column(Numeric(8, 2), nullable=True)  # promedio por registro

    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Índices compuestos útiles para filtros
Index("ix_vm_vendedor_fecha", ReportMetric.vendedor_id, ReportMetric.fecha)
Index("ix_vm_pais_zona_fecha", ReportMetric.pais_id, ReportMetric.zona_geografica, ReportMetric.fecha)
Index("ix_vm_categoria_fecha", ReportMetric.categoria_producto, ReportMetric.fecha)
