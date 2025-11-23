from sqlalchemy import Column, Integer, String, Enum as SQLEnum, Float, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class TipoVehiculo(str, enum.Enum):
    CAMION = "CAMION"
    VAN = "VAN"
    TRACTOMULA = "TRACTOMULA"


class Vehiculo(Base):
    __tablename__ = 'vehiculos'
    
    id = Column(Integer, primary_key=True, index=True)
    id_conductor = Column(Integer, nullable=False, index=True)
    placa = Column(String(20), nullable=False, unique=True, index=True)
    tipo = Column(SQLEnum(TipoVehiculo), nullable=False)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    timestamp = Column(DateTime, nullable=True)
    
    # Relationships
    ordenes = relationship("Orden", back_populates="vehiculo")
