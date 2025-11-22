from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.novedad_orden_schema import NovedadOrdenCreate, NovedadOrdenUpdate, NovedadOrdenResponse
from app.services.novedad_orden_service import NovedadOrdenService

router = APIRouter(prefix="/api/v1/novedades", tags=["Novedades"])


@router.post("/", response_model=NovedadOrdenResponse, status_code=status.HTTP_201_CREATED)
def crear_novedad(payload: NovedadOrdenCreate, db: Session = Depends(get_db)):
    service = NovedadOrdenService(db)
    return service.crear_novedad(payload)


@router.get("/", response_model=List[NovedadOrdenResponse])
def listar_novedades(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = NovedadOrdenService(db)
    return service.listar_novedades(skip=skip, limit=limit)


@router.get("/orden/{orden_id}", response_model=List[NovedadOrdenResponse])
def listar_novedades_por_orden(orden_id: int, db: Session = Depends(get_db)):
    service = NovedadOrdenService(db)
    return service.listar_por_orden(orden_id)


@router.get("/{novedad_id}", response_model=NovedadOrdenResponse)
def obtener_novedad(novedad_id: int, db: Session = Depends(get_db)):
    service = NovedadOrdenService(db)
    novedad = service.obtener_novedad(novedad_id)
    if not novedad:
        raise HTTPException(status_code=404, detail="Novedad no encontrada")
    return novedad


@router.put("/{novedad_id}", response_model=NovedadOrdenResponse)
def actualizar_novedad(novedad_id: int, payload: NovedadOrdenUpdate, db: Session = Depends(get_db)):
    service = NovedadOrdenService(db)
    novedad = service.actualizar_novedad(novedad_id, payload)
    if not novedad:
        raise HTTPException(status_code=404, detail="Novedad no encontrada")
    return novedad


@router.delete("/{novedad_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_novedad(novedad_id: int, db: Session = Depends(get_db)):
    service = NovedadOrdenService(db)
    if not service.eliminar_novedad(novedad_id):
        raise HTTPException(status_code=404, detail="Novedad no encontrada")
