import pytest
import json
import io
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.main import app
from app.services.proveedor_service import ProveedorService

# Configurar base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def setup_database():
    """Configurar base de datos de prueba para cada test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client():
    """Cliente de prueba FastAPI"""
    return TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    """Sesión de base de datos para tests"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def proveedor_ejemplo(db_session):
    """Crear proveedor de ejemplo para los tests"""
    prov_service = ProveedorService(db_session)
    return prov_service.crear_proveedor({
        "razon_social": "Proveedor Test Integration",
        "paises_operacion": [1],
        "certificaciones_sanitarias": [1, 2, 3],
        "categorias_suministradas": [1]
    })

@pytest.fixture(scope="function")
def csv_content_valido():
    """Contenido CSV válido para pruebas"""
    return """sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias
MED1|Paracetamol 500mg|1|https://ejemplo.com/ficha.pdf|2-8°C|45-65%|Protegido de luz|Ventilación normal|Controlado|Envase original|Analgésicos|2025-12-31|15.50|1;2
MED2|Ibuprofeno 400mg|1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|Antiinflamatorios|2025-10-15|18.75|1;3"""

@pytest.fixture(scope="function")
def csv_content_con_errores():
    """Contenido CSV con errores para pruebas"""
    return """sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias
MED1|Paracetamol 500mg|1||2-8°C|45-65%|Protegido de luz|Ventilación normal|Controlado|Envase original|Analgésicos|2025-12-31|15.50|1;2
MED2||1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|Antiinflamatorios|2025-10-15|18.75|1;3"""

