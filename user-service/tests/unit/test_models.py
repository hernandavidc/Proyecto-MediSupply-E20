import pytest
from datetime import datetime
from app.models.user import User


class TestUserModel:
    """Tests para el modelo User"""
    
    def test_user_model_creation(self, db_session):
        """Test creación básica del modelo User"""
        user = User(
            name="Test User",
            email="test@example.com",
            hashed_password="hashed_password_123",
            is_active=True
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashed_password_123"
        assert user.is_active is True
        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)
    
    def test_user_model_default_values(self, db_session):
        """Test valores por defecto del modelo User"""
        user = User(
            name="Default User",
            email="default@example.com",
            hashed_password="hashed_password_123"
            # No especificar is_active para probar default
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.is_active is True  # Valor por defecto
        assert user.created_at is not None
    
    def test_user_model_unique_email(self, db_session):
        """Test que el email debe ser único"""
        # Crear primer usuario
        user1 = User(
            name="First User",
            email="unique@example.com",
            hashed_password="password1"
        )
        
        db_session.add(user1)
        db_session.commit()
        
        # Intentar crear segundo usuario con mismo email
        user2 = User(
            name="Second User",
            email="unique@example.com",
            hashed_password="password2"
        )
        
        db_session.add(user2)
        
        # Esto debería lanzar una excepción de integridad
        with pytest.raises(Exception):  # SQLAlchemy lanzará IntegrityError
            db_session.commit()
    
    def test_user_model_timestamps(self, db_session):
        """Test que los timestamps se generan correctamente"""
        user = User(
            name="Timestamp User",
            email="timestamp@example.com",
            hashed_password="hashed_password_123"
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Verificar created_at
        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)
        
        # updated_at debería ser None inicialmente (solo se establece en updates)
        assert user.updated_at is None
        
        # Hacer una actualización
        original_created_at = user.created_at
        user.name = "Updated Name"
        db_session.commit()
        db_session.refresh(user)
        
        # Verificar que created_at no cambió pero updated_at sí
        assert user.created_at == original_created_at
        assert user.updated_at is not None
        assert isinstance(user.updated_at, datetime)
    
    def test_user_model_string_representation(self, db_session):
        """Test representación en string del modelo (si existe __str__ o __repr__)"""
        user = User(
            name="String Test User",
            email="string@example.com",
            hashed_password="hashed_password_123"
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Test básico - al menos debería poder convertirse a string sin error
        str_representation = str(user)
        assert isinstance(str_representation, str)
        assert len(str_representation) > 0
    
    def test_user_model_required_fields(self, db_session):
        """Test que los campos requeridos están presentes"""
        # Intentar crear usuario sin email (required)
        with pytest.raises(Exception):  # TypeError o similar
            user = User(
                name="No Email User",
                # email faltante
                hashed_password="hashed_password_123"
            )
            db_session.add(user)
            db_session.commit()
        
        # Intentar crear usuario sin name (required)
        with pytest.raises(Exception):
            user = User(
                # name faltante
                email="noname@example.com",
                hashed_password="hashed_password_123"
            )
            db_session.add(user)
            db_session.commit()
        
        # Intentar crear usuario sin hashed_password (required)
        with pytest.raises(Exception):
            user = User(
                name="No Password User",
                email="nopassword@example.com"
                # hashed_password faltante
            )
            db_session.add(user)
            db_session.commit()
    
    def test_user_model_inactive_user(self, db_session):
        """Test creación de usuario inactivo"""
        user = User(
            name="Inactive User",
            email="inactive@example.com",
            hashed_password="hashed_password_123",
            is_active=False
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.is_active is False
    
    def test_user_model_table_name(self):
        """Test que el nombre de la tabla es correcto"""
        assert User.__tablename__ == "users"
    
    def test_user_model_columns(self):
        """Test que las columnas están definidas correctamente"""
        # Verificar que las columnas esperadas existen
        columns = [column.name for column in User.__table__.columns]
        
        expected_columns = [
            "id", "email", "name", "hashed_password", 
            "is_active", "created_at", "updated_at"
        ]
        
        for column in expected_columns:
            assert column in columns
    
    def test_user_model_indexes(self):
        """Test que los índices están configurados correctamente"""
        # Verificar que el email tiene índice único
        email_column = User.__table__.columns['email']
        assert email_column.unique is True
        assert email_column.index is True
        
        # Verificar que id es primary key
        id_column = User.__table__.columns['id']
        assert id_column.primary_key is True
        assert id_column.index is True
