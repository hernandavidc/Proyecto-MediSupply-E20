from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.product_schema import ProductoCreate, ProductoResponse, ProductoBulkResponse
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

@router.post("/bulk-upload", response_model=ProductoBulkResponse, status_code=status.HTTP_201_CREATED)
async def bulk_upload_productos(
    file: UploadFile = File(...),
    reject_on_errors: bool = Form(True),
    db: Session = Depends(get_db)
):
    """
    Carga masiva de productos desde archivo CSV.
    
    El archivo debe estar en formato CSV con separador pipeline (|) y contener las columnas:
    sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias
    """
    service = ProductService(db)
    
    # Validar tipo de archivo
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400, 
            detail="El archivo debe ser de tipo CSV"
        )
    
    try:
        # Leer contenido del archivo
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Procesar carga masiva
        result = service.procesar_carga_masiva(
            csv_content=csv_content,
            reject_on_errors=reject_on_errors
        )
        
        return result
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {str(e)}")

@router.get("/{producto_id}", response_model=ProductoResponse)
def get_producto(producto_id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    item = service.obtener_producto(producto_id)
    if not item:
        raise HTTPException(status_code=404, detail='not found')
    return item
