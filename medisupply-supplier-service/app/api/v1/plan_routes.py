from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.plan_schema import PlanCreate, PlanResponse
from app.services.plan_service import PlanService

router = APIRouter(prefix="/api/v1/planes-venta", tags=["PlanesVenta"])

@router.get("/", response_model=List[PlanResponse])
def list_planes(skip: int=0, limit: int=100, db: Session = Depends(get_db)):
    service = PlanService(db)
    return service.listar_planes(skip=skip, limit=limit)

@router.post("/", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(payload: PlanCreate, db: Session = Depends(get_db)):
    service = PlanService(db)
    try:
        plan = service.crear_plan(payload.model_dump(), usuario_id=None)
        return plan
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    service = PlanService(db)
    item = service.obtener_plan(plan_id)
    if not item:
        raise HTTPException(status_code=404, detail='not found')
    return item

@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    service = PlanService(db)
    item = service.obtener_plan(plan_id)
    if not item:
        raise HTTPException(status_code=404, detail='not found')
    try:
        service.eliminar_plan(item)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    return None
