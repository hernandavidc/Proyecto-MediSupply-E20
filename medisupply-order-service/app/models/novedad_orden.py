from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class TipoNovedad(str, enum.Enum):
    DEVOLUCION = "DEVOLUCION"
    CANTIDAD_DIFERENTE = "CANTIDAD_DIFERENTE"
    MAL_ESTADO = "MAL_ESTADO"
    PRODUCTO_NO_COINCIDE = "PRODUCTO_NO_COINCIDE"


class NovedadOrden(Base):
    __tablename__ = 'novedad_orden'
    
    id = Column(Integer, primary_key=True, index=True)
    id_pedido = Column(Integer, ForeignKey('ordenes.id'), nullable=False, index=True)
    tipo = Column(SQLEnum(TipoNovedad), nullable=False)
    descripcion = Column(String(1000), nullable=True)
    
    # Relationships
    orden = relationship("Orden", back_populates="novedades")
