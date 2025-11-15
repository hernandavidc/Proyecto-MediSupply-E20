from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Any

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

    @field_validator('pais', mode='before')
    @classmethod
    def pais_to_int(cls, v):
        """Acepta que el valor de `pais` venga como objeto ORM Pais o como entero.

        - Si es un objeto con atributo `id`, devuelve su id como int.
        - Si es un dict con key 'id', devuelve int(dict['id']).
        - Si es directamente convertible a int, lo convierte.
        Esto evita errores de validación cuando la capa de servicio retorna
        una instancia de SQLAlchemy `Pais` en la relación `vendedor.pais`.
        """
        if v is None:
            return v
        # SQLAlchemy ORM object con atributo id
        if hasattr(v, 'id'):
            try:
                return int(getattr(v, 'id'))
            except Exception:
                raise ValueError('pais inválido')
        # dict-like
        if isinstance(v, dict) and 'id' in v:
            try:
                return int(v['id'])
            except Exception:
                raise ValueError('pais inválido')
        # fallback: intentar convertir directamente
        try:
            return int(v)
        except Exception:
            raise ValueError('pais inválido')

class VendedorCreate(VendedorBase):
    pass

class VendedorResponse(VendedorBase):
    id: int

    class Config:
        from_attributes = True
