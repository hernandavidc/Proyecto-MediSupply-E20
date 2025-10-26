import pytest
import io
import csv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
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
def client():
    """Cliente de prueba para FastAPI"""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def proveedor_test(client):
    """Crear un proveedor de prueba para las pruebas de integración"""
    response = client.post("/api/v1/proveedores/", json={
        "razon_social": "Proveedor Test Integración",
        "paises_operacion": [1],
        "certificaciones_sanitarias": [1, 2, 3],
        "categorias_suministradas": [1]
    })
    assert response.status_code == 201
    return response.json()

def crear_csv_valido(proveedor_id: int) -> bytes:
    """Crear un CSV válido para testing de integración"""
    output = io.StringIO()
    writer = csv.writer(output, delimiter='|')
    
    # Header
    writer.writerow([
        'sku', 'nombre_producto', 'proveedor_id', 'ficha_tecnica_url',
        'ca_temp', 'ca_humedad', 'ca_luz', 'ca_ventilacion', 'ca_seguridad', 'ca_envase',
        'org_tipo_medicamento', 'org_fecha_vencimiento',
        'valor_unitario_usd', 'certificaciones_sanitarias'
    ])
    
    # Datos válidos
    writer.writerow([
        'ABC123', 'Paracetamol 500mg', str(proveedor_id), 'https://example.com/ficha1.pdf',
        '2-8°C', '45-65%', 'Protegido', 'Adecuada', 'Alto', 'Vidrio',
        'Analgésicos', '2025-12-31',
        '10.50', '1;2'
    ])
    
    writer.writerow([
        'DEF456', 'Amoxicilina 250mg', str(proveedor_id), '',
        '15-25°C', '30-70%', 'Normal', 'Buena', 'Medio', 'Plástico',
        'Antibióticos', '',
        '25.00', '1'
    ])
    
    writer.writerow([
        'GHI789', 'Ibuprofeno 400mg', str(proveedor_id), 'https://example.com/ficha3.pdf',
        '20-25°C', '40-60%', 'Protegido', 'Adecuada', 'Alto', 'Vidrio',
        'Antiinflamatorios', '2026-06-30',
        '15.75', '2;3'
    ])
    
    return output.getvalue().encode('utf-8')

def crear_csv_con_errores(proveedor_id: int) -> bytes:
    """Crear un CSV con errores para testing de integración"""
    output = io.StringIO()
    writer = csv.writer(output, delimiter='|')
    
    # Header
    writer.writerow([
        'sku', 'nombre_producto', 'proveedor_id', 'ficha_tecnica_url',
        'ca_temp', 'ca_humedad', 'ca_luz', 'ca_ventilacion', 'ca_seguridad', 'ca_envase',
        'org_tipo_medicamento', 'org_fecha_vencimiento',
        'valor_unitario_usd', 'certificaciones_sanitarias'
    ])
    
    # Línea válida
    writer.writerow([
        'ABC123', 'Paracetamol 500mg', str(proveedor_id), 'https://example.com/ficha1.pdf',
        '2-8°C', '45-65%', 'Protegido', 'Adecuada', 'Alto', 'Vidrio',
        'Analgésicos', '2025-12-31',
        '10.50', '1;2'
    ])
    
    # Línea con SKU inválido (contiene 0)
    writer.writerow([
        '0BC123', 'Producto Inválido', str(proveedor_id), '',
        '15-25°C', '30-70%', 'Normal', 'Buena', 'Medio', 'Plástico',
        'Antibióticos', '',
        '25.00', '1'
    ])
    
    # Línea con tipo de medicamento inválido
    writer.writerow([
        'GHI789', 'Producto Tipo Inválido', str(proveedor_id), '',
        '20-25°C', '40-60%', 'Protegido', 'Adecuada', 'Alto', 'Vidrio',
        'TipoInvalido', '2026-06-30',
        '15.75', '2;3'
    ])
    
    return output.getvalue().encode('utf-8')

