"""
Provider API Routes
Implements REST endpoints according to HU-001
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.services.proveedor_service import ProveedorService
from app.schemas.proveedor_schema import (
    ProveedorCreate, ProveedorUpdate, ProveedorResponse, 
    ProveedorList, ProveedorAuditoriaResponse, ErrorResponse
)
from app.core.enums import EstadoProveedor

router = APIRouter(prefix="/api/v1/providers", tags=["Providers"])

# Constants
PROVIDER_NOT_FOUND = "Provider not found"


def get_provider_service(db: Session = Depends(get_db)) -> ProveedorService:
    """Dependency to get provider service"""
    return ProveedorService(db)


def get_client_ip(request: Request) -> str:
    """Obtener IP del cliente"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """Obtener User-Agent del cliente"""
    return request.headers.get("User-Agent", "unknown")


@router.post(
    "/",
    response_model=ProveedorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new provider",
    description="Register a new provider with validations according to HU-001"
)
async def create_provider(
    provider_data: ProveedorCreate,
    request: Request,
    service: ProveedorService = Depends(get_provider_service),
    current_user = Depends(get_current_active_user)
):
    """Create a new provider"""
    try:
        new_provider = service.crear_proveedor(
            proveedor_data=provider_data,
            usuario_id=current_user.id,
            ip_usuario=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        return new_provider
    
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Validation error",
                "field_errors": e.errors()
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/",
    response_model=List[ProveedorList],
    summary="List providers",
    description="Get list of providers with optional filters"
)
async def list_providers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Record limit"),
    estado: Optional[EstadoProveedor] = Query(None, description="Filter by status"),
    pais: Optional[str] = Query(None, description="Filter by operation country"),
    service: ProveedorService = Depends(get_provider_service),
    current_user = Depends(get_current_active_user)
):
    """List providers with pagination and filters"""
    try:
        providers = service.listar_proveedores(
            skip=skip,
            limit=limit,
            estado=estado,
            pais=pais
        )
        return providers
    
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting providers"
        )


@router.get(
    "/{provider_id}",
    response_model=ProveedorResponse,
    summary="Get provider by ID",
    description="Get complete details of a provider"
)
async def get_provider(
    provider_id: int,
    service: ProveedorService = Depends(get_provider_service),
    current_user = Depends(get_current_active_user)
):
    """Get specific provider"""
    provider = service.obtener_proveedor(provider_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=PROVIDER_NOT_FOUND
        )
    return provider


@router.put(
    "/{provider_id}",
    response_model=ProveedorResponse,
    summary="Update provider",
    description="Update an existing provider with change auditing"
)
async def update_provider(
    provider_id: int,
    provider_data: ProveedorUpdate,
    request: Request,
    service: ProveedorService = Depends(get_provider_service),
    current_user = Depends(get_current_active_user)
):
    """Update existing provider"""
    try:
        updated_provider = service.actualizar_proveedor(
            proveedor_id=provider_id,
            proveedor_data=provider_data,
            usuario_id=current_user.id,
            ip_usuario=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        if not updated_provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=PROVIDER_NOT_FOUND
            )
        
        return updated_provider
    
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Error de validación",
                "field_errors": e.errors()
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.delete(
    "/{provider_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete provider",
    description="Delete a provider (only if no active products)"
)
async def delete_provider(
    provider_id: int,
    request: Request,
    service: ProveedorService = Depends(get_provider_service),
    current_user = Depends(get_current_active_user)
):
    """Delete provider"""
    try:
        deleted = service.eliminar_proveedor(
            proveedor_id=provider_id,
            usuario_id=current_user.id,
            ip_usuario=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=PROVIDER_NOT_FOUND
            )
    
    except ValueError as e:
        if "catálogo activo" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Provider with active catalog"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/{provider_id}/audit",
    response_model=List[ProveedorAuditoriaResponse],
    summary="Get provider audit history",
    description="Get complete change history of a provider"
)
async def get_provider_audit(
    provider_id: int,
    service: ProveedorService = Depends(get_provider_service),
    current_user = Depends(get_current_active_user)
):
    """Get audit history"""
    try:
        # Verify provider exists
        provider = service.obtener_proveedor(provider_id)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Provider not found"
            )
        
        audit = service.obtener_auditoria_proveedor(provider_id)
        return audit
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting audit history"
        )