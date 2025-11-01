from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class Client(Base):
    __tablename__ = "clients"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(255), nullable=False, index=True)
    nit = Column(String(50), unique=True, nullable=False, index=True)
    direccion = Column(String(500), nullable=False)
    nombre_contacto = Column(String(255), nullable=False)
    telefono_contacto = Column(String(20), nullable=False)
    email_contacto = Column(String(255), nullable=False)
    is_validated = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Client(id={self.id}, nombre={self.nombre}, nit={self.nit})>"

