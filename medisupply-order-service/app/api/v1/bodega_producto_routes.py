from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.bodega_producto_schema import BodegaProductoCreate, BodegaProductoUpdate, BodegaProductoResponse
from app.services.bodega_producto_service import BodegaProductoService

router = APIRouter(prefix="/api/v1/bodega-productos", tags=["Bodega Productos"])


@router.post("/", response_model=BodegaProductoResponse, status_code=status.HTTP_201_CREATED)
def crear_bodega_producto(payload: BodegaProductoCreate, db: Session = Depends(get_db)):
    service = BodegaProductoService(db)
    return service.crear_bodega_producto(payload)


@router.get("/", response_model=List[BodegaProductoResponse])
def listar_bodega_productos(
    skip: int = 0, 
    limit: int = 100,
    id_bodega: int = None,
    id_producto: int = None,
    lote: str = None,
    latitud: float = None,
    longitud: float = None,
    db: Session = Depends(get_db)
):
    service = BodegaProductoService(db)
    return service.listar_bodega_productos(
        skip=skip, 
        limit=limit,
        id_bodega=id_bodega,
        id_producto=id_producto,
        lote=lote,
        latitud=latitud,
        longitud=longitud
    )


@router.get("/bodega/{bodega_id}", response_model=List[BodegaProductoResponse])
def listar_productos_por_bodega(bodega_id: int, db: Session = Depends(get_db)):
    service = BodegaProductoService(db)
    return service.listar_por_bodega(bodega_id)


@router.get("/{bodega_id}/{producto_id}/{lote}", response_model=BodegaProductoResponse)
def obtener_bodega_producto(bodega_id: int, producto_id: int, lote: str, db: Session = Depends(get_db)):
    service = BodegaProductoService(db)
    bodega_producto = service.obtener_bodega_producto(bodega_id, producto_id, lote)
    if not bodega_producto:
        raise HTTPException(status_code=404, detail="BodegaProducto no encontrado")
    return bodega_producto


@router.put("/{bodega_id}/{producto_id}/{lote}", response_model=BodegaProductoResponse)
def actualizar_bodega_producto(bodega_id: int, producto_id: int, lote: str, payload: BodegaProductoUpdate, db: Session = Depends(get_db)):
    service = BodegaProductoService(db)
    bodega_producto = service.actualizar_bodega_producto(bodega_id, producto_id, lote, payload)
    if not bodega_producto:
        raise HTTPException(status_code=404, detail="BodegaProducto no encontrado")
    return bodega_producto


@router.delete("/{bodega_id}/{producto_id}/{lote}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_bodega_producto(bodega_id: int, producto_id: int, lote: str, db: Session = Depends(get_db)):
    service = BodegaProductoService(db)
    if not service.eliminar_bodega_producto(bodega_id, producto_id, lote):
        raise HTTPException(status_code=404, detail="BodegaProducto no encontrado")
