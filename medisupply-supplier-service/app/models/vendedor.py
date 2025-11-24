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
    # user_id guarda el id del usuario creado en el user-service asociado a este vendedor
    user_id = Column(Integer, nullable=True, index=True)

    # relación con clientes asignados (read-only via API)
    pais = relationship("Pais")
    clientes = relationship('Cliente', back_populates='vendedor', cascade='all, delete-orphan')

    def __init__(self, *args, **kwargs):
        # Permitir crear instancias usando el alias `pais` con un id entero
        # (ej. Vendedor(..., pais=1)) para compatibilidad con tests y seeds.
        if 'pais' in kwargs:
            pais_val = kwargs.pop('pais')
            # Si pasan un entero lo mapeamos a pais_id; si pasan un objeto ORM
            # dejamos que SQLAlchemy asigne la relación.
            if isinstance(pais_val, int):
                kwargs['pais_id'] = pais_val
            else:
                # reintroducir 'pais' para que SQLAlchemy asigne la relación
                kwargs['pais'] = pais_val
        super().__init__(*args, **kwargs)


class VendedorAuditoria(Base):
    __tablename__ = 'vendedores_auditoria'
    id = Column(Integer, primary_key=True, index=True)
    vendedor_id = Column(Integer, nullable=True)
    operacion = Column(String(20), nullable=False)
    usuario_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    datos_anteriores = Column(String, nullable=True)
    datos_nuevos = Column(String, nullable=True)
