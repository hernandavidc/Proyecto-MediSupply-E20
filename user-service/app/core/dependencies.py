from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import verify_token
from app.services.user_service import UserService
from app.models.user import User

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
