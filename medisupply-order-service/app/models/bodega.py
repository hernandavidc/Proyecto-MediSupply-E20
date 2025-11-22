from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base


class Bodega(Base):
    __tablename__ = 'bodegas'
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    direccion = Column(String(500), nullable=False)
    id_pais = Column(Integer, nullable=False, index=True)
    ciudad = Column(String(100), nullable=False)
    latitud = Column(Numeric(10, 8), nullable=True)
    longitud = Column(Numeric(11, 8), nullable=True)
    
    # Relationships
    bodega_productos = relationship("BodegaProducto", back_populates="bodega", cascade="all, delete-orphan")
