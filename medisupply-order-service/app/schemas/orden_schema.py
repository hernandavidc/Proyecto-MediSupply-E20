from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class EstadoOrden(str, Enum):
    ABIERTO = "ABIERTO"
    ENTREGADO = "ENTREGADO"
    EN_ALISTAMIENTO = "EN_ALISTAMIENTO"
    EN_REPARTO = "EN_REPARTO"
    DEVUELTO = "DEVUELTO"
    POR_ALISTAR = "POR_ALISTAR"


class ProductoOrden(BaseModel):
    id_producto: int
    cantidad: int


class OrdenBase(BaseModel):
    fecha_entrega_estimada: datetime
    id_vehiculo: Optional[int] = None
    id_cliente: int
    id_vendedor: int


class OrdenCreate(OrdenBase):
    productos: List[ProductoOrden] = []
    estado: Optional[EstadoOrden] = EstadoOrden.ABIERTO


class OrdenUpdate(BaseModel):
    fecha_entrega_estimada: Optional[datetime] = None
    id_vehiculo: Optional[int] = None
    id_cliente: Optional[int] = None
    id_vendedor: Optional[int] = None
    estado: Optional[EstadoOrden] = None
    productos: Optional[List[ProductoOrden]] = None


class OrdenResponse(OrdenBase):
    id: int
    estado: EstadoOrden
    fecha_creacion: datetime
    productos: List[ProductoOrden] = []

    class Config:
        from_attributes = True
