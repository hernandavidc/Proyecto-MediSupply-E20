import requests
from fastapi import HTTPException, status
from starlette.requests import Request
from app.core.config import settings


EXEMPT_PATHS = [
    '/',
    '/healthz',
    '/order-docs',
    '/order-redoc',
    '/order-openapi.json',
]


def verify_token_with_user_service(token: str) -> dict | None:
    if not token:
        return None

    url = settings.USER_SERVICE_URL.rstrip('/') + '/api/v1/users/me'
    headers = {'Authorization': f'Bearer {token}'}
    try:
        resp = requests.get(url, headers=headers, timeout=3)
    except requests.RequestException:
        return None

    if resp.status_code == 200:
        return resp.json()
    return None


def require_auth(request: Request) -> dict:
    path = request.url.path
    if path in EXEMPT_PATHS or path.startswith('/order-docs') or path.startswith('/order-openapi'):
        return None

    auth = request.headers.get('authorization') or request.headers.get('Authorization')
    if not auth or not auth.lower().startswith('bearer '):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing Authorization header')

    token = auth.split(' ', 1)[1].strip()
    user_json = verify_token_with_user_service(token)
    if user_json is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or expired token')

    return user_json
