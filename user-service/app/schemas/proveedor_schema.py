"""
Schemas Pydantic para Proveedor
Implementa todas las validaciones de HU-001
"""

from typing import List, Optional
from pydantic import BaseModel, field_validator, Field
from datetime import datetime
from app.core.enums import (
    PaisOperacion,
    CertificacionSanitaria,
    CategoriaSuministro,
    CapacidadCadenaFrio,
    EstadoProveedor,
)


class ProveedorBase(BaseModel):
    """Schema base para Proveedor"""

    razon_social: str = Field(
        ..., min_length=1, max_length=255, description="Razón social del proveedor"
    )
    paises_operacion: List[PaisOperacion] = Field(
        ..., min_items=1, description="Países donde opera (mínimo 1)"
    )
    certificaciones_sanitarias: List[CertificacionSanitaria] = Field(
        ..., min_items=1, description="Certificaciones sanitarias (mínimo 1)"
    )
    categorias_suministradas: List[CategoriaSuministro] = Field(
        ..., min_items=1, description="Categorías de suministros"
    )
    capacidad_cadena_frio: Optional[List[CapacidadCadenaFrio]] = Field(
        default=None, description="Capacidades de cadena de frío"
    )
    contacto_principal: Optional[str] = Field(None, max_length=255)
    email_contacto: Optional[str] = Field(None, max_length=255)
    telefono_contacto: Optional[str] = Field(None, max_length=50)
    notas: Optional[str] = Field(None, description="Notas internas")

    @field_validator("razon_social")
    @classmethod
    def validar_razon_social(cls, v):
        """Validar que razon_social no sea solo espacios"""
        if not v or v.strip() == "":
            raise ValueError(
                "La razón social no puede estar vacía o contener solo espacios"
            )
        return v.strip()

    @field_validator("paises_operacion")
    @classmethod
    def validar_paises_operacion(cls, v):
        """Validar países de operación"""
        if not v or len(v) < 1:
            raise ValueError("Debe seleccionar al menos un país de operación")

        # Eliminar duplicados manteniendo orden
        seen = set()
        unique_list = []
        for item in v:
            if item not in seen:
                seen.add(item)
                unique_list.append(item)

        # Validar que todos los países estén en la lista permitida
        valid_countries = [pais.value for pais in PaisOperacion]
        for pais in unique_list:
            if pais not in valid_countries:
                raise ValueError(
                    f"País no válido: {pais}. Países permitidos: {', '.join(valid_countries)}"
                )

        return unique_list

    @field_validator("certificaciones_sanitarias")
    @classmethod
    def validar_certificaciones(cls, v):
        """Validar certificaciones sanitarias"""
        if not v or len(v) < 1:
            raise ValueError("Debe seleccionar al menos una certificación sanitaria")

        # Eliminar duplicados
        unique_certs = list(set(v))

        # Validar que todas las certificaciones estén en la lista permitida
        valid_certs = [cert.value for cert in CertificacionSanitaria]
        for cert in unique_certs:
            if cert not in valid_certs:
                raise ValueError(
                    f"Certificación no válida: {cert}. Certificaciones permitidas: {', '.join(valid_certs)}"
                )

        return unique_certs

    @field_validator("categorias_suministradas")
    @classmethod
    def validar_categorias(cls, v):
        """Validar categorías de suministros"""
        if not v or len(v) < 1:
            raise ValueError("Debe seleccionar al menos una categoría de suministro")

        # Eliminar duplicados
        unique_cats = list(set(v))

        # Validar que todas las categorías estén en la lista permitida
        valid_cats = [cat.value for cat in CategoriaSuministro]
        for cat in unique_cats:
            if cat not in valid_cats:
                raise ValueError(
                    f"Categoría no válida: {cat}. Categorías permitidas: {', '.join(valid_cats)}"
                )

        return unique_cats

    @field_validator("capacidad_cadena_frio")
    @classmethod
    def validar_cadena_frio(cls, v):
        """Validar capacidades de cadena de frío"""
        if v is None:
            return v

        if len(v) == 0:
            return None

        # Eliminar duplicados
        unique_caps = list(set(v))

        # Validar que todas las capacidades estén en la lista permitida
        valid_caps = [cap.value for cap in CapacidadCadenaFrio]
        for cap in unique_caps:
            if cap not in valid_caps:
                raise ValueError(
                    f"Capacidad no válida: {cap}. Capacidades permitidas: {', '.join(valid_caps)}"
                )

        return unique_caps

    @field_validator("email_contacto")
    @classmethod
    def validar_email(cls, v):
        """Validar formato de email si se proporciona"""
        if v and v.strip():
            import re

            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, v.strip()):
                raise ValueError("Formato de email no válido")
            return v.strip()
        return v


