from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class EstadoOrden(str, enum.Enum):
    ABIERTO = "ABIERTO"
    ENTREGADO = "ENTREGADO"
    EN_ALISTAMIENTO = "EN_ALISTAMIENTO"
    EN_REPARTO = "EN_REPARTO"
    DEVUELTO = "DEVUELTO"
    POR_ALISTAR = "POR_ALISTAR"


class Orden(Base):
    __tablename__ = 'ordenes'
    
    id = Column(Integer, primary_key=True, index=True)
    fecha_entrega_estimada = Column(DateTime, nullable=False)
    id_vehiculo = Column(Integer, ForeignKey('vehiculos.id'), nullable=True)
    id_cliente = Column(Integer, nullable=False, index=True)
    id_vendedor = Column(Integer, nullable=False, index=True)
    estado = Column(Enum(EstadoOrden), nullable=False, default=EstadoOrden.ABIERTO, server_default=EstadoOrden.ABIERTO.value)
    fecha_creacion = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relationships
    vehiculo = relationship("Vehiculo", back_populates="ordenes")
    orden_productos = relationship("OrdenProducto", back_populates="orden", cascade="all, delete-orphan")
    novedades = relationship("NovedadOrden", back_populates="orden", cascade="all, delete-orphan")
