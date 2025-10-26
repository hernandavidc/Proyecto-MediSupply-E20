from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, validator
from datetime import date
import csv

TIPOS_MEDICAMENTO = [
    "Analgésicos",
    "Antibióticos",
    "Antiinflamatorios",
    "Antivirales",
    "Antifúngicos",
    "Antipiréticos",
    "Antihistamínicos",
    "Anticonvulsivos",
    "Antidepresivos",
    "Antipsicóticos",
    "Antidiabéticos",
    "Antihipertensivos",
    "Anticoagulantes",
    "Antieméticos",
    "Antiespasmódicos",
    "Broncodilatadores",
    "Corticoides",
    "Diuréticos",
    "Inmunosupresores",
    "Vacunas",
    "Otros",
]


class Condiciones(BaseModel):
    temperatura: Optional[str]
    humedad: Optional[str]
    luz: Optional[str]
    ventilacion: Optional[str]
    seguridad: Optional[str]
    envase: Optional[str]


class Organizacion(BaseModel):
    tipo_medicamento: Optional[str]
    fecha_vencimiento: Optional[date]


class ProductoBase(BaseModel):
    sku: str = Field(..., min_length=1, max_length=100)
    nombre_producto: str = Field(..., min_length=1, max_length=255)
    proveedor_id: int
    ficha_tecnica_url: Optional[str] = None
    condiciones: Optional[Condiciones] = None
    organizacion: Optional[Organizacion] = None
    tipo_medicamento: Optional[str] = None
    fecha_vencimiento: Optional[date] = None
    valor_unitario_usd: float = Field(..., gt=0)
    certificaciones: Optional[List[int]] = None
    tiempo_entrega_dias: Optional[int] = None

    @field_validator("sku")
    @classmethod
    def sku_not_zero(cls, v):
        if "0" in v:
            raise ValueError("SKU no puede contener el caracter 0")
        return v

    @validator("tipo_medicamento")
    def tipo_valido(cls, v):
        if v is None:
            return v
        if v not in TIPOS_MEDICAMENTO:
            raise ValueError("tipo de medicamento inválido")
        return v


class ProductoCreate(ProductoBase):
    pass


class ProductoResponse(ProductoBase):
    id: int
    origen: Optional[str]

    class Config:
        from_attributes = True


# Esquemas para carga masiva
class CondicionesAlmacenamiento(BaseModel):
    ca_temp: Optional[str] = None
    ca_humedad: Optional[str] = None
    ca_luz: Optional[str] = None
    ca_ventilacion: Optional[str] = None
    ca_seguridad: Optional[str] = None
    ca_envase: Optional[str] = None


class OrganizacionProducto(BaseModel):
    org_tipo_medicamento: Optional[str] = None
    org_fecha_vencimiento: Optional[date] = None

    @validator("org_tipo_medicamento")
    def tipo_medicamento_valido(cls, v):
        if v is None or v.strip() == "":
            return None
        if v not in TIPOS_MEDICAMENTO:
            raise ValueError("tipo de medicamento inválido")
        return v


class ProductoCSV(BaseModel):
    sku: str = Field(..., min_length=1, max_length=100)
    nombre_producto: str = Field(..., min_length=1, max_length=255)
    proveedor_id: int
    ficha_tecnica_url: Optional[str] = None
    condicion_almacenamiento: Optional[CondicionesAlmacenamiento] = None
    organizacion: Optional[OrganizacionProducto] = None
    valor_unitario_usd: float = Field(..., gt=0)
    certificaciones_sanitarias: Optional[str] = None  # Lista separada por ;

    @field_validator("sku")
    @classmethod
    def sku_not_zero(cls, v):
        if "0" in v:
            raise ValueError("SKU no puede contener el caracter 0")
        return v

    @validator("certificaciones_sanitarias")
    def parse_certificaciones(cls, v):
        if v is None or v.strip() == "":
            return []
        return [int(x.strip()) for x in v.split(";") if x.strip()]


class ErrorValidacion(BaseModel):
    linea: int
    campo: str
    error: str
    valor: Optional[str] = None


class ResultadoCargaMasiva(BaseModel):
    total_lineas: int
    exitosas: int
    fallidas: int
    errores: List[ErrorValidacion]
    productos_creados: List[ProductoResponse] = []


class ConfiguracionCarga(BaseModel):
    rechazar_lote_ante_errores: bool = True
