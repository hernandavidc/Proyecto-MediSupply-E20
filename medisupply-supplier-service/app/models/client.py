from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Cliente(Base):
    __tablename__ = 'clientes'

    id = Column(Integer, primary_key=True, index=True)
    vendedor_id = Column(Integer, ForeignKey('vendedores.id'), nullable=False, index=True)
    # id del usuario creado en el user-service asociado a este cliente
    user_id = Column(Integer, nullable=True, index=True)
    institucion_nombre = Column(String(255), nullable=False)
    direccion = Column(String(255), nullable=True)
    contacto_principal = Column(String(255), nullable=True)

    vendedor = relationship('Vendedor', back_populates='clientes')
