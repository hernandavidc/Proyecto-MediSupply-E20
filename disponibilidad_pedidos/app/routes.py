from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Pedido
from .schemas import PedidoCreate
from .redis_client import redis_client
from datetime import datetime
import json

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/pedidos")
def crear_pedido(pedido: PedidoCreate, db: Session = Depends(get_db)):
    """
    Endpoint para crear un pedido.
    """
    try:
        # Guardar directamente en PostgreSQL
        nuevo_pedido = Pedido(
            cliente=pedido.cliente,
            producto=pedido.producto,
            cantidad=pedido.cantidad
        )
        db.add(nuevo_pedido)
        db.commit()
        db.refresh(nuevo_pedido)
        return {"message": "Pedido creado", "id": nuevo_pedido.id}

    except Exception:
        # Si hay error (ejemplo: DB saturada), guardar en Redis como buffer temporal
        pedido_data = {
            "cliente": pedido.cliente,
            "producto": pedido.producto,
            "cantidad": pedido.cantidad,
            "fecha": str(datetime.utcnow())
        }
        redis_client.lpush("pedidos_buffer", json.dumps(pedido_data))
        return {"message": "Pedido en buffer temporal"}