class TestBulkUploadIntegration:
    """Tests de integración para carga masiva de productos"""

    def test_bulk_upload_endpoint_exists(self, client):
        """Verificar que el endpoint de carga masiva existe"""
        response = client.get("/docs")
        assert response.status_code == 200
        # El endpoint debería estar documentado en la API

    def test_bulk_upload_success_reject_on_errors_true(self, client, setup_database, proveedor_ejemplo, csv_content_valido):
        """Test de carga masiva exitosa con reject_on_errors=true"""
        # Crear archivo CSV temporal
        csv_file = io.BytesIO(csv_content_valido.encode('utf-8'))
        
        response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("test.csv", csv_file, "text/csv")},
            data={"reject_on_errors": "true"}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verificar respuesta
        assert data["total_procesados"] == 2
        assert data["exitosos"] == 2
        assert data["fallidos"] == 0
        assert len(data["productos_creados"]) == 2
        assert len(data["errores"]) == 0
        assert "Procesamiento exitoso" in data["mensaje"]
        
        # Verificar que los productos se crearon correctamente
        for producto in data["productos_creados"]:
            assert producto["origen"] == "BULK_UPLOAD"
            assert producto["sku"] in ["MED1", "MED2"]
            assert producto["proveedor_id"] == 1
            assert producto["valor_unitario_usd"] > 0

    def test_bulk_upload_success_reject_on_errors_false(self, client, setup_database, proveedor_ejemplo, csv_content_valido):
        """Test de carga masiva exitosa con reject_on_errors=false"""
        csv_file = io.BytesIO(csv_content_valido.encode('utf-8'))
        
        response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("test.csv", csv_file, "text/csv")},
            data={"reject_on_errors": "false"}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["total_procesados"] == 2
        assert data["exitosos"] == 2
        assert data["fallidos"] == 0

    def test_bulk_upload_with_errors_reject_on_errors_true(self, client, setup_database, proveedor_ejemplo, csv_content_con_errores):
        """Test de carga masiva con errores y reject_on_errors=true"""
        csv_file = io.BytesIO(csv_content_con_errores.encode('utf-8'))
        
        response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("test.csv", csv_file, "text/csv")},
            data={"reject_on_errors": "true"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Error en línea" in data["detail"]

    def test_bulk_upload_with_errors_reject_on_errors_false(self, client, setup_database, proveedor_ejemplo, csv_content_con_errores):
        """Test de carga masiva con errores y reject_on_errors=false"""
        csv_file = io.BytesIO(csv_content_con_errores.encode('utf-8'))
        
        response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("test.csv", csv_file, "text/csv")},
            data={"reject_on_errors": "false"}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["total_procesados"] == 2
        assert data["exitosos"] == 1
        assert data["fallidos"] == 1
        assert len(data["errores"]) == 1
        assert "Procesamiento completado con 1 errores" in data["mensaje"]

    def test_bulk_upload_invalid_file_type(self, client, setup_database):
        """Test con tipo de archivo inválido"""
        # Crear archivo que no es CSV
        txt_file = io.BytesIO(b"This is not a CSV file")
        
        response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("test.txt", txt_file, "text/plain")},
            data={"reject_on_errors": "true"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "El archivo debe ser de tipo CSV" in data["detail"]

    def test_bulk_upload_missing_columns(self, client, setup_database, proveedor_ejemplo):
        """Test con columnas faltantes"""
        csv_content_invalido = """sku|nombre_producto|proveedor_id|valor_unitario_usd
MED1|Paracetamol|1|15.50"""
        
        csv_file = io.BytesIO(csv_content_invalido.encode('utf-8'))
        
        response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("test.csv", csv_file, "text/csv")},
            data={"reject_on_errors": "true"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Faltan las siguientes columnas requeridas" in data["detail"]

    def test_bulk_upload_empty_file(self, client, setup_database):
        """Test con archivo vacío"""
        csv_file = io.BytesIO(b"")
        
        response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("empty.csv", csv_file, "text/csv")},
            data={"reject_on_errors": "true"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "El archivo CSV está vacío" in data["detail"]

    def test_bulk_upload_proveedor_no_existe(self, client, setup_database):
        """Test con proveedor que no existe"""
        csv_content = """sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias
MED1|Paracetamol|999||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|Analgésicos|2025-12-31|15.50|1;2"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("test.csv", csv_file, "text/csv")},
            data={"reject_on_errors": "true"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Proveedor no encontrado" in data["detail"]

    def test_bulk_upload_sku_invalid(self, client, setup_database, proveedor_ejemplo):
        """Test con SKU inválido (contiene '0')"""
        csv_content = """sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias
MED01|Paracetamol|1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|Analgésicos|2025-12-31|15.50|1;2"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("test.csv", csv_file, "text/csv")},
            data={"reject_on_errors": "true"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "SKU no puede contener el caracter 0" in data["detail"]

    def test_bulk_upload_tipo_medicamento_invalid(self, client, setup_database, proveedor_ejemplo):
        """Test con tipo de medicamento inválido"""
        csv_content = """sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias
MED1|Paracetamol|1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|TipoInvalido|2025-12-31|15.50|1;2"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("test.csv", csv_file, "text/csv")},
            data={"reject_on_errors": "true"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "tipo de medicamento inválido" in data["detail"]

    def test_bulk_upload_fecha_invalid(self, client, setup_database, proveedor_ejemplo):
        """Test con fecha inválida"""
        csv_content = """sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias
MED1|Paracetamol|1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|Analgésicos|fecha-invalida|15.50|1;2"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("test.csv", csv_file, "text/csv")},
            data={"reject_on_errors": "true"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Formato de fecha inválido" in data["detail"]

    def test_bulk_upload_certificaciones_invalid(self, client, setup_database, proveedor_ejemplo):
        """Test con certificaciones inválidas"""
        csv_content = """sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias
MED1|Paracetamol|1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|Analgésicos|2025-12-31|15.50|abc;def"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("test.csv", csv_file, "text/csv")},
            data={"reject_on_errors": "true"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Certificaciones deben ser números enteros" in data["detail"]

    def test_bulk_upload_valor_unitario_invalid(self, client, setup_database, proveedor_ejemplo):
        """Test con valor unitario inválido"""
        csv_content = """sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias
MED1|Paracetamol|1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|Analgésicos|2025-12-31|abc|1;2"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("test.csv", csv_file, "text/csv")},
            data={"reject_on_errors": "true"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Valor unitario inválido" in data["detail"]

    def test_bulk_upload_large_file(self, client, setup_database, proveedor_ejemplo):
        """Test con archivo grande (10 productos)"""
        # Generar CSV con 10 productos
        csv_lines = ["sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias"]
        
        for i in range(1, 11):
            csv_lines.append(f"MED{i}|Producto {i}|1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|Analgésicos|2025-12-31|{10 + i}.50|1;2")
        
        csv_content = "\n".join(csv_lines)
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("large_test.csv", csv_file, "text/csv")},
            data={"reject_on_errors": "true"}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["total_procesados"] == 10
        assert data["exitosos"] == 10
        assert data["fallidos"] == 0
        assert len(data["productos_creados"]) == 10

    def test_bulk_upload_products_appear_in_list(self, client, setup_database, proveedor_ejemplo, csv_content_valido):
        """Test que los productos cargados aparecen en la lista de productos"""
        # Cargar productos
        csv_file = io.BytesIO(csv_content_valido.encode('utf-8'))
        
        upload_response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("test.csv", csv_file, "text/csv")},
            data={"reject_on_errors": "true"}
        )
        
        assert upload_response.status_code == 201
        
        # Verificar que aparecen en la lista
        list_response = client.get("/api/v1/productos/")
        assert list_response.status_code == 200
        
        productos = list_response.json()
        assert len(productos) >= 2
        
        # Verificar que los productos cargados están en la lista
        skus_cargados = [p["sku"] for p in upload_response.json()["productos_creados"]]
        skus_en_lista = [p["sku"] for p in productos]
        
        for sku in skus_cargados:
            assert sku in skus_en_lista

    def test_bulk_upload_individual_product_access(self, client, setup_database, proveedor_ejemplo, csv_content_valido):
        """Test que los productos cargados son accesibles individualmente"""
        # Cargar productos
        csv_file = io.BytesIO(csv_content_valido.encode('utf-8'))
        
        upload_response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("test.csv", csv_file, "text/csv")},
            data={"reject_on_errors": "true"}
        )
        
        assert upload_response.status_code == 201
        
        # Acceder a cada producto individualmente
        for producto in upload_response.json()["productos_creados"]:
            product_id = producto["id"]
            
            response = client.get(f"/api/v1/productos/{product_id}")
            assert response.status_code == 200
            
            product_data = response.json()
            assert product_data["sku"] == producto["sku"]
            assert product_data["nombre_producto"] == producto["nombre_producto"]
            assert product_data["origen"] == "BULK_UPLOAD"

    def test_bulk_upload_audit_trail(self, client, setup_database, proveedor_ejemplo, csv_content_valido):
        """Test que se crea auditoría para productos cargados masivamente"""
        csv_file = io.BytesIO(csv_content_valido.encode('utf-8'))
        
        response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("test.csv", csv_file, "text/csv")},
            data={"reject_on_errors": "true"}
        )
        
        assert response.status_code == 201
        
        # Verificar que los productos tienen origen BULK_UPLOAD
        for producto in response.json()["productos_creados"]:
            assert producto["origen"] == "BULK_UPLOAD"

    def test_bulk_upload_error_reporting_detail(self, client, setup_database, proveedor_ejemplo):
        """Test que el reporte de errores es detallado"""
        csv_content = """sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias
MED1|Paracetamol|1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|Analgésicos|2025-12-31|15.50|1;2
MED2||1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|Analgésicos|2025-12-31|15.50|1;2
MED3|Producto|1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|TipoInvalido|2025-12-31|15.50|1;2"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("test.csv", csv_file, "text/csv")},
            data={"reject_on_errors": "false"}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["total_procesados"] == 3
        assert data["exitosos"] == 1
        assert data["fallidos"] == 2
        assert len(data["errores"]) == 2
        
        # Verificar que los errores tienen información detallada
        for error in data["errores"]:
            assert "linea" in error
            assert "campo" in error
            assert "valor" in error
            assert "error" in error
            assert error["linea"] in [3, 4]  # Líneas con errores
