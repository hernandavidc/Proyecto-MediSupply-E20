from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy import ForeignKey


class Vendedor(Base):
    __tablename__ = 'vendedores'
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    pais_id = Column(Integer, ForeignKey("paises.id"), nullable=False)
    estado = Column(String(20), nullable=False, server_default='ACTIVO')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, nullable=True)

    # relación con clientes asignados (read-only via API)
    pais = relationship("Pais")
    clientes = relationship('Cliente', back_populates='vendedor', cascade='all, delete-orphan')


class VendedorAuditoria(Base):
    __tablename__ = 'vendedores_auditoria'
    id = Column(Integer, primary_key=True, index=True)
    vendedor_id = Column(Integer, nullable=True)
    operacion = Column(String(20), nullable=False)
    usuario_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    datos_anteriores = Column(String, nullable=True)
    datos_nuevos = Column(String, nullable=True)
