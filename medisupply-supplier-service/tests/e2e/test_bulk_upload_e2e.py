import pytest
import io
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db
from tests.e2e.conftest import e2e_database, clean_e2e_database

@pytest.fixture
def client(e2e_database):
    """Cliente de prueba con base de datos configurada"""
    engine, SessionLocal = e2e_database
    
    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

class TestBulkUploadEndToEnd:
    """Tests de integración end-to-end para carga masiva"""

    def test_complete_bulk_upload_workflow(self, client, clean_e2e_database):
        """Test del flujo completo de carga masiva"""
        # 1. Verificar que no hay productos inicialmente
        response = client.get("/api/v1/productos/")
        assert response.status_code == 200
        initial_products = response.json()
        initial_count = len(initial_products)
        
        # 2. Preparar archivo CSV válido
        csv_content = """sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias
MED1|Paracetamol 500mg|1|https://ejemplo.com/ficha.pdf|2-8°C|45-65%|Protegido de luz|Ventilación normal|Controlado|Envase original|Analgésicos|2025-12-31|15.50|1;2
MED2|Ibuprofeno 400mg|1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|Antiinflamatorios|2025-10-15|18.75|1;3
MED3|Amoxicilina 250mg|1||2-8°C|45-65%|Protegido de luz|Ventilación controlada|Controlado|Envase original|Antibióticos|2025-08-20|25.00|2;3"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        # 3. Ejecutar carga masiva
        upload_response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("test.csv", csv_file, "text/csv")},
            data={"reject_on_errors": "true"}
        )
        
        # 4. Verificar respuesta de carga masiva
        assert upload_response.status_code == 201
        upload_data = upload_response.json()
        
        assert upload_data["total_procesados"] == 3
        assert upload_data["exitosos"] == 3
        assert upload_data["fallidos"] == 0
        assert len(upload_data["productos_creados"]) == 3
        
        # 5. Verificar que los productos aparecen en la lista
        list_response = client.get("/api/v1/productos/")
        assert list_response.status_code == 200
        
        products = list_response.json()
        assert len(products) == initial_count + 3
        
        # 6. Verificar cada producto individualmente
        uploaded_skus = [p["sku"] for p in upload_data["productos_creados"]]
        for producto in products:
            if producto["sku"] in uploaded_skus:
                assert producto["origen"] == "BULK_UPLOAD"
                assert producto["proveedor_id"] == 1
                assert producto["valor_unitario_usd"] > 0
                
                # Verificar acceso individual
                individual_response = client.get(f"/api/v1/productos/{producto['id']}")
                assert individual_response.status_code == 200
                individual_data = individual_response.json()
                assert individual_data["sku"] == producto["sku"]

    def test_bulk_upload_with_mixed_results(self, client, clean_e2e_database):
        """Test de carga masiva con resultados mixtos (algunos exitosos, algunos con errores)"""
        csv_content = """sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias
