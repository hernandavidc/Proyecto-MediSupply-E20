from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class ClientBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=255, description="Nombre de la empresa")
    nit: str = Field(..., min_length=5, max_length=50, description="Número de identificación tributaria (NIT)")
    direccion: str = Field(..., min_length=10, max_length=500, description="Dirección de la empresa")
    nombre_contacto: str = Field(..., min_length=2, max_length=255, description="Nombre de la persona de contacto")
    telefono_contacto: str = Field(..., min_length=7, max_length=20, description="Número de teléfono de contacto")
    email_contacto: EmailStr = Field(..., description="Dirección de correo electrónico de contacto")
    
    @field_validator('nit')
    @classmethod
    def validate_nit_format(cls, v):
        """
        Validate NIT format (adjust according to country requirements)
        """
        # Remove spaces and hyphens
        nit_clean = re.sub(r'[\s-]', '', v)
        
        # Validación básica: debe contener solo dígitos
        if not re.match(r'^\d{5,15}$', nit_clean):
            raise ValueError('El NIT debe contener entre 5 y 15 dígitos')
        
        return nit_clean
    
    @field_validator('telefono_contacto')
    @classmethod
    def validate_phone(cls, v):
        """
        Validate phone number format
        """
        # Remove spaces, hyphens, and parentheses
        phone_clean = re.sub(r'[\s\-\(\)]', '', v)
        
        # Debe contener solo dígitos y posiblemente un signo más al inicio
        if not re.match(r'^\+?\d{7,15}$', phone_clean):
            raise ValueError('El número de teléfono debe contener entre 7 y 15 dígitos')
        
        return phone_clean


class ClientCreate(ClientBase):
    """
    Schema for creating a new client
    """
    pass


class ClientUpdate(BaseModel):
    """
    Schema for updating a client (all fields optional)
    """
    nombre: Optional[str] = Field(None, min_length=2, max_length=255)
    direccion: Optional[str] = Field(None, min_length=10, max_length=500)
    nombre_contacto: Optional[str] = Field(None, min_length=2, max_length=255)
    telefono_contacto: Optional[str] = Field(None, min_length=7, max_length=20)
    email_contacto: Optional[EmailStr] = None


class ClientResponse(ClientBase):
    """
    Schema for client response
    """
    id: str
    is_validated: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class NITValidationResponse(BaseModel):
    """
    Schema for NIT validation response
    """
    nit: str
    is_valid: bool
    company_name: Optional[str] = None
    company_status: Optional[str] = None
    message: str


class ClientListResponse(BaseModel):
    """
    Schema for paginated client list
    """
    total: int
    page: int
    page_size: int
    clients: list[ClientResponse]

