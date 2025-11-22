from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.schemas.orden_schema import OrdenResponse
from app.services.orden_service import OrdenService

router = APIRouter(prefix="/internal/v1/ordenes", tags=["Internal"])


@router.get("/", response_model=List[OrdenResponse])
def listar_ordenes_interno(
    skip: int = 0, 
    limit: int = 1000, 
    estado: Optional[str] = None,
    id_cliente: Optional[int] = None,
    id_vendedor: Optional[int] = None,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Endpoint interno para comunicación entre servicios.
    NO requiere autenticación JWT pero SÍ requiere header X-Internal-Service-Key.
    """
    service = OrdenService(db)
    ordenes = service.listar_ordenes(
        skip=skip,
        limit=limit,
        estado=estado,
        id_cliente=id_cliente,
        id_vendedor=id_vendedor,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta
    )
    return [service._orden_to_response(orden) for orden in ordenes]
