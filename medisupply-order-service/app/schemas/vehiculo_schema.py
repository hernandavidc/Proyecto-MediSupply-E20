from typing import Optional
from pydantic import BaseModel
from app.models.vehiculo import TipoVehiculo


class VehiculoBase(BaseModel):
    id_conductor: int
    placa: str
    tipo: TipoVehiculo


class VehiculoCreate(VehiculoBase):
    pass


class VehiculoUpdate(BaseModel):
    id_conductor: Optional[int] = None
    placa: Optional[str] = None
    tipo: Optional[TipoVehiculo] = None


class VehiculoResponse(VehiculoBase):
    id: int

    class Config:
        from_attributes = True
