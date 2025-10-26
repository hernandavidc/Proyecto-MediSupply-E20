"""
Modelo Proveedor para MediSupply
Implementa HU-001 con auditoría completa
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    ARRAY,
    Boolean,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
from app.core.enums import (
    PaisOperacion,
    CertificacionSanitaria,
    CategoriaSuministro,
    CapacidadCadenaFrio,
    EstadoProveedor,
)


class BaseAuditModel:
    """Modelo base con campos de auditoría"""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    created_by = Column(Integer, nullable=False)  # ID del usuario que creó
    updated_by = Column(Integer, nullable=True)  # ID del usuario que actualizó


class Proveedor(Base, BaseAuditModel):
    """
    Modelo de Proveedor según HU-001
    Incluye todos los campos requeridos y auditoría
    """

    __tablename__ = "proveedores"

    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    razon_social = Column(String(255), nullable=False, index=True)

    # Campos de listas múltiples (almacenados como arrays de strings)
    paises_operacion = Column(ARRAY(String), nullable=False)
    certificaciones_sanitarias = Column(ARRAY(String), nullable=False)
    categorias_suministradas = Column(ARRAY(String), nullable=False)
    capacidad_cadena_frio = Column(ARRAY(String), nullable=True)

    # Estado del proveedor
    estado = Column(
        String(50), default=EstadoProveedor.PENDIENTE_APROBACION, nullable=False
    )

    # Información adicional
    contacto_principal = Column(String(255), nullable=True)
    email_contacto = Column(String(255), nullable=True)
    telefono_contacto = Column(String(50), nullable=True)

    # Campo para verificar si tiene productos asociados
    tiene_productos_activos = Column(Boolean, default=False, nullable=False)

    # Notas internas
    notas = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Proveedor(id={self.id}, razon_social='{self.razon_social}')>"


class ProveedorAuditoria(Base):
    """
    Tabla de auditoría para cambios en proveedores
    Registra antes/después según HU-001
    """

    __tablename__ = "proveedores_auditoria"

    id = Column(Integer, primary_key=True, index=True)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=False)

    # Información de la modificación
    operacion = Column(String(20), nullable=False)  # CREATE, UPDATE, DELETE
    usuario_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Datos antes y después del cambio
    datos_anteriores = Column(JSON, nullable=True)
    datos_nuevos = Column(JSON, nullable=True)

    # Campos específicos modificados
    campos_modificados = Column(ARRAY(String), nullable=True)

    # IP y metadatos adicionales
    ip_usuario = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)

    def __repr__(self):
        return f"<ProveedorAuditoria(id={self.id}, proveedor_id={self.proveedor_id}, operacion='{self.operacion}')>"
