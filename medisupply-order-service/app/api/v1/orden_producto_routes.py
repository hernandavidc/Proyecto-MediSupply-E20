from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.schemas.orden_producto_schema import OrdenProductoCreate, OrdenProductoUpdate, OrdenProductoResponse
from app.services.orden_producto_service import OrdenProductoService

router = APIRouter(prefix="/api/v1/orden-productos", tags=["Orden Productos"])


@router.post("/", response_model=OrdenProductoResponse, status_code=status.HTTP_201_CREATED)
def crear_orden_producto(payload: OrdenProductoCreate, db: Session = Depends(get_db)):
    service = OrdenProductoService(db)
    return service.crear_orden_producto(payload)


@router.get("/", response_model=List[OrdenProductoResponse])
def listar_orden_productos(
    skip: int = 0, 
    limit: int = 100, 
    id_vendedor: Optional[int] = None,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    service = OrdenProductoService(db)
    return service.listar_orden_productos(
        skip=skip, 
        limit=limit, 
        id_vendedor=id_vendedor,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta
    )


@router.get("/orden/{orden_id}", response_model=List[OrdenProductoResponse])
def listar_productos_por_orden(orden_id: int, db: Session = Depends(get_db)):
    service = OrdenProductoService(db)
    return service.listar_por_orden(orden_id)


@router.get("/{orden_id}/{producto_id}", response_model=OrdenProductoResponse)
def obtener_orden_producto(orden_id: int, producto_id: int, db: Session = Depends(get_db)):
    service = OrdenProductoService(db)
    orden_producto = service.obtener_orden_producto(orden_id, producto_id)
    if not orden_producto:
        raise HTTPException(status_code=404, detail="OrdenProducto no encontrado")
    return orden_producto


@router.put("/{orden_id}/{producto_id}", response_model=OrdenProductoResponse)
def actualizar_orden_producto(orden_id: int, producto_id: int, payload: OrdenProductoUpdate, db: Session = Depends(get_db)):
    service = OrdenProductoService(db)
    orden_producto = service.actualizar_orden_producto(orden_id, producto_id, payload)
    if not orden_producto:
        raise HTTPException(status_code=404, detail="OrdenProducto no encontrado")
    return orden_producto


@router.delete("/{orden_id}/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_orden_producto(orden_id: int, producto_id: int, db: Session = Depends(get_db)):
    service = OrdenProductoService(db)
    if not service.eliminar_orden_producto(orden_id, producto_id):
        raise HTTPException(status_code=404, detail="OrdenProducto no encontrado")
