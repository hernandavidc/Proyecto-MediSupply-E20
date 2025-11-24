from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import require_roles, get_current_user
from app.schemas.vendedor_schema import VendedorCreate, VendedorResponse, VendedorCreateResponse
from app.services.vendedor_service import VendedorService
from app.services.client_service import ClientService
from app.schemas.client_schema import ClienteResponse
from app.schemas.client_schema import ClienteCreate, ClienteCreateResponse

# Router requires the 'Vendedor' role (resolved dynamically from the current user payload)
router = APIRouter(prefix="/api/v1/vendedores", tags=["Vendedores"], dependencies=[Depends(require_roles('Vendedor'))])

@router.get("/", response_model=List[VendedorResponse])
def list_vendedores(skip: int=0, limit: int=100, db: Session = Depends(get_db)):
    service = VendedorService(db)
    return service.listar_vendedores(skip=skip, limit=limit)

@router.post("/", response_model=VendedorCreateResponse, status_code=status.HTTP_201_CREATED)
def create_vendedor(payload: VendedorCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    service = VendedorService(db)
    try:
        usuario_id = current_user.get('id') if isinstance(current_user, dict) else None
        # Solo crear el usuario remoto cuando la petición viene con un usuario
        # autenticado (i.e. current_user es un dict). Esto mantiene compatibilidad
        # con tests que llaman a la función directamente (no inyectan dependencias).
        create_remote = isinstance(current_user, dict)
        result = service.crear_vendedor(payload.model_dump(), usuario_id=usuario_id, create_remote_user=create_remote)
        # result is a dict: {"vendedor": {...}, "user": {...}} when create_remote True
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@router.get("/{vendedor_id}", response_model=VendedorResponse)
def get_vendedor(vendedor_id: int, db: Session = Depends(get_db)):
    service = VendedorService(db)
    item = service.obtener_vendedor(vendedor_id)
    if not item:
        raise HTTPException(status_code=404, detail='not found')
    return item


@router.get("/{vendedor_id}/clientes", response_model=List[ClienteResponse])
def get_clientes_por_vendedor(vendedor_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Consultar clientes asignados a un vendedor.

    Note: clients are seeded (read-only). There is no API to create/edit clients.
    """
    service = ClientService(db)
    items = service.get_clients_by_vendor(vendedor_id=vendedor_id, skip=skip, limit=limit)
    return items


@router.post("/{vendedor_id}/clientes", response_model=ClienteCreateResponse, status_code=status.HTTP_201_CREATED)
def create_cliente_for_vendedor(vendedor_id: int, payload: ClienteCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Crear un cliente asignado a un vendedor.

    Al crear, se genera también un usuario en el microservicio de usuarios con el rol 'Cliente'.
    El id retornado por user-service se guarda en `clientes.user_id`. Se devuelve el cliente
    creado y las credenciales (email y contraseña fija `12345678`).
    """
    service = ClientService(db)
    try:
        usuario_id = current_user.get('id') if isinstance(current_user, dict) else None
        create_remote = isinstance(current_user, dict)
        result = service.crear_cliente(vendedor_id=vendedor_id, data=payload.model_dump(), usuario_id=usuario_id, create_remote_user=create_remote)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@router.delete("/{vendedor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vendedor(vendedor_id: int, db: Session = Depends(get_db)):
    service = VendedorService(db)
    item = service.obtener_vendedor(vendedor_id)
    if not item:
        raise HTTPException(status_code=404, detail='not found')
    try:
        service.eliminar_vendedor(item)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    return None
