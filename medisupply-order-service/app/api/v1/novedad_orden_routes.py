from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.novedad_orden_schema import NovedadOrdenCreate, NovedadOrdenUpdate, NovedadOrdenResponse
from app.services.novedad_orden_service import NovedadOrdenService
from app.models.novedad_orden import TipoNovedad

router = APIRouter(prefix="/api/v1/novedades", tags=["Novedades"])


@router.post("/", response_model=NovedadOrdenResponse, status_code=status.HTTP_201_CREATED)
async def crear_novedad(
    id_pedido: int = Form(...),
    tipo: TipoNovedad = Form(...),
    descripcion: Optional[str] = Form(None),
    fotos: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db)
):
    """
    Crear una nueva novedad con opción de adjuntar fotos.
    
    - **id_pedido**: ID del pedido asociado
    - **tipo**: Tipo de novedad (DEVOLUCION, CANTIDAD_DIFERENTE, MAL_ESTADO, PRODUCTO_NO_COINCIDE)
    - **descripcion**: Descripción opcional de la novedad
    - **fotos**: Lista de archivos de imagen (opcional)
    """
    # Crear el objeto de datos
    novedad_data = NovedadOrdenCreate(
        id_pedido=id_pedido,
        tipo=tipo,
        descripcion=descripcion
    )
    
    service = NovedadOrdenService(db)
    novedad = service.crear_novedad(novedad_data, fotos)
    
    # El validador del schema se encarga de convertir el JSON a lista
    return NovedadOrdenResponse.model_validate(novedad)


@router.get("/", response_model=List[NovedadOrdenResponse])
def listar_novedades(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = NovedadOrdenService(db)
    novedades = service.listar_novedades(skip=skip, limit=limit)
    return [NovedadOrdenResponse.model_validate(n) for n in novedades]


@router.get("/orden/{orden_id}", response_model=List[NovedadOrdenResponse])
def listar_novedades_por_orden(orden_id: int, db: Session = Depends(get_db)):
    service = NovedadOrdenService(db)
    novedades = service.listar_por_orden(orden_id)
    return [NovedadOrdenResponse.model_validate(n) for n in novedades]


@router.get("/{novedad_id}", response_model=NovedadOrdenResponse)
def obtener_novedad(novedad_id: int, db: Session = Depends(get_db)):
    service = NovedadOrdenService(db)
    novedad = service.obtener_novedad(novedad_id)
    if not novedad:
        raise HTTPException(status_code=404, detail="Novedad no encontrada")
    return NovedadOrdenResponse.model_validate(novedad)


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
