from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.client import Client
from app.schemas.client_schema import ClientCreate, ClientUpdate, NITValidationResponse
from fastapi import HTTPException, status
from typing import Optional, List, Dict, Any
import httpx
from app.core.config import settings
import logging
import secrets
import string

logger = logging.getLogger(__name__)


class ClientService:
    """
    Service class for client business logic
    """
    
    # Nombre del rol para clientes (más robusto que usar ID hardcodeado)
    CLIENTE_ROLE_NAME = "Cliente"
    # Fallback: ID del rol "Cliente" si no se puede obtener dinámicamente
    CLIENTE_ROLE_ID_FALLBACK = 2
    
    @staticmethod
    async def _get_cliente_role_id() -> int:
        """
        Get the role ID for "Cliente" from user-service dynamically
        
        Returns:
            The role ID for "Cliente" role
            
        Raises:
            HTTPException: If role cannot be retrieved
        """
        try:
            user_service_url = settings.USER_SERVICE_URL
            roles_endpoint = f"{user_service_url}/api/v1/roles"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(roles_endpoint)
                
                if response.status_code == 200:
                    roles = response.json()
                    for role in roles:
                        if role.get("name") == ClientService.CLIENTE_ROLE_NAME:
                            role_id = role.get("id")
                            logger.info(f"Role ID para '{ClientService.CLIENTE_ROLE_NAME}' obtenido dinámicamente: {role_id}")
                            return role_id
                    
                    # Si no se encuentra el rol por nombre, usar fallback
                    logger.warning(
                        f"Rol '{ClientService.CLIENTE_ROLE_NAME}' no encontrado en user-service. "
                        f"Usando fallback ID={ClientService.CLIENTE_ROLE_ID_FALLBACK}"
                    )
                    return ClientService.CLIENTE_ROLE_ID_FALLBACK
                else:
                    logger.warning(
                        f"No se pudo obtener roles desde user-service (status {response.status_code}). "
                        f"Usando fallback ID={ClientService.CLIENTE_ROLE_ID_FALLBACK}"
                    )
                    return ClientService.CLIENTE_ROLE_ID_FALLBACK
                    
        except Exception as e:
            logger.warning(
                f"Error obteniendo role ID desde user-service: {str(e)}. "
                f"Usando fallback ID={ClientService.CLIENTE_ROLE_ID_FALLBACK}"
            )
            return ClientService.CLIENTE_ROLE_ID_FALLBACK
    
    @staticmethod
    def _generate_temporary_password(length: int = 12) -> str:
        """
        Generate a secure temporary password
        
        Args:
            length: Length of the password (default: 12)
            
        Returns:
            A random password with uppercase, lowercase, digits and special chars
        """
        # Asegurar que la contraseña tenga al menos un carácter de cada tipo
        password_chars = [
            secrets.choice(string.ascii_uppercase),  # Al menos una mayúscula
            secrets.choice(string.ascii_lowercase),  # Al menos una minúscula
            secrets.choice(string.digits),           # Al menos un dígito
            secrets.choice("!@#$%^&*()_+-=[]{}|;:,.<>?")  # Al menos un carácter especial
        ]
        
        # Completar el resto de la contraseña
        all_chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
        password_chars.extend(secrets.choice(all_chars) for _ in range(length - 4))
        
        # Mezclar los caracteres
        secrets.SystemRandom().shuffle(password_chars)
        
        return ''.join(password_chars)
    
    @staticmethod
    async def _create_user_in_user_service(
        name: str,
        email: str,
        password: str,
        role_id: int
    ) -> Dict[str, Any]:
        """
        Create a user in the user-service via HTTP request
        
        Args:
            name: User's full name
            email: User's email (will be used as username)
            password: User's password
            role_id: Role ID (default: CLIENTE_ROLE_ID)
            
        Returns:
            Dictionary with user creation response from user-service
            
        Raises:
            HTTPException: If user creation fails
        """
        try:
            user_service_url = settings.USER_SERVICE_URL
            register_endpoint = f"{user_service_url}/api/v1/users/register"
            
            payload = {
                "name": name,
                "email": email,
                "password": password,
                "role_id": role_id
            }
            
            logger.info(f"Creando usuario en user-service: {email}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(register_endpoint, json=payload)
                
                if response.status_code == 201:
                    user_data = response.json()
                    logger.info(f"Usuario creado exitosamente en user-service: ID={user_data.get('id')}, email={email}")
                    return user_data
                elif response.status_code == 400:
                    # El usuario ya existe
                    error_detail = response.json().get("detail", "Error desconocido")
                    logger.warning(f"Error creando usuario: {error_detail}")
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"No se pudo crear el usuario: {error_detail}"
                    )
                else:
                    logger.error(f"Error inesperado del user-service: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="El servicio de usuarios no está disponible temporalmente"
                    )
                    
        except httpx.RequestError as e:
            logger.error(f"Error de conexión con user-service: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"No se pudo conectar con el servicio de usuarios: {str(e)}"
            )
        except HTTPException:
            # Re-raise HTTPExceptions as-is
            raise
        except Exception as e:
            logger.error(f"Error inesperado creando usuario: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno al crear el usuario"
            )
    
    @staticmethod
    async def validate_nit(nit: str) -> NITValidationResponse:
        """
        Validate NIT with external service
        
        This is a mock implementation. In production, this should call
        the actual government/business registry API.
        """
        try:
            # Mock validation - replace with actual API call
            # Example: Colombian DIAN API, Chilean SII API, etc.
            
            if settings.NIT_VALIDATION_SERVICE_URL:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{settings.NIT_VALIDATION_SERVICE_URL}/validate/{nit}",
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        return NITValidationResponse(
                            nit=nit,
                            is_valid=data.get("is_valid", False),
                            company_name=data.get("company_name"),
                            company_status=data.get("status"),
                            message=data.get("message", "NIT validado exitosamente")
                        )
            
            # Respuesta mock para desarrollo
            
            return NITValidationResponse(
                nit=nit,
                is_valid=True,
                company_name=f"Empresa Mock para NIT {nit}",
                company_status="ACTIVO",
                message="Validación mock - Configure NIT_VALIDATION_SERVICE_URL para validación real"
            )
            
        except httpx.RequestError as e:
            logger.error(f"Error validando NIT {nit}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="El servicio de validación de NIT no está disponible temporalmente"
            )
        except Exception as e:
            logger.error(f"Error inesperado validando NIT {nit}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al validar el NIT"
            )
    
    @staticmethod
    async def create_client(db: Session, client_data: ClientCreate) -> Dict[str, Any]:
        """
        Create a new client in the database and create associated user account
        
        Returns:
            Dictionary containing client data, user_id, and temporary_password
        """
        db_client = None
        user_created = False
        user_id = None
        
        try:
            # 1. Verificar si ya existe un cliente con ese NIT
            existing_client = db.query(Client).filter(Client.nit == client_data.nit).first()
            if existing_client:
                logger.warning(f"Intento de crear cliente duplicado con NIT: {client_data.nit}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Cliente con NIT {client_data.nit} ya existe"
                )
            
            # 2. Obtener ID del rol "Cliente" dinámicamente
            cliente_role_id = await ClientService._get_cliente_role_id()
            
            # 3. Generar contraseña temporal
            temporary_password = ClientService._generate_temporary_password()
            logger.info(f"Contraseña temporal generada para {client_data.email_contacto}")
            
            # 4. Crear usuario en user-service
            try:
                user_response = await ClientService._create_user_in_user_service(
                    name=client_data.nombre_contacto,
                    email=client_data.email_contacto,
                    password=temporary_password,
                    role_id=cliente_role_id
                )
                user_created = True
                user_id = user_response.get("id")
                logger.info(f"Usuario creado en user-service: user_id={user_id}")
            except HTTPException as e:
                # Si falla la creación del usuario, no crear el cliente
                logger.error(f"No se pudo crear usuario: {e.detail}")
                raise
            
            # 5. Crear cliente en la base de datos
            db_client = Client(
                nombre=client_data.nombre,
                nit=client_data.nit,
                direccion=client_data.direccion,
                nombre_contacto=client_data.nombre_contacto,
                telefono_contacto=client_data.telefono_contacto,
                email_contacto=client_data.email_contacto,
                is_validated=False  # Will be validated separately
            )
            
            db.add(db_client)
            db.commit()
            db.refresh(db_client)
            
            logger.info(f"Cliente creado exitosamente: {db_client.id}, user_id={user_id}")
            
            # 6. Retornar información completa incluyendo la contraseña temporal
            return {
                "client": db_client,
                "user_id": user_id,
                "temporary_password": temporary_password,
                "login_instructions": (
                    f"El usuario '{client_data.email_contacto}' ha sido creado. "
                    f"Utilice el email y la contraseña temporal proporcionada para iniciar sesión. "
                    f"Se recomienda cambiar la contraseña en el primer inicio de sesión."
                )
            }
            
        except IntegrityError:
            db.rollback()
            logger.warning(f"Intento de crear cliente duplicado con NIT: {client_data.nit}")
            
            # NOTA: En caso de fallo después de crear usuario, quedaría un usuario huérfano
            # Mejora futura: Implementar patrón Saga o endpoint de rollback en user-service
            if user_created:
                logger.warning(f"Usuario creado pero cliente falló. Usuario huérfano: user_id={user_id}")
            
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cliente con NIT {client_data.nit} ya existe"
            )
        except HTTPException:
            # Re-raise HTTPExceptions (incluye errores de user-service)
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error creando cliente: {str(e)}")
            
            if user_created:
                logger.warning(f"Usuario creado pero cliente falló. Usuario huérfano: user_id={user_id}")
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al crear el cliente"
            )
    
    @staticmethod
    def get_client_by_id(db: Session, client_id: str) -> Optional[Client]:
        """
        Get client by ID
        """
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cliente con ID {client_id} no encontrado"
            )
        return client
    
    @staticmethod
    def get_client_by_nit(db: Session, nit: str) -> Optional[Client]:
        """
        Get client by NIT
        """
        return db.query(Client).filter(Client.nit == nit).first()
    
    @staticmethod
    def get_clients(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Client], int]:
        """
        Get paginated list of clients
        """
        total = db.query(Client).count()
        clients = db.query(Client).offset(skip).limit(limit).all()
        return clients, total
    
    @staticmethod
    def update_client(
        db: Session,
        client_id: str,
        client_data: ClientUpdate
    ) -> Client:
        """
        Update client information
        """
        client = ClientService.get_client_by_id(db, client_id)
        
        # Update only provided fields
        update_data = client_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(client, field, value)
        
        try:
            db.commit()
            db.refresh(client)
            logger.info(f"Cliente actualizado exitosamente: {client_id}")
            return client
        except Exception as e:
            db.rollback()
            logger.error(f"Error actualizando cliente {client_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar el cliente"
            )
    
    @staticmethod
    def delete_client(db: Session, client_id: str) -> dict:
        """
        Delete client (soft delete by marking as inactive could be implemented)
        """
        client = ClientService.get_client_by_id(db, client_id)
        
        try:
            db.delete(client)
            db.commit()
            logger.info(f"Cliente eliminado exitosamente: {client_id}")
            return {"message": f"Cliente {client_id} eliminado exitosamente"}
        except Exception as e:
            db.rollback()
            logger.error(f"Error eliminando cliente {client_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar el cliente"
            )
    
    @staticmethod
    def mark_as_validated(db: Session, client_id: str) -> Client:
        """
        Mark client as validated after successful NIT verification
        """
        client = ClientService.get_client_by_id(db, client_id)
        client.is_validated = True
        
        try:
            db.commit()
            db.refresh(client)
            logger.info(f"Cliente marcado como validado: {client_id}")
            return client
        except Exception as e:
            db.rollback()
            logger.error(f"Error validando cliente {client_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al validar el cliente"
            )

