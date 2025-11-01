from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class ClientBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=255, description="Company name")
    nit: str = Field(..., min_length=5, max_length=50, description="Tax identification number (NIT)")
    direccion: str = Field(..., min_length=10, max_length=500, description="Company address")
    nombre_contacto: str = Field(..., min_length=2, max_length=255, description="Contact person name")
    telefono_contacto: str = Field(..., min_length=7, max_length=20, description="Contact phone number")
    email_contacto: EmailStr = Field(..., description="Contact email address")
    
    @field_validator('nit')
    @classmethod
    def validate_nit_format(cls, v):
        """
        Validate NIT format (adjust according to country requirements)
        """
        # Remove spaces and hyphens
        nit_clean = re.sub(r'[\s-]', '', v)
        
        # Basic validation: should contain only digits and possibly one verification digit
        if not re.match(r'^\d{5,15}$', nit_clean):
            raise ValueError('NIT must contain between 5 and 15 digits')
        
        return nit_clean
    
    @field_validator('telefono_contacto')
    @classmethod
    def validate_phone(cls, v):
        """
        Validate phone number format
        """
        # Remove spaces, hyphens, and parentheses
        phone_clean = re.sub(r'[\s\-\(\)]', '', v)
        
        # Should contain only digits and possibly a plus sign at the beginning
        if not re.match(r'^\+?\d{7,15}$', phone_clean):
            raise ValueError('Phone number must contain between 7 and 15 digits')
        
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

