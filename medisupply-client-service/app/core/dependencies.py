from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.auth import verify_token
from app.core.config import settings

# Esquema OAuth2 para extraer el token del header Authorization
# tokenUrl se usa para Swagger UI, apunta al User Service
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.USER_SERVICE_URL}/api/v1/users/token",
    scheme_name="Bearer"
)

def get_current_user_email(
    token: str = Depends(oauth2_scheme)
) -> str:
    """
    Dependencia de FastAPI para obtener el email del usuario desde el token JWT
    
    Esta dependencia:
    1. Extrae el token del header Authorization: Bearer <token>
    2. Verifica que el token sea válido usando verify_token
    3. Retorna el email del usuario si el token es válido
    
    Uso en rutas:
        @router.post("/")
        def create_client(
            client_data: ClientCreate,
            db: Session = Depends(get_db),
            user_email: str = Depends(get_current_user_email)
        ):
            # Lógica del endpoint
            return client
    
    Args:
        token: Token JWT extraído automáticamente del header Authorization
        
    Returns:
        str: Email del usuario autenticado
        
    Raises:
        HTTPException: 401 si el token es inválido o no está presente
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    email = verify_token(token)
    if email is None:
        raise credentials_exception
    
    return email

# Opcional: Si necesitas información adicional del token
def get_current_user_info(
    token: str = Depends(oauth2_scheme)
) -> dict:
    """
    Dependencia alternativa que retorna información completa del token
    
    Returns:
        dict: Información del usuario desde el token (email, exp, etc.)
    """
    from app.core.auth import get_token_payload
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = get_token_payload(token)
    if payload is None:
        raise credentials_exception
    
    return payload

