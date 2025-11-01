from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.client import Client
from app.schemas.client_schema import ClientCreate, ClientUpdate, NITValidationResponse
from fastapi import HTTPException, status
from typing import Optional, List
import httpx
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class ClientService:
    """
    Service class for client business logic
    """
    
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
    def create_client(db: Session, client_data: ClientCreate) -> Client:
        """
        Create a new client in the database
        """
        try:
            # Create client instance
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
            
            logger.info(f"Cliente creado exitosamente: {db_client.id}")
            return db_client
            
        except IntegrityError:
            db.rollback()
            logger.warning(f"Intento de crear cliente duplicado con NIT: {client_data.nit}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cliente con NIT {client_data.nit} ya existe"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Error creando cliente: {str(e)}")
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

