
import os
from typing import Optional
from fastapi import HTTPException, Request, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.auth import verify_token_with_user_service
from fastapi import Depends

# Security scheme used for OpenAPI (shows the lock icon in docs)
# Set auto_error=False so FastAPI won't automatically raise 401 when the
# Authorization header is missing. This allows `AUTH_DISABLED=true` or
# unauthenticated test containers to call endpoints without failing at
# dependency resolution time.
_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Security(_bearer_scheme)) -> dict:
	"""Dependency para inyectar el usuario actual en endpoints.

	Comportamiento:
	- Si `AUTH_DISABLED=true` en el entorno, devuelve un usuario de prueba (para CI/tests locales).
	- Si `request.state.user` ya fue poblado por el middleware, lo devuelve (evita doble verificación remota).
	- En caso contrario, delega la verificación al user-service vía `verify_token_with_user_service`.
	Lanza 401 si el token es inválido o user-service no responde.
	"""
	# Test / local shortcut
	if os.getenv("AUTH_DISABLED", "false").lower() == "true":
		return {"id": 0, "email": "test@local", "name": "test-user", "is_active": True}

	# If middleware already validated the token it should have set request.state.user
	user: Optional[dict] = getattr(request.state, "user", None)
	if user:
		return user


	# Prefer using credentials provided by Security(HTTPBearer) so OpenAPI marks the endpoint as secured
	token = None
	if credentials:
		# credentials is HTTPAuthorizationCredentials(scheme='Bearer', credentials='<token>')
		if credentials.scheme and credentials.scheme.lower() == 'bearer':
			token = credentials.credentials
		else:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization scheme")

	# Fallback to raw header parsing if Security did not provide credentials (maintain backward compatibility)
	if not token:
		auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
		if not auth_header:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
		parts = auth_header.split()
		if len(parts) != 2 or parts[0].lower() != "bearer":
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header format")
		token = parts[1]

	user = verify_token_with_user_service(token)
	if not user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
	return user


def require_auth_security(credentials: Optional[HTTPAuthorizationCredentials] = Security(HTTPBearer(auto_error=False))) -> dict:
	"""Security dependency to show OpenAPI lock and validate token.

	This is intended to be used with Security(...) at the router level so
	FastAPI shows the padlock in the docs. It performs the same token
	validation as get_current_user but is a minimal dependency that accepts
	the HTTP Bearer credential directly.
	"""
	# If tests disable auth, allow through with a test user
	if os.getenv("AUTH_DISABLED", "false").lower() == "true":
		return {"id": 0, "email": "test@local", "name": "test-user", "is_active": True}

	if not credentials or not credentials.scheme or credentials.scheme.lower() != 'bearer':
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing credentials")

	token = credentials.credentials
	user = verify_token_with_user_service(token)
	if not user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
	return user


def require_roles(*allowed_roles: str):
	"""Factory dependency: returns a dependency that verifies the current user's role.

	Behavior:
	- User with id == 1 is considered global admin and is allowed for all endpoints.
	- Otherwise the user's `role` (name) must be in allowed_roles.

	Usage example in routers:
		from fastapi import Depends
		from app.core.dependencies import require_roles

		router = APIRouter(..., dependencies=[Depends(require_roles('Vendedor'))])
	"""
	def _dep(user: dict = Depends(get_current_user)) -> dict:
		# global admin shortcut (user id 1)
		try:
			if user.get('id') == 1:
				return user
		except Exception:
			pass

		role_name = None
		# user may include 'role' (name) or nested object
		if isinstance(user.get('role'), dict):
			role_name = user.get('role').get('name')
		else:
			role_name = user.get('role')

		if role_name is None or role_name not in allowed_roles:
			raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para acceder a este recurso")
		return user

	return _dep

