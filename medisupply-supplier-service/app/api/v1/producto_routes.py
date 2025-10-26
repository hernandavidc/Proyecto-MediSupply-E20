from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.product_schema import ProductoCreate, ProductoResponse, ResultadoCargaMasiva, ConfiguracionCarga
from app.services.product_service import ProductService
from app.services.csv_processor import CSVProcessor

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

@router.post("/carga-masiva", response_model=ResultadoCargaMasiva, status_code=status.HTTP_201_CREATED)
async def carga_masiva_productos(
    archivo: UploadFile = File(..., description="Archivo CSV con productos"),
    rechazar_lote_ante_errores: bool = Form(True, description="Rechazar todo el lote si hay errores"),
    db: Session = Depends(get_db)
):
    """
    Carga masiva de productos desde archivo CSV.
    
    El archivo debe estar en formato CSV con separador pipeline (|) y contener las siguientes columnas:
    - sku: Identificador único del producto
    - nombre_producto: Nombre del producto
    - proveedor_id: ID del proveedor
    - ficha_tecnica_url: URL opcional de la ficha técnica
    - ca_temp, ca_humedad, ca_luz, ca_ventilacion, ca_seguridad, ca_envase: Condiciones de almacenamiento
    - org_tipo_medicamento, org_fecha_vencimiento: Datos de organización
    - valor_unitario_usd: Precio en USD
    - certificaciones_sanitarias: Lista de IDs separados por punto y coma (;)
    """
    # Validar tipo de archivo
    if not archivo.filename.lower().endswith('.csv'):
        raise HTTPException(
            status_code=400, 
            detail="El archivo debe ser de tipo CSV"
        )
    
    try:
        # Leer contenido del archivo
        contenido = await archivo.read()
        
        # Procesar archivo
        processor = CSVProcessor(db)
        resultado = processor.procesar_archivo(contenido, rechazar_lote_ante_errores)
        
        # Si hay errores y se debe rechazar el lote, devolver error
        if rechazar_lote_ante_errores and resultado.errores:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "El lote fue rechazado debido a errores de validación",
                    "errores": [error.model_dump() for error in resultado.errores],
                    "estadisticas": {
                        "total_lineas": resultado.total_lineas,
                        "exitosas": resultado.exitosas,
                        "fallidas": resultado.fallidas
                    }
                }
            )
        
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al procesar el archivo: {str(e)}"
        )
