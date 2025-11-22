from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import verify_token
from app.services.user_service import UserService
from app.models.user import User

from typing import List


def require_roles(*allowed_roles: List[str]):
    """Factory dependency: returns a dependency that verifies the current user's role.

    Usage in routes:
        @router.get("/admin-only", dependencies=[Depends(require_roles('Admin'))])
    """
    def _dep(current_user: User = Depends(get_current_active_user)) -> User:
        role_name = getattr(current_user.role, 'name', None)
        if role_name is None or role_name not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para acceder a este recurso")
        return current_user

    return _dep

# Actualizado para que funcione con el endpoint /oauth2/login para Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/users/token")

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Obtener instancia del servicio de usuarios"""
    return UserService(db)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """Obtener el usuario actual desde el token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    email = verify_token(token)
    if email is None:
        raise credentials_exception
    
    user = user_service.get_user_by_email(email)
    if user is None:
        raise credentials_exception
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Verificar que el usuario actual esté activo"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user
