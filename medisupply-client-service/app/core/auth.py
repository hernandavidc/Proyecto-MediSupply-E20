from jose import JWTError, jwt
from app.core.config import settings

def verify_token(token: str):
    """
    Verificar token JWT y extraer el email del usuario
    
    Args:
        token: Token JWT en formato string
        
    Returns:
        str: Email del usuario si el token es válido, None si no es válido
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None

def get_token_payload(token: str):
    """
    Obtener el payload completo del token sin validar expiración
    (Útil para debugging o información adicional)
    
    Args:
        token: Token JWT en formato string
        
    Returns:
        dict: Payload del token si es válido, None si no es válido
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None

