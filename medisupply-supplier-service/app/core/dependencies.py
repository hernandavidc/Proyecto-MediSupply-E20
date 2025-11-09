from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.auth import verify_token_with_user_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/token")

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
	"""Dependency para inyectar el usuario actual en endpoints.

	Usa la función `verify_token_with_user_service` para delegar la validación al user-service.
	Lanza 401 si el token es inválido o user-service no responde.
	"""
	user = verify_token_with_user_service(token)
	if not user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
	return user

