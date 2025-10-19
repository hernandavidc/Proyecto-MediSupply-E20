from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

class VendedorBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    pais: int
    estado: str

    @field_validator('nombre')
    @classmethod
    def nombre_no_vacio(cls, v):
        if not v or not v.strip():
            raise ValueError('nombre is required')
        return v.strip()

class VendedorCreate(VendedorBase):
    pass

class VendedorResponse(VendedorBase):
    id: int

    class Config:
        from_attributes = True
