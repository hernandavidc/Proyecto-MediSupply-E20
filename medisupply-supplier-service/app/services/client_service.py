from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional, Union
from sqlalchemy.exc import IntegrityError
import uuid
import httpx
from app.core.config import settings
from app.models.client import Cliente
from app.models.vendedor import Vendedor


class ClientService:
    """Service to manage clients.

    Supports listing clients by vendor and creating a client associated
    to a vendor. Creation will create a user in the user-service and
    persist the returned user id in clientes.user_id.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_clients_by_vendor(self, vendedor_id: int, skip: int = 0, limit: int = 100) -> List[Cliente]:
        return (
            self.db.query(Cliente)
            .filter(Cliente.vendedor_id == vendedor_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def crear_cliente(self, vendedor_id: int, data: Dict[str, Any], usuario_id: Optional[int] = None, create_remote_user: bool = False, as_dict: bool = False) -> Union[Cliente, Dict[str, Any]]:
        """Create a client for a given vendedor.

        This method creates a user in user-service with role 'Cliente' and stores
        the returned id in clientes.user_id. Returns the created Cliente or a
        composite dict {cliente, user} containing the credentials (including the fixed password).
        """

        # Ensure vendedor exists (do not change any vendedor logic)
        vendedor = self.db.query(Vendedor).filter(Vendedor.id == vendedor_id).first()
        if not vendedor:
            raise ValueError('Vendedor no encontrado')

        created_user_info = None
        if create_remote_user:
            rnd = uuid.uuid4().hex[:8]
            generated_email = f"cliente_{rnd}@gmail.com"
            password = '12345678'
            user_payload = {
                "name": data.get('institucion_nombre') or 'Cliente',
                "email": generated_email,
                "password": password,
                # Asumimos que el role_id de 'Cliente' es 2 (seeded in user-service)
                "role_id": 2
            }
            try:
                url = f"{settings.USER_SERVICE_URL}/api/v1/users/register"
                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(url, json=user_payload)
                    if resp.status_code not in (200, 201):
                        raise ValueError(f"user-service register failed: {resp.status_code} {resp.text}")
                    created_user_info = resp.json()
            except Exception as e:
                raise ValueError(f"No se pudo crear usuario en user-service: {str(e)}")

        cliente = Cliente(
            vendedor_id=vendedor_id,
            institucion_nombre=data.get('institucion_nombre'),
            direccion=data.get('direccion'),
            contacto_principal=data.get('contacto_principal'),
            user_id=(created_user_info.get('id') if created_user_info else usuario_id),
        )

        try:
            self.db.add(cliente)
            self.db.flush()
            self.db.commit()
            self.db.refresh(cliente)
            if create_remote_user:
                user_out = {
                    "id": created_user_info.get('id') if created_user_info else None,
                    "email": created_user_info.get('email') if created_user_info else generated_email,
                    "password": password,
                }
                return {
                    "cliente": self._to_dict(cliente),
                    "user": user_out
                }
            return self._to_dict(cliente) if as_dict else cliente
        except IntegrityError:
            try:
                self.db.rollback()
            except Exception:
                pass
            raise
        except Exception:
            try:
                self.db.rollback()
            except Exception:
                pass
            raise

    def _to_dict(self, c: Cliente) -> Dict[str, Any]:
        return {
            "id": c.id,
            "vendedor_id": c.vendedor_id,
            "institucion_nombre": c.institucion_nombre,
            "direccion": c.direccion,
            "contacto_principal": c.contacto_principal,
            "user_id": getattr(c, 'user_id', None),
        }
