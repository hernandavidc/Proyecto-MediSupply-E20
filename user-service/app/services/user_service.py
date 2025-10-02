from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.schemas.user_schema import UserCreate, UserResponse, UserLogin
from app.models.user import User
from app.core.auth import get_password_hash, verify_password, create_access_token
from typing import Optional

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserCreate) -> UserResponse:
        """Crear un nuevo usuario"""
        # Verificar si el email ya existe
        db_user = self.db.query(User).filter(User.email == user.email).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Crear hash de la contraseña
        hashed_password = get_password_hash(user.password)
        
        # Crear nuevo usuario
        db_user = User(
            name=user.name,
            email=user.email,
            hashed_password=hashed_password
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return UserResponse(
            id=db_user.id,
            name=db_user.name,
            email=db_user.email,
            is_active=db_user.is_active,
            created_at=db_user.created_at
        )

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Autenticar usuario con email y contraseña"""
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def login_user(self, user_login: UserLogin) -> dict:
        """Login de usuario y generación de token"""
        user = self.authenticate_user(user_login.email, user_login.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario inactivo"
            )
        
        # Crear token de acceso
        access_token = create_access_token(data={"sub": user.email})
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_user(self, user_id: int) -> UserResponse:
        """Obtener usuario por ID"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at
        )
