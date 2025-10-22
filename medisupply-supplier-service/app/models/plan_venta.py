from sqlalchemy import Column, Integer, String, Numeric, JSON, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class PlanVenta(Base):
    __tablename__ = 'planes_venta'
    id = Column(Integer, primary_key=True, index=True)
    vendedor_id = Column(Integer, nullable=False, index=True)
    periodo = Column(String(2), nullable=False)
    anio = Column(Integer, nullable=False)
    pais = Column(Integer, nullable=False)
    productos_objetivo = Column(JSON, nullable=False)
    meta_monetaria_usd = Column(Numeric(14,2), nullable=True)
    estado = Column(String(20), nullable=False, server_default='CREADO')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, nullable=True)

class PlanVentaAuditoria(Base):
    __tablename__ = 'planes_venta_auditoria'
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, nullable=True)
    operacion = Column(String(20), nullable=False)
    usuario_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    datos_anteriores = Column(JSON, nullable=True)
    datos_nuevos = Column(JSON, nullable=True)
    origen = Column(String(20), nullable=True)
