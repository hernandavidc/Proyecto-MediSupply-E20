from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, JSON, Boolean, Text
from sqlalchemy.sql import func
from app.core.database import Base

class Producto(Base):
    __tablename__ = 'productos'
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(100), nullable=False, index=True)
    nombre_producto = Column(String(255), nullable=False)
    proveedor_id = Column(Integer, nullable=False, index=True)
    ficha_tecnica_url = Column(String(2048), nullable=True)
    ficha_tecnica_pdf = Column(String(1024), nullable=True)  # path/filename si se sube
    condiciones = Column(JSON, nullable=True)
    organizacion = Column(JSON, nullable=True)
    tipo_medicamento = Column(String(100), nullable=True)
    fecha_vencimiento = Column(Date, nullable=True)
    valor_unitario_usd = Column(Numeric(12,2), nullable=False)
    certificaciones = Column(JSON, nullable=True)
    tiempo_entrega_dias = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())
    origen = Column(String(20), nullable=False, server_default='MANUAL')

class ProductoAuditoria(Base):
    __tablename__ = 'productos_auditoria'
    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, nullable=True)
    operacion = Column(String(20), nullable=False)
    usuario_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    datos_anteriores = Column(JSON, nullable=True)
    datos_nuevos = Column(JSON, nullable=True)
    origen = Column(String(20), nullable=True)
    errores_validacion = Column(JSON, nullable=True)
