from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user_email
from app.schemas.client_schema import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    NITValidationResponse,
    ClientListResponse
)
from app.services.client_service import ClientService
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/clientes",
    tags=["Clients"]
)


@router.post(
    "",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new institutional client",
    description="""
    Register a new institutional client with automatic NIT validation.
    
    **User Story**: MSCM-HU-CL-001-MOV - Register Institutional Client
    
    This endpoint allows future MediSupply clients to register quickly with automatic validation,
    so they can start using the products offered by the company as a medical products provider.
    
    **Authentication**: This endpoint requires a valid JWT token in the Authorization header.
    
    **Required fields**:
    - nombre: Company name
    - nit: Tax identification number (NIT)
    - direccion: Company address
    - nombre_contacto: Contact person name
    - telefono_contacto: Contact phone number
    - email_contacto: Contact email address
    
    **Automatic validation**:
    - The NIT is validated against the national business registry
    - Company existence is verified automatically
    """
)
async def register_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_user_email)
):
    """
    Register a new institutional client
    
    Requires authentication via JWT token. The user_email parameter is automatically
    extracted from the valid JWT token in the Authorization header.
    """
    # Log who is registering the client (for audit purposes)
    logger.info(f"User {user_email} is registering a new client with NIT: {client_data.nit}")
    
    # First, validate the NIT
    nit_validation = await ClientService.validate_nit(client_data.nit)
    
    # Create the client
    client = ClientService.create_client(db, client_data)
    
    # If NIT is valid, mark client as validated
    if nit_validation.is_valid:
        client = ClientService.mark_as_validated(db, client.id)
    
    return client


@router.get(
    "/validate-nit/{nit}",
    response_model=NITValidationResponse,
    summary="Validate NIT and get company information",
    description="""
    Validate a tax identification number (NIT) and retrieve company information
    from the national business registry.
    
    This endpoint is used for automatic validation when a client enters their NIT
    during the registration process.
    
    **Returns**:
    - is_valid: Whether the NIT is valid and registered
    - company_name: Official company name from registry
    - company_status: Current status of the company (ACTIVE, INACTIVE, etc.)
    - message: Validation result message
    """
)
async def validate_nit(nit: str):
    """
    Validate NIT and get company information
    """
    return await ClientService.validate_nit(nit)


@router.get(
    "",
    response_model=ClientListResponse,
    summary="List all clients",
    description="Get a paginated list of all registered clients"
)
def get_clients(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of clients
    """
    skip = (page - 1) * page_size
    clients, total = ClientService.get_clients(db, skip=skip, limit=page_size)
    
    return ClientListResponse(
        total=total,
        page=page,
        page_size=page_size,
        clients=clients
    )


@router.get(
    "/{client_id}",
    response_model=ClientResponse,
    summary="Get client by ID",
    description="Retrieve detailed information about a specific client"
)
def get_client(client_id: str, db: Session = Depends(get_db)):
    """
    Get client by ID
    """
    return ClientService.get_client_by_id(db, client_id)


@router.get(
    "/by-nit/{nit}",
    response_model=ClientResponse,
    summary="Get client by NIT",
    description="Retrieve client information using their tax identification number (NIT)"
)
def get_client_by_nit(nit: str, db: Session = Depends(get_db)):
    """
    Get client by NIT
    """
    client = ClientService.get_client_by_nit(db, nit)
    if not client:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with NIT {nit} not found"
        )
    return client


@router.put(
    "/{client_id}",
    response_model=ClientResponse,
    summary="Update client information",
    description="Update client details. All fields are optional. Requires authentication."
)
def update_client(
    client_id: str,
    client_data: ClientUpdate,
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_user_email)
):
    """
    Update client information
    
    Requires authentication via JWT token.
    """
    logger.info(f"User {user_email} is updating client: {client_id}")
    return ClientService.update_client(db, client_id, client_data)


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete client",
    description="Delete a client from the system. Requires authentication."
)
def delete_client(
    client_id: str, 
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_user_email)
):
    """
    Delete client
    
    Requires authentication via JWT token.
    """
    logger.info(f"User {user_email} is deleting client: {client_id}")
    ClientService.delete_client(db, client_id)
    return None


@router.post(
    "/{client_id}/validate",
    response_model=ClientResponse,
    summary="Mark client as validated",
    description="Manually mark a client as validated after successful verification. Requires authentication."
)
def validate_client(
    client_id: str, 
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_user_email)
):
    """
    Mark client as validated
    
    Requires authentication via JWT token.
    """
    logger.info(f"User {user_email} is validating client: {client_id}")
    return ClientService.mark_as_validated(db, client_id)

