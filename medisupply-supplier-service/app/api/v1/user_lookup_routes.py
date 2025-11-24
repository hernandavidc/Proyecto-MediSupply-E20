from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.vendedor import Vendedor
from app.models.client import Cliente
from app.schemas.vendedor_schema import VendedorResponse
from app.schemas.client_schema import ClienteResponse

router = APIRouter(prefix="/api/v1/users", tags=["User Lookup"])


@router.get("/{user_id}/vendedores", response_model=List[VendedorResponse])
def get_vendedores_by_user(user_id: int, db: Session = Depends(get_db)):
    """Return vendedores associated to the given user_id (vendedor.user_id)."""
    items = db.query(Vendedor).filter(Vendedor.user_id == user_id).all()
    return items


@router.get("/{user_id}/clientes", response_model=List[ClienteResponse])
def get_clientes_by_user(user_id: int, db: Session = Depends(get_db)):
    """Return clientes associated to the given user_id (cliente.user_id)."""
    items = db.query(Cliente).filter(Cliente.user_id == user_id).all()
    return items
