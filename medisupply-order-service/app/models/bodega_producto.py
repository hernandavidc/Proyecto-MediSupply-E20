from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class BodegaProducto(Base):
    __tablename__ = 'bodega_producto'
    
    id_bodega = Column(Integer, ForeignKey('bodegas.id'), primary_key=True)
    id_producto = Column(Integer, primary_key=True)
    lote = Column(String(50), primary_key=True, nullable=False)
    cantidad = Column(Integer, nullable=False)
    dias_alistamiento = Column(Integer, nullable=False, default=0)
    
    # Relationships
    bodega = relationship("Bodega", back_populates="bodega_productos")
