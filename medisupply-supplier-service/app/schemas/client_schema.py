from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class ClienteBase(BaseModel):
    institucion_nombre: str = Field(..., min_length=1, max_length=255)
    direccion: Optional[str] = None
    contacto_principal: Optional[str] = None


class ClienteCreate(ClienteBase):
    pass


class ClienteResponse(ClienteBase):
    id: int
    vendedor_id: int
    # id del usuario creado en el user-service asociado a este cliente
    user_id: Optional[int] = None

    class Config:
        from_attributes = True


class CreatedUser(BaseModel):
    id: Optional[int]
    email: EmailStr
    password: str


class ClienteCreateResponse(BaseModel):
    cliente: ClienteResponse
    user: CreatedUser

    class Config:
        from_attributes = True
