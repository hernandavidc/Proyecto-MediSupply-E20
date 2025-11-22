from jose import JWTError, jwt
from fastapi import HTTPException, status
from starlette.requests import Request
from app.core.config import settings


EXEMPT_PATHS = [
    '/',
    '/healthz',
    settings.DOCS_URL if hasattr(settings, 'DOCS_URL') else '/supplier-docs',
    '/supplier-docs',
    '/supplier-redoc',
    '/supplier-openapi.json',
]


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


def require_auth(request: Request) -> dict | None:
    """Helper sencillo para verificar Authorization header y devolver user payload.

    Lanza HTTPException 401 si no hay token o es inválido.
    Retorna None para rutas exentas.
    """
    # Eximir rutas públicas
    path = request.url.path
    if path in EXEMPT_PATHS or path.startswith('/supplier-docs') or path.startswith('/supplier-openapi'):
        return None

    auth = request.headers.get('authorization') or request.headers.get('Authorization')
    if not auth or not auth.lower().startswith('bearer '):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing Authorization header')

    token = auth.split(' ', 1)[1].strip()
    payload = get_token_payload(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or expired token')

    return payload
