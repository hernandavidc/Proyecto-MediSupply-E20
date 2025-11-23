from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.vehiculo import TipoVehiculo


class VehiculoBase(BaseModel):
    id_conductor: int
    placa: str
    tipo: TipoVehiculo


class VehiculoCreate(VehiculoBase):
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    timestamp: Optional[datetime] = None


class VehiculoUpdate(BaseModel):
    id_conductor: Optional[int] = None
    placa: Optional[str] = None
    tipo: Optional[TipoVehiculo] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    timestamp: Optional[datetime] = None


class VehiculoResponse(VehiculoBase):
    id_vehiculo: int = Field(validation_alias="id")
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True
