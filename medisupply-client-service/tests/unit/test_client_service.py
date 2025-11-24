import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.services.client_service import ClientService
from app.models.client import Client
from app.schemas.client_schema import ClientCreate, ClientUpdate
from fastapi import HTTPException, status


@pytest.fixture
def mock_db_session():
    """Mock database session"""
    return Mock(spec=Session)


@pytest.fixture
def sample_client_create():
    """Sample client create data"""
    return ClientCreate(
        nombre="Test Company S.A.",
        nit="1234567890",
        direccion="123 Test Street",
        nombre_contacto="John Doe",
        telefono_contacto="+1234567890",
        email_contacto="john.doe@testcompany.com"
    )


@pytest.fixture
def sample_client():
    """Sample client model instance"""
    client = Client(
        id="client-123",
        nombre="Test Company S.A.",
        nit="1234567890",
        direccion="123 Test Street",
        nombre_contacto="John Doe",
        telefono_contacto="+1234567890",
        email_contacto="john.doe@testcompany.com",
        is_validated=False
    )
    return client


class TestClientService:
    """Test ClientService methods"""
    
    def test_generate_temporary_password(self):
        """Test password generation"""
        password = ClientService._generate_temporary_password(12)
        
        assert len(password) == 12
        assert any(c.isupper() for c in password)
        assert any(c.islower() for c in password)
        assert any(c.isdigit() for c in password)
        assert any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    def test_generate_temporary_password_different_length(self):
        """Test password generation with different lengths"""
        password_8 = ClientService._generate_temporary_password(8)
        password_16 = ClientService._generate_temporary_password(16)
        
        assert len(password_8) == 8
        assert len(password_16) == 16
        # Passwords should be different
        assert password_8 != password_16
    
    @pytest.mark.asyncio
    async def test_get_cliente_role_id_success(self, monkeypatch):
        """Test getting role ID successfully"""
        async def mock_get(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = [
                {"id": 1, "name": "Admin"},
                {"id": 2, "name": "Cliente"},
                {"id": 3, "name": "Vendedor"}
            ]
            return mock_response
        
        class MockAsyncClient:
            def __init__(self, *args, **kwargs):
                pass
            async def __aenter__(self):
                return self
            async def __aexit__(self, *args):
                pass
            get = mock_get
        
        monkeypatch.setattr('httpx.AsyncClient', MockAsyncClient)
        
        role_id = await ClientService._get_cliente_role_id()
        assert role_id == 2
    
    @pytest.mark.asyncio
    async def test_get_cliente_role_id_fallback_on_error(self, monkeypatch):
        """Test fallback role ID on connection error"""
        async def mock_get(*args, **kwargs):
            raise Exception("Connection error")
        
        class MockAsyncClient:
            def __init__(self, *args, **kwargs):
                pass
            async def __aenter__(self):
                return self
            async def __aexit__(self, *args):
                pass
            get = mock_get
        
        monkeypatch.setattr('httpx.AsyncClient', MockAsyncClient)
        
        role_id = await ClientService._get_cliente_role_id()
        assert role_id == ClientService.CLIENTE_ROLE_ID_FALLBACK
    
    @pytest.mark.asyncio
    async def test_get_cliente_role_id_fallback_on_404(self, monkeypatch):
        """Test fallback role ID when role service returns 404"""
        async def mock_get(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.status_code = 404
            return mock_response
        
        class MockAsyncClient:
            def __init__(self, *args, **kwargs):
                pass
            async def __aenter__(self):
                return self
            async def __aexit__(self, *args):
                pass
            get = mock_get
        
        monkeypatch.setattr('httpx.AsyncClient', MockAsyncClient)
        
        role_id = await ClientService._get_cliente_role_id()
        assert role_id == ClientService.CLIENTE_ROLE_ID_FALLBACK
    
    @pytest.mark.asyncio
    async def test_get_cliente_role_id_role_not_found_in_list(self, monkeypatch):
        """Test fallback when Cliente role is not in the list"""
        async def mock_get(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = [
                {"id": 1, "name": "Admin"},
                {"id": 3, "name": "Vendedor"}
            ]
            return mock_response
        
        class MockAsyncClient:
            def __init__(self, *args, **kwargs):
                pass
            async def __aenter__(self):
                return self
            async def __aexit__(self, *args):
                pass
            get = mock_get
        
        monkeypatch.setattr('httpx.AsyncClient', MockAsyncClient)
        
        role_id = await ClientService._get_cliente_role_id()
        assert role_id == ClientService.CLIENTE_ROLE_ID_FALLBACK
    
    def test_get_client_by_id_found(self, mock_db_session, sample_client):
        """Test getting existing client by ID"""
        mock_db_session.query().filter().first.return_value = sample_client
        
        result = ClientService.get_client_by_id(mock_db_session, "client-123")
        
        assert result == sample_client
        mock_db_session.query.assert_called_once()
    
    def test_get_client_by_id_not_found(self, mock_db_session):
        """Test getting non-existent client by ID"""
        mock_db_session.query().filter().first.return_value = None
        
        result = ClientService.get_client_by_id(mock_db_session, "nonexistent")
        
        assert result is None
    
    def test_get_client_by_nit_found(self, mock_db_session, sample_client):
        """Test getting existing client by NIT"""
        mock_db_session.query().filter().first.return_value = sample_client
        
        result = ClientService.get_client_by_nit(mock_db_session, "1234567890")
        
        assert result == sample_client
    
    def test_get_client_by_nit_not_found(self, mock_db_session):
        """Test getting non-existent client by NIT"""
        mock_db_session.query().filter().first.return_value = None
        
        result = ClientService.get_client_by_nit(mock_db_session, "nonexistent")
        
        assert result is None
    
    def test_list_clients_empty(self, mock_db_session):
        """Test listing clients with no results"""
        mock_db_session.query().count.return_value = 0
        mock_db_session.query().offset().limit().all.return_value = []
        
        result = ClientService.list_clients(mock_db_session, skip=0, limit=10)
        
        assert result == []
    
    def test_list_clients_with_results(self, mock_db_session, sample_client):
        """Test listing clients with results"""
        mock_clients = [sample_client]
        mock_db_session.query().count.return_value = 1
        mock_db_session.query().offset().limit().all.return_value = mock_clients
        
        result = ClientService.list_clients(mock_db_session, skip=0, limit=10)
        
        assert len(result) == 1
        assert result[0] == sample_client
    
    def test_list_clients_pagination(self, mock_db_session, sample_client):
        """Test client listing with pagination"""
        mock_clients = [sample_client]
        mock_db_session.query().count.return_value = 100
        mock_db_session.query().offset().limit().all.return_value = mock_clients
        
        result = ClientService.list_clients(mock_db_session, skip=10, limit=20)
        
        assert len(result) == 1
    
    def test_update_client(self, mock_db_session, sample_client):
        """Test updating client"""
        mock_db_session.query().filter().first.return_value = sample_client
        update_data = ClientUpdate(nombre_contacto="Jane Smith")
        
        result = ClientService.update_client(
            mock_db_session, 
            "client-123", 
            update_data
        )
        
        assert result.nombre_contacto == "Jane Smith"
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(sample_client)
    
    def test_update_client_not_found(self, mock_db_session):
        """Test updating non-existent client"""
        mock_db_session.query().filter().first.return_value = None
        update_data = ClientUpdate(nombre_contacto="Jane Smith")
        
        result = ClientService.update_client(
            mock_db_session,
            "nonexistent",
            update_data
        )
        
        assert result is None
    
    def test_delete_client(self, mock_db_session, sample_client):
        """Test deleting client"""
        mock_db_session.query().filter().first.return_value = sample_client
        
        result = ClientService.delete_client(mock_db_session, "client-123")
        
        assert result is True
        mock_db_session.delete.assert_called_once_with(sample_client)
        mock_db_session.commit.assert_called_once()
    
    def test_delete_client_not_found(self, mock_db_session):
        """Test deleting non-existent client"""
        mock_db_session.query().filter().first.return_value = None
        
        result = ClientService.delete_client(mock_db_session, "nonexistent")
        
        assert result is False
        mock_db_session.delete.assert_not_called()
    
    def test_validate_client(self, mock_db_session, sample_client):
        """Test validating client"""
        mock_db_session.query().filter().first.return_value = sample_client
        
        result = ClientService.validate_client(mock_db_session, "client-123")
        
        assert result.is_validated is True
        mock_db_session.commit.assert_called_once()
    
    def test_validate_client_not_found(self, mock_db_session):
        """Test validating non-existent client"""
        mock_db_session.query().filter().first.return_value = None
        
        result = ClientService.validate_client(mock_db_session, "nonexistent")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_validate_nit_valid_format(self):
        """Test NIT validation with valid format"""
        result = await ClientService.validate_nit("1234567890")
        
        assert result.nit == "1234567890"
        assert result.is_valid is True
    
    @pytest.mark.asyncio
    async def test_validate_nit_invalid_length(self):
        """Test NIT validation with invalid length"""
        result = await ClientService.validate_nit("123")
        
        assert result.nit == "123"
        assert result.is_valid is False
        assert "debe tener entre 9 y 10 dígitos" in result.message
    
    @pytest.mark.asyncio
    async def test_validate_nit_non_numeric(self):
        """Test NIT validation with non-numeric characters"""
        result = await ClientService.validate_nit("12345ABC90")
        
        assert result.nit == "12345ABC90"
        assert result.is_valid is False
        assert "solo debe contener dígitos" in result.message