MED1|Paracetamol 500mg|1||2-8°C|45-65%|Protegido de luz|Ventilación normal|Controlado|Envase original|Analgésicos|2025-12-31|15.50|1;2
MED2||1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|Antiinflamatorios|2025-10-15|18.75|1;3
MED3|Amoxicilina 250mg|1||2-8°C|45-65%|Protegido de luz|Ventilación controlada|Controlado|Envase original|Antibióticos|2025-08-20|25.00|2;3
MED4|Producto|1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|TipoInvalido|2025-12-31|15.50|1;2"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        # Ejecutar con reject_on_errors=false
        upload_response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("test.csv", csv_file, "text/csv")},
            data={"reject_on_errors": "false"}
        )
        
        assert upload_response.status_code == 201
        upload_data = upload_response.json()
        
        # Verificar resultados mixtos
        assert upload_data["total_procesados"] == 4
        assert upload_data["exitosos"] == 2  # MED1 y MED3
        assert upload_data["fallidos"] == 2  # MED2 y MED4
        assert len(upload_data["errores"]) == 2
        
        # Verificar que solo los productos exitosos están en productos_creados
        successful_skus = [p["sku"] for p in upload_data["productos_creados"]]
        assert "MED1" in successful_skus
        assert "MED3" in successful_skus
        assert len(successful_skus) == 2

    def test_bulk_upload_performance_with_large_file(self, client, clean_e2e_database):
        """Test de rendimiento con archivo grande"""
        # Generar CSV con 50 productos
        csv_lines = ["sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias"]
        
        # Crear SKUs sin el caracter '0'
        for i in range(1, 51):
            # Usar letras para evitar el caracter '0'
            if i < 10:
                sku = f"MED{i}"
            elif i < 19:
                sku = f"MDA{i-9}"
            elif i < 28:
                sku = f"MDB{i-18}"
            elif i < 37:
                sku = f"MDC{i-27}"
            elif i < 46:
                sku = f"MDD{i-36}"
            else:
                sku = f"MDE{i-45}"
            csv_lines.append(f"{sku}|Producto {i}|1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|Analgésicos|2025-12-31|{10 + i}.50|1;2")
        
        csv_content = "\n".join(csv_lines)
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        # Medir tiempo de ejecución
        import time
        start_time = time.time()
        
        upload_response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("large_test.csv", csv_file, "text/csv")},
            data={"reject_on_errors": "true"}
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verificar éxito
        assert upload_response.status_code == 201
        upload_data = upload_response.json()
        
        assert upload_data["total_procesados"] == 50
        assert upload_data["exitosos"] == 50
        assert upload_data["fallidos"] == 0
        
        # Verificar rendimiento (debería ser rápido)
        assert execution_time < 5.0  # Menos de 5 segundos para 50 productos
        
        # Verificar que todos los productos se crearon
        list_response = client.get("/api/v1/productos/")
        assert list_response.status_code == 200
        
        products = list_response.json()
        assert len(products) >= 50

    def test_bulk_upload_error_scenarios(self, client, clean_e2e_database):
        """Test de diferentes escenarios de error"""
        
        # Test 1: Archivo vacío
        empty_file = io.BytesIO(b"")
        response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("empty.csv", empty_file, "text/csv")},
            data={"reject_on_errors": "true"}
        )
        assert response.status_code == 400
        assert "El archivo CSV está vacío" in response.json()["detail"]
        
        # Test 2: Tipo de archivo incorrecto
        txt_file = io.BytesIO(b"This is not a CSV file")
        response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("test.txt", txt_file, "text/plain")},
            data={"reject_on_errors": "true"}
        )
        assert response.status_code == 400
        assert "El archivo debe ser de tipo CSV" in response.json()["detail"]
        
        # Test 3: Columnas faltantes
        invalid_csv = """sku|nombre_producto|proveedor_id|valor_unitario_usd
MED1|Paracetamol|1|15.50"""
        csv_file = io.BytesIO(invalid_csv.encode('utf-8'))
        
        response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("invalid.csv", csv_file, "text/csv")},
            data={"reject_on_errors": "true"}
        )
        assert response.status_code == 400
        assert "Faltan las siguientes columnas requeridas" in response.json()["detail"]
        
        # Test 4: Proveedor inexistente
        csv_content = """sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias
MED1|Paracetamol|999||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|Analgésicos|2025-12-31|15.50|1;2"""
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("test.csv", csv_file, "text/csv")},
            data={"reject_on_errors": "true"}
        )
        assert response.status_code == 400
        assert "Proveedor no encontrado" in response.json()["detail"]

    def test_bulk_upload_data_validation(self, client, clean_e2e_database):
        """Test de validación de datos específicos"""
        
        # Test SKU inválido (contiene '0')
        csv_content = """sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias
MED01|Paracetamol|1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|Analgésicos|2025-12-31|15.50|1;2"""
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("test.csv", csv_file, "text/csv")},
            data={"reject_on_errors": "true"}
        )
        assert response.status_code == 400
        assert "SKU no puede contener el caracter 0" in response.json()["detail"]
        
        # Test tipo de medicamento inválido
        csv_content = """sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias
MED1|Paracetamol|1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|TipoInvalido|2025-12-31|15.50|1;2"""
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("test.csv", csv_file, "text/csv")},
            data={"reject_on_errors": "true"}
        )
        assert response.status_code == 400
        assert "tipo de medicamento inválido" in response.json()["detail"]
        
        # Test fecha inválida
        csv_content = """sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias
MED1|Paracetamol|1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|Analgésicos|fecha-invalida|15.50|1;2"""
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        response = client.post(
            "/api/v1/productos/bulk-upload",
            files={"file": ("test.csv", csv_file, "text/csv")},
            data={"reject_on_errors": "true"}
        )
        assert response.status_code == 400
        assert "Formato de fecha inválido" in response.json()["detail"]

    def test_bulk_upload_api_documentation(self, client):
        """Test que la API está documentada correctamente"""
        # Verificar que la documentación está disponible
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Verificar que el endpoint está en la documentación OpenAPI
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        openapi_data = response.json()
        assert "/api/v1/productos/bulk-upload" in openapi_data["paths"]
        
        # Verificar que el endpoint tiene la documentación correcta
        bulk_upload_path = openapi_data["paths"]["/api/v1/productos/bulk-upload"]
        assert "post" in bulk_upload_path
        
        post_info = bulk_upload_path["post"]
        assert "summary" in post_info
        assert "description" in post_info
        # El endpoint usa requestBody, no parameters
        assert "requestBody" in post_info
        assert "responses" in post_info
