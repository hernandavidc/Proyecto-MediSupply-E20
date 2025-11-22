from typing import Optional
from pydantic import BaseModel
from app.models.novedad_orden import TipoNovedad


class NovedadOrdenBase(BaseModel):
    id_pedido: int
    tipo: TipoNovedad
    descripcion: Optional[str] = None


class NovedadOrdenCreate(NovedadOrdenBase):
    pass


class NovedadOrdenUpdate(BaseModel):
    tipo: Optional[TipoNovedad] = None
    descripcion: Optional[str] = None


class NovedadOrdenResponse(NovedadOrdenBase):
    id: int

    class Config:
        from_attributes = True
