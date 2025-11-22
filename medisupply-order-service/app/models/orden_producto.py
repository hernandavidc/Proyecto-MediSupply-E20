from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class OrdenProducto(Base):
    __tablename__ = 'orden_producto'
    
    id_orden = Column(Integer, ForeignKey('ordenes.id'), primary_key=True)
    id_producto = Column(Integer, primary_key=True)
    cantidad = Column(Integer, nullable=False)
    
    # Relationships
    orden = relationship("Orden", back_populates="orden_productos")
