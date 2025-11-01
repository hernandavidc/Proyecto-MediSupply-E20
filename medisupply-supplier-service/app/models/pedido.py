from sqlalchemy import Column, Integer, String, ForeignKey, Date, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    vendedor_id = Column(Integer, ForeignKey("vendedores.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    fecha = Column(Date, nullable=False)
    cantidad = Column(Integer, nullable=False, default=1)
    valor_total_usd = Column(Numeric(12, 2), nullable=False)
    estado = Column(String(20), nullable=False, default="ENTREGADO")

    vendedor = relationship("Vendedor")
    cliente = relationship("Cliente")
    producto = relationship("Producto")
