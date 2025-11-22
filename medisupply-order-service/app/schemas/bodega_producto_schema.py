from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BodegaProductoBase(BaseModel):
    id_bodega: int
    id_producto: int
    lote: str
    cantidad: int
    dias_alistamiento: int = Field(default=0, ge=0)


class BodegaProductoCreate(BodegaProductoBase):
    pass


class BodegaProductoUpdate(BaseModel):
    cantidad: Optional[int] = None
    dias_alistamiento: Optional[int] = Field(None, ge=0)


class BodegaProductoResponse(BodegaProductoBase):
    pronostico_entrega: Optional[datetime] = None
    
    class Config:
        from_attributes = True
