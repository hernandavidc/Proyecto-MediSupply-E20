import requests
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


def verify_token_with_user_service(token: str) -> dict | None:
    """Verifica el token llamando al endpoint /api/v1/users/me del user-service.

    Si el token es válido, devuelve el payload (JSON) del usuario. Si no, devuelve None.
    """
    if not token:
        return None

    url = settings.USER_SERVICE_URL.rstrip('/') + '/api/v1/users/me'
    headers = {'Authorization': f'Bearer {token}'}
    try:
        resp = requests.get(url, headers=headers, timeout=3)
    except requests.RequestException:
        # Si no se puede contactar al user-service, tratamos el token como inválido
        return None

    if resp.status_code == 200:
        return resp.json()
    return None


def require_auth(request: Request) -> dict:
    """Helper sencillo para verificar Authorization header y devolver user json.

    Lanza HTTPException 401 si no hay token o es inválido.
    """
    # Eximir rutas públicas
    path = request.url.path
    if path in EXEMPT_PATHS or path.startswith('/supplier-docs') or path.startswith('/supplier-openapi'):
        return None

    auth = request.headers.get('authorization') or request.headers.get('Authorization')
    if not auth or not auth.lower().startswith('bearer '):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing Authorization header')

    token = auth.split(' ', 1)[1].strip()
    user_json = verify_token_with_user_service(token)
    if user_json is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or expired token')

    return user_json
