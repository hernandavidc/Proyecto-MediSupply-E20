from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.proveedor_schema import (
    ProveedorCreate,
    ProveedorUpdate,
    ProveedorResponse,
)
from app.services.proveedor_service import ProveedorService

router = APIRouter(prefix="/api/v1/proveedores", tags=["Proveedores"])

@router.get("/", response_model=List[ProveedorResponse])
def list_proveedores(db: Session = Depends(get_db)):
    service = ProveedorService(db)
    return service.listar_proveedores()

@router.post("/", response_model=ProveedorResponse, status_code=status.HTTP_201_CREATED)
def create_proveedor(payload: ProveedorCreate, db: Session = Depends(get_db)):
    service = ProveedorService(db)
    proveedor = service.crear_proveedor(payload.model_dump(), usuario_id=None)
    return proveedor

@router.get("/{proveedor_id}", response_model=ProveedorResponse)
def get_proveedor(proveedor_id: int, db: Session = Depends(get_db)):
    service = ProveedorService(db)
    item = service.obtener_proveedor(proveedor_id)
    if not item:
        raise HTTPException(status_code=404, detail='not found')
    return item

@router.put("/{proveedor_id}", response_model=ProveedorResponse)
def update_proveedor(proveedor_id: int, payload: ProveedorUpdate, db: Session = Depends(get_db)):
    service = ProveedorService(db)
    item = service.obtener_proveedor(proveedor_id)
    if not item:
        raise HTTPException(status_code=404, detail='not found')
    proveedor = service.actualizar_proveedor(item, payload.model_dump(), usuario_id=None)
    return proveedor

@router.delete("/{proveedor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_proveedor(proveedor_id: int, db: Session = Depends(get_db)):
    service = ProveedorService(db)
    item = service.obtener_proveedor(proveedor_id)
    if not item:
        raise HTTPException(status_code=404, detail='not found')
    try:
        service.eliminar_proveedor(item, usuario_id=None)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    return None
