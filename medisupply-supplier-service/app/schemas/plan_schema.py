from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

PERIODOS = ["Q1", "Q2", "Q3", "Q4"]


class PlanCreate(BaseModel):
    vendedor_id: int
    periodo: str
    anio: int
    pais: int
    productos_objetivo: List[int] = Field(..., min_length=1)
    meta_monetaria_usd: Optional[float] = None

    @field_validator("vendedor_id")
    @classmethod
    def vendedor_must_be_positive(cls, v):
        if v is None or v <= 0:
            raise ValueError("vendedor_id inválido")
        return v

    @field_validator("periodo")
    @classmethod
    def periodo_valido(cls, v):
        if v not in PERIODOS:
            raise ValueError("periodo inválido")
        return v

    @field_validator("anio")
    @classmethod
    def anio_valido(cls, v):
        if v < 1900 or v > 9999:
            raise ValueError("anio inválido")
        return v

    @field_validator("meta_monetaria_usd")
    @classmethod
    def meta_valida(cls, v):
        if v is None:
            return v
        if v <= 0:
            raise ValueError("meta_monetaria_usd debe ser > 0")
        return round(v, 2)


class PlanResponse(PlanCreate):
    id: int
    estado: str

    model_config = ConfigDict(from_attributes=True)