def crear_csv_columnas_incorrectas() -> bytes:
    """Crear un CSV con columnas incorrectas"""
    output = io.StringIO()
    writer = csv.writer(output, delimiter='|')
    
    # Header incorrecto (falta certificaciones_sanitarias)
    writer.writerow([
        'sku', 'nombre_producto', 'proveedor_id', 'ficha_tecnica_url',
        'ca_temp', 'ca_humedad', 'ca_luz', 'ca_ventilacion', 'ca_seguridad', 'ca_envase',
        'org_tipo_medicamento', 'org_fecha_vencimiento',
        'valor_unitario_usd'  # Falta certificaciones_sanitarias
    ])
    
    return output.getvalue().encode('utf-8')

class TestCargaMasivaIntegracion:
    """Pruebas de integración para carga masiva de productos"""
    
    def test_carga_masiva_exitosa(self, client, proveedor_test):
        """Test de carga masiva exitosa completa"""
        csv_content = crear_csv_valido(proveedor_test['id'])
        
        # Realizar carga masiva
        response = client.post(
            "/api/v1/productos/carga-masiva",
            files={"archivo": ("test.csv", csv_content, "text/csv")},
            data={"rechazar_lote_ante_errores": "true"}
        )
        
        # Verificar respuesta
        assert response.status_code == 201
        data = response.json()
        assert data["total_lineas"] == 3
        assert data["exitosas"] == 3
        assert data["fallidas"] == 0
        assert len(data["errores"]) == 0
        assert len(data["productos_creados"]) == 3
        
        # Verificar que los productos se crearon correctamente
        productos = data["productos_creados"]
        assert productos[0]["sku"] == "ABC123"
        assert productos[0]["nombre_producto"] == "Paracetamol 500mg"
        assert productos[0]["proveedor_id"] == proveedor_test['id']
        assert productos[0]["origen"] == "CSV_MASIVO"
        assert productos[0]["certificaciones"] == [1, 2]
        
        assert productos[1]["sku"] == "DEF456"
        assert productos[1]["nombre_producto"] == "Amoxicilina 250mg"
        assert productos[1]["certificaciones"] == [1]
        
        assert productos[2]["sku"] == "GHI789"
        assert productos[2]["nombre_producto"] == "Ibuprofeno 400mg"
        assert productos[2]["certificaciones"] == [2, 3]
        
        # Verificar que los productos están en la base de datos
        response = client.get("/api/v1/productos/")
        assert response.status_code == 200
        productos_db = response.json()
        assert len(productos_db) == 3
        
        # Verificar que se pueden obtener individualmente
        for producto in productos:
            response = client.get(f"/api/v1/productos/{producto['id']}")
            assert response.status_code == 200
            producto_individual = response.json()
            assert producto_individual["sku"] == producto["sku"]
            assert producto_individual["origen"] == "CSV_MASIVO"
    
    def test_carga_masiva_rechazar_lote_ante_errores(self, client, proveedor_test):
        """Test de carga masiva rechazando lote ante errores"""
        csv_content = crear_csv_con_errores(proveedor_test['id'])
        
        # Realizar carga masiva con rechazar lote
        response = client.post(
            "/api/v1/productos/carga-masiva",
            files={"archivo": ("test.csv", csv_content, "text/csv")},
            data={"rechazar_lote_ante_errores": "true"}
        )
        
        # Verificar que se rechaza el lote
        assert response.status_code == 400
        data = response.json()
        assert "El lote fue rechazado debido a errores de validación" in data["detail"]["message"]
        assert len(data["detail"]["errores"]) > 0
        
        # Verificar que se procesó hasta el primer error (1 línea exitosa, 1 fallida)
        assert data["detail"]["estadisticas"]["total_lineas"] == 2
        assert data["detail"]["estadisticas"]["exitosas"] == 1
        assert data["detail"]["estadisticas"]["fallidas"] == 1
        
        # Verificar que hay un producto creado (la primera línea válida)
        response = client.get("/api/v1/productos/")
        assert response.status_code == 200
        productos = response.json()
        assert len(productos) == 1
        assert productos[0]["sku"] == "ABC123"
    
    def test_carga_masiva_procesar_validos(self, client, proveedor_test):
        """Test de carga masiva procesando solo los válidos"""
        csv_content = crear_csv_con_errores(proveedor_test['id'])
        
        # Realizar carga masiva procesando válidos
        response = client.post(
            "/api/v1/productos/carga-masiva",
            files={"archivo": ("test.csv", csv_content, "text/csv")},
            data={"rechazar_lote_ante_errores": "false"}
        )
        
        # Verificar respuesta
        assert response.status_code == 201
        data = response.json()
        assert data["total_lineas"] == 3
        assert data["exitosas"] == 1  # Solo la primera línea es válida
        assert data["fallidas"] == 2
        assert len(data["errores"]) == 2
        assert len(data["productos_creados"]) == 1
        
        # Verificar que se creó solo el producto válido
        producto_creado = data["productos_creados"][0]
        assert producto_creado["sku"] == "ABC123"
        assert producto_creado["nombre_producto"] == "Paracetamol 500mg"
        
        # Verificar errores específicos
        errores = data["errores"]
        sku_errors = [e for e in errores if e["campo"] == "sku"]
        tipo_errors = [e for e in errores if "tipo de medicamento" in e["error"]]
        
        assert len(sku_errors) == 1
        assert "SKU no puede contener el caracter 0" in sku_errors[0]["error"]
        
        assert len(tipo_errors) == 1
        assert "tipo de medicamento inválido" in tipo_errors[0]["error"]
        
        # Verificar que solo hay un producto en la base de datos
        response = client.get("/api/v1/productos/")
        assert response.status_code == 200
        productos = response.json()
        assert len(productos) == 1
        assert productos[0]["sku"] == "ABC123"
    
    def test_carga_masiva_columnas_incorrectas(self, client):
        """Test de carga masiva con columnas incorrectas"""
        csv_content = crear_csv_columnas_incorrectas()
        
        # Realizar carga masiva
        response = client.post(
            "/api/v1/productos/carga-masiva",
            files={"archivo": ("test.csv", csv_content, "text/csv")},
            data={"rechazar_lote_ante_errores": "true"}
        )
        
        # Verificar que se rechaza por columnas incorrectas
        assert response.status_code == 400
        data = response.json()
        assert "El lote fue rechazado debido a errores de validación" in data["detail"]["message"]
        
        errores = data["detail"]["errores"]
        assert len(errores) > 0
        assert any("Faltan las siguientes columnas" in error["error"] for error in errores)
    
    def test_carga_masiva_archivo_no_csv(self, client):
        """Test de carga masiva con archivo que no es CSV"""
        # Crear un archivo de texto que no es CSV
        contenido = "Este no es un archivo CSV válido"
        
        response = client.post(
            "/api/v1/productos/carga-masiva",
            files={"archivo": ("test.txt", contenido, "text/plain")},
            data={"rechazar_lote_ante_errores": "true"}
        )
        
        # Verificar que se rechaza por tipo de archivo
        assert response.status_code == 400
        assert "El archivo debe ser de tipo CSV" in response.json()["detail"]
    
    def test_carga_masiva_proveedor_inexistente(self, client):
        """Test de carga masiva con proveedor que no existe"""
        csv_content = crear_csv_valido(999)  # Proveedor que no existe
        
        response = client.post(
            "/api/v1/productos/carga-masiva",
            files={"archivo": ("test.csv", csv_content, "text/csv")},
            data={"rechazar_lote_ante_errores": "true"}
        )
        
        # Verificar que se rechaza por proveedor inexistente
        assert response.status_code == 400
        data = response.json()
        assert "El lote fue rechazado debido a errores de validación" in data["detail"]["message"]
        
        errores = data["detail"]["errores"]
        assert len(errores) > 0
        assert any("Proveedor no encontrado" in error["error"] for error in errores)
    
    def test_carga_masiva_certificaciones_incompatibles(self, client):
        """Test de carga masiva con certificaciones incompatibles"""
        # Crear proveedor con certificaciones limitadas
        response = client.post("/api/v1/proveedores/", json={
            "razon_social": "Proveedor Limitado",
            "paises_operacion": [1],
            "certificaciones_sanitarias": [1],  # Solo certificación 1
            "categorias_suministradas": [1]
        })
        assert response.status_code == 201
        proveedor = response.json()
        
        # Crear CSV con certificaciones que el proveedor no tiene
        output = io.StringIO()
        writer = csv.writer(output, delimiter='|')
        
        writer.writerow([
            'sku', 'nombre_producto', 'proveedor_id', 'ficha_tecnica_url',
            'ca_temp', 'ca_humedad', 'ca_luz', 'ca_ventilacion', 'ca_seguridad', 'ca_envase',
            'org_tipo_medicamento', 'org_fecha_vencimiento',
            'valor_unitario_usd', 'certificaciones_sanitarias'
        ])
        
        writer.writerow([
            'ABC123', 'Producto Test', str(proveedor['id']), '',
            '', '', '', '', '', '',
            'Analgésicos', '',
            '10.50', '2;3'  # Certificaciones que el proveedor no tiene
        ])
        
        csv_content = output.getvalue().encode('utf-8')
        
        response = client.post(
            "/api/v1/productos/carga-masiva",
            files={"archivo": ("test.csv", csv_content, "text/csv")},
            data={"rechazar_lote_ante_errores": "true"}
        )
        
        # Verificar que se rechaza por certificaciones incompatibles
        assert response.status_code == 400
        data = response.json()
        assert "El lote fue rechazado debido a errores de validación" in data["detail"]["message"]
        
        errores = data["detail"]["errores"]
        assert len(errores) > 0
        assert any("certificaciones compatibles" in error["error"] for error in errores)
    
    def test_carga_masiva_validaciones_campos(self, client, proveedor_test):
        """Test de carga masiva con validaciones de campos específicos"""
        output = io.StringIO()
        writer = csv.writer(output, delimiter='|')
        
        writer.writerow([
            'sku', 'nombre_producto', 'proveedor_id', 'ficha_tecnica_url',
            'ca_temp', 'ca_humedad', 'ca_luz', 'ca_ventilacion', 'ca_seguridad', 'ca_envase',
            'org_tipo_medicamento', 'org_fecha_vencimiento',
            'valor_unitario_usd', 'certificaciones_sanitarias'
        ])
        
        # Línea con valor unitario inválido (negativo)
        writer.writerow([
            'ABC123', 'Producto Test', str(proveedor_test['id']), '',
            '', '', '', '', '', '',
            'Analgésicos', '',
            '-10.50', '1'  # Valor negativo
        ])
        
        csv_content = output.getvalue().encode('utf-8')
        
        response = client.post(
            "/api/v1/productos/carga-masiva",
            files={"archivo": ("test.csv", csv_content, "text/csv")},
            data={"rechazar_lote_ante_errores": "true"}
        )
        
        # Verificar que se rechaza por valor inválido
        assert response.status_code == 400
        data = response.json()
        assert "El lote fue rechazado debido a errores de validación" in data["detail"]["message"]
        
        errores = data["detail"]["errores"]
        assert len(errores) > 0
        assert any("greater than 0" in error["error"] for error in errores)
    
    def test_carga_masiva_auditoria(self, client, proveedor_test):
        """Test de que la carga masiva genera auditoría correcta"""
        csv_content = crear_csv_valido(proveedor_test['id'])
        
        # Realizar carga masiva
        response = client.post(
            "/api/v1/productos/carga-masiva",
            files={"archivo": ("test.csv", csv_content, "text/csv")},
            data={"rechazar_lote_ante_errores": "true"}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verificar que todos los productos tienen origen CSV_MASIVO
        for producto in data["productos_creados"]:
            assert producto["origen"] == "CSV_MASIVO"
        
        # Verificar que se pueden obtener individualmente y tienen el origen correcto
        for producto in data["productos_creados"]:
            response = client.get(f"/api/v1/productos/{producto['id']}")
            assert response.status_code == 200
            producto_individual = response.json()
            assert producto_individual["origen"] == "CSV_MASIVO"
