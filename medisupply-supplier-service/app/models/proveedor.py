from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class Proveedor(Base):
    __tablename__ = "proveedores"
    id = Column(Integer, primary_key=True, index=True)
    razon_social = Column(String(255), nullable=False, index=True)
    paises_operacion = Column(JSON, nullable=False)
    certificaciones_sanitarias = Column(JSON, nullable=False)
    categorias_suministradas = Column(JSON, nullable=False)
    capacidad_cadena_frio = Column(JSON, nullable=True)
    estado = Column(String(50), nullable=False, server_default="PENDIENTE")
    contacto_principal = Column(String(255), nullable=True)
    email_contacto = Column(String(255), nullable=True)
    telefono_contacto = Column(String(50), nullable=True)
    tiene_productos_activos = Column(Boolean, default=False, nullable=False)
    notas = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)


class ProveedorAuditoria(Base):
    __tablename__ = "proveedores_auditoria"
    id = Column(Integer, primary_key=True, index=True)
    proveedor_id = Column(Integer, nullable=True)
    operacion = Column(String(20), nullable=False)
    usuario_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    datos_anteriores = Column(JSON, nullable=True)
    datos_nuevos = Column(JSON, nullable=True)
    campos_modificados = Column(JSON, nullable=True)
    ip_usuario = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