class ProveedorCreate(ProveedorBase):
    """Schema para crear proveedor"""

    pass


class ProveedorUpdate(BaseModel):
    """Schema para actualizar proveedor (campos opcionales)"""

    razon_social: Optional[str] = Field(None, min_length=1, max_length=255)
    paises_operacion: Optional[List[PaisOperacion]] = Field(None, min_items=1)
    certificaciones_sanitarias: Optional[List[CertificacionSanitaria]] = Field(
        None, min_items=1
    )
    categorias_suministradas: Optional[List[CategoriaSuministro]] = Field(
        None, min_items=1
    )
    capacidad_cadena_frio: Optional[List[CapacidadCadenaFrio]] = None
    contacto_principal: Optional[str] = Field(None, max_length=255)
    email_contacto: Optional[str] = Field(None, max_length=255)
    telefono_contacto: Optional[str] = Field(None, max_length=50)
    notas: Optional[str] = None
    estado: Optional[EstadoProveedor] = None

    # Reutilizar validadores de ProveedorBase para campos que los necesiten
    @field_validator("razon_social")
    @classmethod
    def validar_razon_social(cls, v):
        if v is not None:
            return ProveedorBase.validar_razon_social(v)
        return v

    @field_validator("paises_operacion")
    @classmethod
    def validar_paises_operacion(cls, v):
        if v is not None:
            return ProveedorBase.validar_paises_operacion(v)
        return v

    @field_validator("certificaciones_sanitarias")
    @classmethod
    def validar_certificaciones(cls, v):
        if v is not None:
            return ProveedorBase.validar_certificaciones(v)
        return v

    @field_validator("categorias_suministradas")
    @classmethod
    def validar_categorias(cls, v):
        if v is not None:
            return ProveedorBase.validar_categorias(v)
        return v

    @field_validator("capacidad_cadena_frio")
    @classmethod
    def validar_cadena_frio(cls, v):
        if v is not None:
            return ProveedorBase.validar_cadena_frio(v)
        return v

    @field_validator("email_contacto")
    @classmethod
    def validar_email(cls, v):
        if v is not None:
            return ProveedorBase.validar_email(v)
        return v


class ProveedorResponse(ProveedorBase):
    """Schema para respuesta de proveedor"""

    id: int
    estado: EstadoProveedor
    tiene_productos_activos: bool
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: Optional[int]

    class Config:
        from_attributes = True


class ProveedorList(BaseModel):
    """Schema para lista de proveedores"""

    id: int
    razon_social: str
    estado: EstadoProveedor
    paises_operacion: List[str]
    tiene_productos_activos: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProveedorAuditoriaResponse(BaseModel):
    """Schema para respuesta de auditoría"""

    id: int
    proveedor_id: int
    operacion: str
    usuario_id: int
    timestamp: datetime
    datos_anteriores: Optional[dict]
    datos_nuevos: Optional[dict]
    campos_modificados: Optional[List[str]]

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Schema para respuestas de error"""

    detail: str
    error_code: Optional[str] = None
    field_errors: Optional[dict] = None
