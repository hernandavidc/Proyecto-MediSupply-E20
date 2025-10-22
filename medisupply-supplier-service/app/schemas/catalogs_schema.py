from pydantic import BaseModel

class PaisOut(BaseModel):
    id: int
    nombre: str

class CertificacionOut(BaseModel):
    id: int
    codigo: str
    nombre: str

class CategoriaOut(BaseModel):
    id: int
    nombre: str
