from typing import Optional
from pydantic import BaseModel
from decimal import Decimal


class BodegaBase(BaseModel):
    nombre: str
    direccion: str
    id_pais: int
    ciudad: str
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None


class BodegaCreate(BodegaBase):
    pass


class BodegaUpdate(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    id_pais: Optional[int] = None
    ciudad: Optional[str] = None
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None


class BodegaResponse(BodegaBase):
    id: int

    class Config:
        from_attributes = True
