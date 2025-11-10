from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy import JSON as SA_JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Visita(Base):
    __tablename__ = 'visitas'
    id = Column(Integer, primary_key=True, index=True)
    vendedor_id = Column(Integer, ForeignKey('vendedores.id'), nullable=False)
    cliente_id = Column(Integer, nullable=True)
    direccion = Column(String(255), nullable=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    notas = Column(Text, nullable=True)
    evidencias = Column(SA_JSON, nullable=True)  # lista de URLs/paths de evidencias (fotos/videos)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    vendedor = relationship('Vendedor')

