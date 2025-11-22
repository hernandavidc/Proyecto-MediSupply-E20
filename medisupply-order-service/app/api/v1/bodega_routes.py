from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.bodega_schema import BodegaCreate, BodegaUpdate, BodegaResponse
from app.services.bodega_service import BodegaService

router = APIRouter(prefix="/api/v1/bodegas", tags=["Bodegas"])


@router.post("/", response_model=BodegaResponse, status_code=status.HTTP_201_CREATED)
def crear_bodega(payload: BodegaCreate, db: Session = Depends(get_db)):
    service = BodegaService(db)
    return service.crear_bodega(payload)


@router.get("/", response_model=List[BodegaResponse])
def listar_bodegas(
    skip: int = 0, 
    limit: int = 100, 
    id_pais: int = None,
    id_producto: int = None,
    db: Session = Depends(get_db)
):
    service = BodegaService(db)
    return service.listar_bodegas(skip=skip, limit=limit, id_pais=id_pais, id_producto=id_producto)


@router.get("/{bodega_id}", response_model=BodegaResponse)
def obtener_bodega(bodega_id: int, db: Session = Depends(get_db)):
    service = BodegaService(db)
    bodega = service.obtener_bodega(bodega_id)
    if not bodega:
        raise HTTPException(status_code=404, detail="Bodega no encontrada")
    return bodega


@router.put("/{bodega_id}", response_model=BodegaResponse)
def actualizar_bodega(bodega_id: int, payload: BodegaUpdate, db: Session = Depends(get_db)):
    service = BodegaService(db)
    bodega = service.actualizar_bodega(bodega_id, payload)
    if not bodega:
        raise HTTPException(status_code=404, detail="Bodega no encontrada")
    return bodega


@router.delete("/{bodega_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_bodega(bodega_id: int, db: Session = Depends(get_db)):
    service = BodegaService(db)
    if not service.eliminar_bodega(bodega_id):
        raise HTTPException(status_code=404, detail="Bodega no encontrada")
