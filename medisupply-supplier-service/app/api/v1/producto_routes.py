from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.product_schema import ProductoCreate, ProductoResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/api/v1/productos", tags=["Productos"])

@router.get("/", response_model=List[ProductoResponse])
def list_productos(skip: int=0, limit: int=100, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.listar_productos(skip=skip, limit=limit)

@router.post("/", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
async def create_producto(payload: ProductoCreate, db: Session = Depends(get_db)):
    service = ProductService(db)
    try:
        producto = service.crear_producto(payload.model_dump(), usuario_id=None, origen='MANUAL')
        return producto
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@router.get("/{producto_id}", response_model=ProductoResponse)
def get_producto(producto_id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    item = service.obtener_producto(producto_id)
    if not item:
        raise HTTPException(status_code=404, detail='not found')
    return item
