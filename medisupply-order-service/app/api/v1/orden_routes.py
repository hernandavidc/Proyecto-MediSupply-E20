from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.orden_schema import OrdenCreate, OrdenUpdate, OrdenResponse
from app.services.orden_service import OrdenService

router = APIRouter(prefix="/api/v1/ordenes", tags=["Ordenes"])


@router.post("/", response_model=OrdenResponse, status_code=status.HTTP_201_CREATED)
def crear_orden(payload: OrdenCreate, db: Session = Depends(get_db)):
    service = OrdenService(db)
    orden = service.crear_orden(payload)
    return service._orden_to_response(orden)


@router.get("/", response_model=List[OrdenResponse])
def listar_ordenes(
    skip: int = 0, 
    limit: int = 100, 
    estado: str = None,
    id_cliente: int = None,
    db: Session = Depends(get_db)
):
    service = OrdenService(db)
    ordenes = service.listar_ordenes(
        skip=skip, 
        limit=limit, 
        estado=estado, 
        id_cliente=id_cliente
    )
    return [service._orden_to_response(orden) for orden in ordenes]


@router.get("/{orden_id}", response_model=OrdenResponse)
def obtener_orden(orden_id: int, db: Session = Depends(get_db)):
    service = OrdenService(db)
    orden = service.obtener_orden(orden_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return service._orden_to_response(orden)


@router.put("/{orden_id}", response_model=OrdenResponse)
def actualizar_orden(orden_id: int, payload: OrdenUpdate, db: Session = Depends(get_db)):
    service = OrdenService(db)
    try:
        orden = service.actualizar_orden(orden_id, payload)
        if not orden:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        return service._orden_to_response(orden)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{orden_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_orden(orden_id: int, db: Session = Depends(get_db)):
    service = OrdenService(db)
    if not service.eliminar_orden(orden_id):
        raise HTTPException(status_code=404, detail="Orden no encontrada")
