from sqlalchemy import Column, Integer, String, DateTime, Float
from .database import Base
from datetime import datetime

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(String, index=True)
    producto = Column(String, index=True)
    cantidad = Column(Integer)
    estado = Column(String, default="pendiente")
    fecha_creacion = Column(DateTime, default=datetime.utcnow)