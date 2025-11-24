from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user_email
from app.schemas.client_schema import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientCreatedResponse,
    NITValidationResponse,
    ClientListResponse
)
from app.services.client_service import ClientService
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/clientes",
    tags=["Clientes"]
)


@router.post(
    "",
    response_model=ClientCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo cliente institucional",
    description="""
    Registrar un nuevo cliente institucional con validación automática de NIT 
    y creación automática de cuenta de usuario.
    
    **Historia de Usuario**: MSCM-HU-CL-001-MOV - Registrar Cliente Institucional
    
    Este endpoint permite que los futuros clientes de MediSupply se registren rápidamente
    con validación automática, para que puedan comenzar a usar los productos ofrecidos
    por la empresa como proveedor de productos médicos.
    
    **Autenticación**: Este endpoint requiere un token JWT válido en el header Authorization.
    
    **Campos requeridos**:
    - nombre: Nombre de la empresa
    - nit: Número de identificación tributaria (NIT)
    - direccion: Dirección de la empresa
    - nombre_contacto: Nombre de la persona de contacto
    - telefono_contacto: Número de teléfono de contacto
    - email_contacto: Dirección de correo electrónico de contacto
    
    **Proceso automatizado**:
    1. Se valida el NIT contra el registro nacional de empresas
    2. Se crea el registro del cliente en la base de datos
    3. Se crea automáticamente una cuenta de usuario con rol "Cliente"
    4. Se genera una contraseña temporal segura
    
    **IMPORTANTE**: La contraseña temporal solo se muestra en esta respuesta.
    Guarde esta información para proporcionársela al cliente.
    
    El cliente podrá iniciar sesión usando:
    - **Usuario**: El email_contacto proporcionado
    - **Contraseña**: La contraseña temporal devuelta en el response
    """
)
async def register_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_user_email)
):
    """
    Registrar un nuevo cliente institucional y crear su cuenta de usuario
    
    Requiere autenticación mediante token JWT. El parámetro user_email se extrae
    automáticamente del token JWT válido en el header Authorization.
    
    Returns:
        ClientCreatedResponse con información del cliente, user_id, y contraseña temporal
    """
    # Registrar quién está registrando el cliente (para auditoría)
    logger.info(f"Usuario {user_email} está registrando un nuevo cliente con NIT: {client_data.nit}")
    
    # Primero, validar el NIT
    nit_validation = await ClientService.validate_nit(client_data.nit)
    
    # Crear el cliente y su usuario asociado
    creation_result = await ClientService.create_client(db, client_data)
    
    client = creation_result["client"]
    
    # Si el NIT es válido, marcar cliente como validado
    if nit_validation.is_valid:
        client = ClientService.mark_as_validated(db, client.id)
    
    # Construir la respuesta completa
    return ClientCreatedResponse(
        # Datos del cliente
        id=client.id,
        nombre=client.nombre,
        nit=client.nit,
        direccion=client.direccion,
        nombre_contacto=client.nombre_contacto,
        telefono_contacto=client.telefono_contacto,
        email_contacto=client.email_contacto,
        is_validated=client.is_validated,
        created_at=client.created_at,
        updated_at=client.updated_at,
        # Información de usuario y credenciales
        user_id=creation_result["user_id"],
        temporary_password=creation_result["temporary_password"],
        login_instructions=creation_result["login_instructions"]
    )


@router.get(
    "/validate-nit/{nit}",
    response_model=NITValidationResponse,
    summary="Validar NIT y obtener información de la empresa",
    description="""
    Validar un número de identificación tributaria (NIT) y recuperar información
    de la empresa desde el registro nacional de empresas.
    
    Este endpoint se utiliza para validación automática cuando un cliente ingresa
    su NIT durante el proceso de registro.
    
    **Retorna**:
    - is_valid: Si el NIT es válido y está registrado
    - company_name: Nombre oficial de la empresa desde el registro
    - company_status: Estado actual de la empresa (ACTIVO, INACTIVO, etc.)
    - message: Mensaje de resultado de la validación
    """
)
async def validate_nit(nit: str):
    """
    Validar NIT y obtener información de la empresa
    """
    return await ClientService.validate_nit(nit)


@router.get(
    "",
    response_model=ClientListResponse,
    summary="Listar todos los clientes",
    description="Obtener una lista paginada de todos los clientes registrados"
)
def get_clients(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=100, description="Elementos por página"),
    db: Session = Depends(get_db)
):
    """
    Obtener lista paginada de clientes
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
    summary="Obtener cliente por ID",
    description="Recuperar información detallada sobre un cliente específico"
)
def get_client(client_id: str, db: Session = Depends(get_db)):
    """
    Obtener cliente por ID
    """
    return ClientService.get_client_by_id(db, client_id)


@router.get(
    "/by-nit/{nit}",
    response_model=ClientResponse,
    summary="Obtener cliente por NIT",
    description="Recuperar información del cliente usando su número de identificación tributaria (NIT)"
)
def get_client_by_nit(nit: str, db: Session = Depends(get_db)):
    """
    Obtener cliente por NIT
    """
    client = ClientService.get_client_by_nit(db, nit)
    if not client:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente con NIT {nit} no encontrado"
        )
    return client


@router.put(
    "/{client_id}",
    response_model=ClientResponse,
    summary="Actualizar información del cliente",
    description="Actualizar detalles del cliente. Todos los campos son opcionales. Requiere autenticación."
)
def update_client(
    client_id: str,
    client_data: ClientUpdate,
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_user_email)
):
    """
    Actualizar información del cliente
    
    Requiere autenticación mediante token JWT.
    """
    logger.info(f"Usuario {user_email} está actualizando cliente: {client_id}")
    return ClientService.update_client(db, client_id, client_data)


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar cliente",
    description="Eliminar un cliente del sistema. Requiere autenticación."
)
def delete_client(
    client_id: str, 
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_user_email)
):
    """
    Eliminar cliente
    
    Requiere autenticación mediante token JWT.
    """
    logger.info(f"Usuario {user_email} está eliminando cliente: {client_id}")
    ClientService.delete_client(db, client_id)
    return None


@router.post(
    "/{client_id}/validate",
    response_model=ClientResponse,
    summary="Marcar cliente como validado",
    description="Marcar manualmente un cliente como validado después de una verificación exitosa. Requiere autenticación."
)
def validate_client(
    client_id: str, 
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_user_email)
):
    """
    Marcar cliente como validado
    
    Requiere autenticación mediante token JWT.
    """
    logger.info(f"Usuario {user_email} está validando cliente: {client_id}")
    return ClientService.mark_as_validated(db, client_id)

