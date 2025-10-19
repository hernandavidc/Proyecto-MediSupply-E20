from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.vendedor_schema import VendedorCreate, VendedorResponse
from app.services.vendedor_service import VendedorService

router = APIRouter(prefix="/api/v1/vendedores", tags=["Vendedores"])

@router.get("/", response_model=List[VendedorResponse])
def list_vendedores(skip: int=0, limit: int=100, db: Session = Depends(get_db)):
    service = VendedorService(db)
    return service.listar_vendedores(skip=skip, limit=limit)

@router.post("/", response_model=VendedorResponse, status_code=status.HTTP_201_CREATED)
def create_vendedor(payload: VendedorCreate, db: Session = Depends(get_db)):
    service = VendedorService(db)
    try:
        vendedor = service.crear_vendedor(payload.model_dump(), usuario_id=None)
        return vendedor
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@router.get("/{vendedor_id}", response_model=VendedorResponse)
def get_vendedor(vendedor_id: int, db: Session = Depends(get_db)):
    service = VendedorService(db)
    item = service.obtener_vendedor(vendedor_id)
    if not item:
        raise HTTPException(status_code=404, detail='not found')
    return item

@router.delete("/{vendedor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vendedor(vendedor_id: int, db: Session = Depends(get_db)):
    service = VendedorService(db)
    item = service.obtener_vendedor(vendedor_id)
    if not item:
        raise HTTPException(status_code=404, detail='not found')
    try:
        service.eliminar_vendedor(item)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    return None
