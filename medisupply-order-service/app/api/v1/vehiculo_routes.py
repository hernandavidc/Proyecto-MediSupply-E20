from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.vehiculo_schema import VehiculoCreate, VehiculoUpdate, VehiculoResponse
from app.services.vehiculo_service import VehiculoService

router = APIRouter(prefix="/api/v1/vehiculos", tags=["Vehiculos"])


@router.post("/", response_model=VehiculoResponse, status_code=status.HTTP_201_CREATED)
def crear_vehiculo(payload: VehiculoCreate, db: Session = Depends(get_db)):
    service = VehiculoService(db)
    try:
        return service.crear_vehiculo(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[VehiculoResponse])
def listar_vehiculos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = VehiculoService(db)
    return service.listar_vehiculos(skip=skip, limit=limit)


@router.get("/{vehiculo_id}", response_model=VehiculoResponse)
def obtener_vehiculo(vehiculo_id: int, db: Session = Depends(get_db)):
    service = VehiculoService(db)
    vehiculo = service.obtener_vehiculo(vehiculo_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehiculo no encontrado")
    return vehiculo


@router.put("/{vehiculo_id}", response_model=VehiculoResponse)
def actualizar_vehiculo(vehiculo_id: int, payload: VehiculoUpdate, db: Session = Depends(get_db)):
    service = VehiculoService(db)
    try:
        vehiculo = service.actualizar_vehiculo(vehiculo_id, payload)
        if not vehiculo:
            raise HTTPException(status_code=404, detail="Vehiculo no encontrado")
        return vehiculo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{vehiculo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_vehiculo(vehiculo_id: int, db: Session = Depends(get_db)):
    service = VehiculoService(db)
    if not service.eliminar_vehiculo(vehiculo_id):
        raise HTTPException(status_code=404, detail="Vehiculo no encontrado")
