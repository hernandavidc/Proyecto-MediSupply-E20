from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, validator
from datetime import date, datetime

TIPOS_MEDICAMENTO = [
    "Analgésicos","Antibióticos","Antiinflamatorios","Antivirales","Antifúngicos","Antipiréticos",
    "Antihistamínicos","Anticonvulsivos","Antidepresivos","Antipsicóticos","Antidiabéticos","Antihipertensivos",
    "Anticoagulantes","Antieméticos","Antiespasmódicos","Broncodilatadores","Corticoides","Diuréticos",
    "Inmunosupresores","Vacunas","Otros"
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

    @field_validator('sku')
    @classmethod
    def sku_not_zero(cls, v):
        if '0' in v:
            raise ValueError('SKU no puede contener el caracter 0')
        return v

    @validator('tipo_medicamento')
    def tipo_valido(cls, v):
        if v is None:
            return v
        if v not in TIPOS_MEDICAMENTO:
            raise ValueError('tipo de medicamento inválido')
        return v

class ProductoCreate(ProductoBase):
    pass

class ProductoResponse(ProductoBase):
    id: int
    origen: Optional[str]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ErrorDetalle(BaseModel):
    linea: int
    campo: str
    valor: str
    error: str

class ProductoBulkResponse(BaseModel):
    total_procesados: int
    exitosos: int
    fallidos: int
    productos_creados: List[ProductoResponse]
    errores: List[ErrorDetalle]
    mensaje: str
