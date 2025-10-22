from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class ProveedorBase(BaseModel):
    razon_social: str = Field(..., min_length=1, max_length=255)
    paises_operacion: List[int] = Field(..., min_items=1)
    certificaciones_sanitarias: List[int] = Field(..., min_items=1)
    categorias_suministradas: List[int] = Field(..., min_items=1)
    capacidad_cadena_frio: Optional[List[str]] = None

    @field_validator('razon_social')
    @classmethod
    def not_blank(cls, v):
        if not v or not v.strip():
            raise ValueError('razon_social es obligatorio')
        return v.strip()

    @field_validator('paises_operacion', 'certificaciones_sanitarias', 'categorias_suministradas')
    @classmethod
    def non_empty_list(cls, v):
        if not v or len(v) == 0:
            raise ValueError('listas deben contener al menos un elemento')
        seen = set()
        out = []
        for item in v:
            if item not in seen:
                seen.add(item)
                out.append(item)
        return out

class ProveedorCreate(ProveedorBase):
    pass

class ProveedorUpdate(BaseModel):
    razon_social: Optional[str] = None
    paises_operacion: Optional[List[int]] = None
    certificaciones_sanitarias: Optional[List[int]] = None
    categorias_suministradas: Optional[List[int]] = None
    capacidad_cadena_frio: Optional[List[str]] = None

class ProveedorResponse(ProveedorBase):
    id: int
    estado: str
    tiene_productos_activos: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
