from typing import Optional, List
from pydantic import BaseModel, field_validator
from app.models.novedad_orden import TipoNovedad
import json


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
    fotos: Optional[List[str]] = None  # Lista de URLs de las fotos

    @field_validator('fotos', mode='before')
    @classmethod
    def parse_fotos_json(cls, v):
        """Convierte el string JSON de fotos a lista"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, ValueError):
                return None
        return v

    class Config:
        from_attributes = True
