"""
Fixtures compartidos para pruebas de performance
"""
import pytest
import httpx
from config import EDGE_PROXY_URL, TEST_USER_EMAIL, TEST_USER_PASSWORD


@pytest.fixture(scope="session")
def auth_token():
    """
    Obtiene un token JWT válido para usar en las pruebas
    """
    url = f"{EDGE_PROXY_URL}/api/v1/users/generate-token"
    payload = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("access_token")
    except Exception as e:
        pytest.skip(f"No se pudo obtener token de autenticación: {e}")


@pytest.fixture(scope="session")
def auth_headers(auth_token):
    """
    Headers de autenticación para usar en las pruebas
    """
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture(scope="session")
def http_client():
    """
    Cliente HTTP reutilizable con timeout adecuado
    """
    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        yield client


@pytest.fixture
def vendedor_id(http_client, auth_headers):
    """
    Obtiene un vendedor existente para pruebas de rutas
    """
    url = f"{EDGE_PROXY_URL}/api/v1/vendedores"
    try:
        response = http_client.get(url, headers=auth_headers)
        response.raise_for_status()
        vendedores = response.json()
        if vendedores and len(vendedores) > 0:
            return vendedores[0]["id"]
        else:
            pytest.skip("No hay vendedores en el sistema para probar")
    except Exception as e:
        pytest.skip(f"No se pudo obtener vendedores: {e}")

