from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.schemas.user_schema import UserCreate, UserResponse, UserLogin, Token, HealthCheck
from app.core.dependencies import get_user_service, get_current_active_user
from app.core.database import get_db
from app.services.user_service import UserService
from app.models.user import User

router = APIRouter()

# ===== ENDPOINTS PARA POSTMAN (JSON) =====

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user: UserCreate, 
    user_service: UserService = Depends(get_user_service)
):
    """✅ Registrar un nuevo usuario (JSON) - Para Postman"""
    return user_service.create_user(user)

@router.post("/generate-token", response_model=Token)
def generate_access_token(
    user_login: UserLogin,
    user_service: UserService = Depends(get_user_service)
):
    """🔑 Generar token de acceso JWT (JSON) - Para Postman y APIs"""
    return user_service.login_user(user_login)

# ===== ENDPOINTS PARA SWAGGER UI (OAuth2 Form) =====

@router.post("/token", response_model=Token)
def generate_token_oauth2(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service)
):
    """🔐 Generar token de acceso JWT (OAuth2 Form) - Para Swagger UI"""
    user_login = UserLogin(email=form_data.username, password=form_data.password)
    return user_service.login_user(user_login)

# ===== ENDPOINTS PROTEGIDOS =====

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """👤 Obtener información del usuario actual (requiere token)"""
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int, 
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_active_user)
):
    """👥 Obtener un usuario por ID (requiere autenticación)"""
    return user_service.get_user(user_id)

# ===== HEALTH CHECKS =====

@router.get("/", response_model=HealthCheck)
def health_check():
    """💚 Endpoint de health check"""
    return HealthCheck(
        status="healthy",
        message="User service is running",
        timestamp=datetime.now(timezone.utc)
    )
