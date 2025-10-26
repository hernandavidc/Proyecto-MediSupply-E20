import pytest
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.catalogs import Pais, Certificacion, CategoriaSuministro
from app.models.proveedor import Proveedor

@pytest.fixture(scope="session")
def test_database():
    """Configurar base de datos de prueba para toda la sesión"""
    # Usar base de datos en memoria para tests de integración
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Crear tablas
    Base.metadata.create_all(bind=engine)
    
    # Debug: Verificar que las tablas se crearon
    db = TestingSessionLocal()
    try:
        from sqlalchemy import text
        result = db.execute(text('SELECT name FROM sqlite_master WHERE type="table"'))
        tables = [row[0] for row in result.fetchall()]
        print(f"DEBUG: Tablas creadas en test_database: {tables}")
    except Exception as e:
        print(f"DEBUG: Error verificando tablas: {e}")
    finally:
        db.close()
    
    # Poblar datos base necesarios
    db = TestingSessionLocal()
    try:
        # Crear países
        paises = [
            Pais(id=1, nombre='Colombia'),
            Pais(id=2, nombre='Perú'),
            Pais(id=3, nombre='Ecuador'),
        ]
        db.add_all(paises)
        
        # Crear certificaciones
        certificaciones = [
            Certificacion(id=1, codigo='FDA', nombre='FDA'),
            Certificacion(id=2, codigo='EMA', nombre='EMA'),
            Certificacion(id=3, codigo='INVIMA', nombre='INVIMA'),
        ]
        db.add_all(certificaciones)
        
        # Crear categorías
        categorias = [
            CategoriaSuministro(id=1, nombre='Medicamentos especiales'),
            CategoriaSuministro(id=2, nombre='Medicamentos controlados'),
        ]
        db.add_all(categorias)
        
        # Crear proveedor de prueba
        proveedor = Proveedor(
            razon_social="Proveedor Test Integration",
            paises_operacion=[1],
            certificaciones_sanitarias=[1, 2, 3],
            categorias_suministradas=[1],
            estado="APROBADO"
        )
        db.add(proveedor)
        
        db.commit()
        
        yield engine, TestingSessionLocal
        
    finally:
        db.close()

@pytest.fixture(scope="function")
def clean_database(test_database):
    """Limpiar base de datos antes de cada test"""
    engine, SessionLocal = test_database
    
    # Limpiar tablas específicas (mantener datos base)
    db = SessionLocal()
    try:
        # Eliminar productos, planes y auditorías usando text()
        from sqlalchemy import text
        db.execute(text("DELETE FROM productos_auditoria"))
        db.execute(text("DELETE FROM productos"))
        db.execute(text("DELETE FROM planes_venta_auditoria"))
        db.execute(text("DELETE FROM planes_venta"))
        db.execute(text("DELETE FROM vendedores_auditoria"))
        db.execute(text("DELETE FROM vendedores"))
        db.execute(text("DELETE FROM proveedores_auditoria"))
        db.execute(text("DELETE FROM proveedores WHERE razon_social != 'Proveedor Test Integration'"))
        
        db.commit()
        yield db
    finally:
        db.close()

@pytest.fixture
def sample_csv_files():
    """Archivos CSV de ejemplo para pruebas"""
    return {
        "valid": """sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias
MED1|Paracetamol 500mg|1|https://ejemplo.com/ficha.pdf|2-8°C|45-65%|Protegido de luz|Ventilación normal|Controlado|Envase original|Analgésicos|2025-12-31|15.50|1;2
MED2|Ibuprofeno 400mg|1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|Antiinflamatorios|2025-10-15|18.75|1;3""",
        
        "with_errors": """sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias
MED1|Paracetamol 500mg|1||2-8°C|45-65%|Protegido de luz|Ventilación normal|Controlado|Envase original|Analgésicos|2025-12-31|15.50|1;2
MED2||1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|Antiinflamatorios|2025-10-15|18.75|1;3
MED3|Producto|1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|TipoInvalido|2025-12-31|15.50|1;2""",
        
        "missing_columns": """sku|nombre_producto|proveedor_id|valor_unitario_usd
MED1|Paracetamol|1|15.50""",
        
        "invalid_sku": """sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias
MED01|Paracetamol|1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|Analgésicos|2025-12-31|15.50|1;2""",
        
        "large_file": """sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias
""" + "\n".join([f"MED{i}|Producto {i}|1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|Analgésicos|2025-12-31|{10 + i}.50|1;2" for i in range(1, 21)])
    }

@pytest.fixture
def temp_csv_file(sample_csv_files, request):
    """Crear archivo CSV temporal para pruebas"""
    csv_type = request.param
    csv_content = sample_csv_files[csv_type]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        temp_file = f.name
    
    yield temp_file
    
    # Limpiar archivo temporal
    try:
        os.unlink(temp_file)
    except OSError:
        pass
