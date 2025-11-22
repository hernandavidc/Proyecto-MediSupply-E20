from sqlalchemy import Column, Integer, String, Enum as SQLEnum
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
    
    # Relationships
    ordenes = relationship("Orden", back_populates="vehiculo")
