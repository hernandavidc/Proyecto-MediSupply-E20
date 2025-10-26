import pytest
from fastapi.testclient import TestClient
from fastapi import status

from app.models.proveedor import Proveedor


@pytest.fixture
def auth_token(client):
    """Fixture que proporciona un token de autenticación para los tests"""
    # Registrar usuario
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    register_response = client.post("/api/v1/users/register", json=user_data)
    assert register_response.status_code == 201
    
    # Obtener token
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    
    login_response = client.post("/api/v1/users/token", json=login_data)
    assert login_response.status_code == 200
    
    token_data = login_response.json()
    token = token_data["access_token"]
    
    return {"Authorization": f"Bearer {token}"}


class TestProveedorRoutesIntegration:
    """Tests de integración para las rutas de proveedores usando PostgreSQL"""

    def test_create_provider_success(self, client: TestClient, auth_token: dict):
        """Test creación exitosa de proveedor"""
        provider_data = {
            "razon_social": "Proveedor Test Integration",
            "paises_operacion": ["Colombia", "Perú", "Ecuador"],
            "certificaciones_sanitarias": ["FDA", "EMA", "INVIMA"],
            "categorias_suministradas": ["Medicamentos especiales", "Medicamentos controlados"],
            "estado": "APROBADO"
        }
        
        response = client.post(
            "/api/v1/providers/",
            json=provider_data,
            headers=auth_token
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["razon_social"] == "Proveedor Test Integration"
        assert data["estado"] == "APROBADO"
        assert len(data["paises_operacion"]) == 3
        assert len(data["certificaciones_sanitarias"]) == 3
        assert "id" in data
        assert "created_at" in data
        
        # Verificar que se creó registro de auditoría
        audit_response = client.get(
            f"/api/v1/providers/{data['id']}/audit",
            headers=auth_token
        )
        assert audit_response.status_code == status.HTTP_200_OK
        audit_data = audit_response.json()
        assert len(audit_data) > 0
        assert audit_data[0]["operacion"] == "CREATE"
    
    def test_create_provider_invalid_data(self, client: TestClient, auth_token: dict):
        """Test creación con datos inválidos"""
        # Faltan campos requeridos
        provider_data = {
            "razon_social": "Proveedor Incompleto"
        }
        
        response = client.post(
            "/api/v1/providers/",
            json=provider_data,
            headers=auth_token
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        data = response.json()
        assert "detail" in data
    
    def test_list_providers_empty(self, client: TestClient, auth_token: dict):
        """Test listar proveedores sin datos"""
        response = client.get(
            "/api/v1/providers/",
            headers=auth_token
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_list_providers_with_data(self, client: TestClient, auth_token: dict, db_session):
        """Test listar proveedores con datos"""
        # Crear algunos proveedores directamente en la base de datos
        for i in range(3):
            provider = Proveedor(
                razon_social=f"Proveedor Test {i}",
                paises_operacion=["Colombia"],
                certificaciones_sanitarias=["FDA"],
                categorias_suministradas=["Medicamentos especiales"],
                estado="APROBADO",
                created_by=1,
                updated_by=1
            )
            db_session.add(provider)
        
        db_session.commit()
        
        response = client.get(
            "/api/v1/providers/",
            headers=auth_token
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        
        for provider in data:
            assert "razon_social" in provider
            assert "estado" in provider
    
    def test_list_providers_pagination(self, client: TestClient, auth_token: dict, db_session):
        """Test paginación de proveedores"""
        # Crear 5 proveedores
        for i in range(5):
            provider = Proveedor(
                razon_social=f"Proveedor Test {i}",
                paises_operacion=["Colombia"],
                certificaciones_sanitarias=["FDA"],
                categorias_suministradas=["Medicamentos especiales"],
                estado="APROBADO",
                created_by=1,
                updated_by=1
            )
            db_session.add(provider)
        
        db_session.commit()
        
        # Primera página (2 resultados)
        response = client.get(
            "/api/v1/providers/?skip=0&limit=2",
            headers=auth_token
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        
        # Segunda página
        response = client.get(
            "/api/v1/providers/?skip=2&limit=2",
            headers=auth_token
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
    
    def test_get_provider_by_id_success(self, client: TestClient, auth_token: dict):
        """Test obtener proveedor por ID"""
        # Crear proveedor
        provider_data = {
            "razon_social": "Proveedor Detail Test",
            "paises_operacion": ["Colombia"],
            "certificaciones_sanitarias": ["FDA", "EMA"],
            "categorias_suministradas": ["Medicamentos especiales"],
            "estado": "APROBADO"
        }
        
        create_response = client.post(
            "/api/v1/providers/",
            json=provider_data,
            headers=auth_token
        )
        
        provider_id = create_response.json()["id"]
        
        # Obtener proveedor
        response = client.get(
            f"/api/v1/providers/{provider_id}",
            headers=auth_token
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["razon_social"] == "Proveedor Detail Test"
        assert data["id"] == provider_id
        assert data["estado"] == "APROBADO"
    
    def test_get_provider_by_id_not_found(self, client: TestClient, auth_token: dict):
        """Test obtener proveedor inexistente"""
        response = client.get(
            "/api/v1/providers/999999",
            headers=auth_token
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Provider not found" in response.json()["detail"]
    
    def test_update_provider_success(self, client: TestClient, auth_token: dict, db_session):
        """Test actualización exitosa de proveedor"""
        # Crear proveedor
        provider = Proveedor(
            razon_social="Proveedor Original",
            paises_operacion=["Colombia"],
            certificaciones_sanitarias=["FDA"],
            categorias_suministradas=["Medicamentos especiales"],
            estado="APROBADO",
            created_by=1,
            updated_by=1
        )
        db_session.add(provider)
        db_session.commit()
        provider_id = provider.id
        
        # Actualizar proveedor
        update_data = {
            "razon_social": "Proveedor Actualizado",
            "contacto_principal": "Nuevo Contacto"
        }
        
        response = client.put(
            f"/api/v1/providers/{provider_id}",
            json=update_data,
            headers=auth_token
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["razon_social"] == "Proveedor Actualizado"
        assert data["contacto_principal"] == "Nuevo Contacto"
        
        # Verificar que se creó registro de auditoría
        audit_response = client.get(
            f"/api/v1/providers/{provider_id}/audit",
            headers=auth_token
        )
        audit_data = audit_response.json()
        
        # Debe haber al menos 2 registros de auditoría (CREATE y UPDATE)
        assert len(audit_data) >= 2
        update_audit = [a for a in audit_data if a["operacion"] == "UPDATE"]
        assert len(update_audit) > 0
    
    def test_delete_provider_success(self, client: TestClient, auth_token: dict, db_session):
        """Test eliminación exitosa de proveedor"""
        # Crear proveedor
        provider = Proveedor(
            razon_social="Proveedor a Eliminar",
            paises_operacion=["Colombia"],
            certificaciones_sanitarias=["FDA"],
            categorias_suministradas=["Medicamentos especiales"],
            estado="APROBADO",
            created_by=1,
            updated_by=1
        )
        db_session.add(provider)
        db_session.commit()
        provider_id = provider.id
        
        # Eliminar proveedor
        response = client.delete(
            f"/api/v1/providers/{provider_id}",
            headers=auth_token
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verificar que el proveedor fue eliminado
        get_response = client.get(
            f"/api/v1/providers/{provider_id}",
            headers=auth_token
        )
        
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_provider_workflow_complete(self, client: TestClient, auth_token: dict):
        """Test flujo completo de operaciones con proveedor"""
        # 1. Crear proveedor
        create_data = {
            "razon_social": "Proveedor Workflow",
            "paises_operacion": ["Colombia", "Perú"],
            "certificaciones_sanitarias": ["FDA", "EMA"],
            "categorias_suministradas": ["Medicamentos especiales"],
            "estado": "PENDIENTE_APROBACION",
            "contacto_principal": "Contacto Inicial"
        }
        
        create_response = client.post(
            "/api/v1/providers/",
            json=create_data,
            headers=auth_token
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        provider_id = create_response.json()["id"]
        
        # 2. Obtener proveedor
        get_response = client.get(
            f"/api/v1/providers/{provider_id}",
            headers=auth_token
        )
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["razon_social"] == "Proveedor Workflow"
        
        # 3. Actualizar estado a APROBADO
        update_data = {
            "estado": "APROBADO",
            "contacto_principal": "Contacto Aprobado"
        }
        
        update_response = client.put(
            f"/api/v1/providers/{provider_id}",
            json=update_data,
            headers=auth_token
        )
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["estado"] == "APROBADO"
        
        # 4. Listar proveedores y verificar que aparece
        list_response = client.get(
            "/api/v1/providers/",
            headers=auth_token
        )
        assert list_response.status_code == status.HTTP_200_OK
        providers = list_response.json()
        provider_found = any(p["id"] == provider_id for p in providers)
        assert provider_found
        
        # 5. Verificar auditoría completa
        audit_response = client.get(
            f"/api/v1/providers/{provider_id}/audit",
            headers=auth_token
        )
        assert audit_response.status_code == status.HTTP_200_OK
        audit_entries = audit_response.json()
        
        # Debe haber al menos CREATE y UPDATE
        assert len(audit_entries) >= 2
        
        operaciones = [entry["operacion"] for entry in audit_entries]
        assert "CREATE" in operaciones
        assert "UPDATE" in operaciones
        
        # 6. Eliminar proveedor
        delete_response = client.delete(
            f"/api/v1/providers/{provider_id}",
            headers=auth_token
        )
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # 7. Verificar que ya no existe
        final_get_response = client.get(
            f"/api/v1/providers/{provider_id}",
            headers=auth_token
        )
        assert final_get_response.status_code == status.HTTP_404_NOT_FOUND

