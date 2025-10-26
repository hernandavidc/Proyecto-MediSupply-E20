import pytest
import io
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.services.csv_processor import CSVProcessor
from app.services.proveedor_service import ProveedorService

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def proveedor_test(db_session):
    """Crear un proveedor de prueba"""
    prov_service = ProveedorService(db_session)
    return prov_service.crear_proveedor({
        "razon_social": "Proveedor Test",
        "paises_operacion": [1],
        "certificaciones_sanitarias": [1, 2],
        "categorias_suministradas": [1]
    })

def crear_csv_valido(proveedor_id: int) -> bytes:
    """Crear un CSV válido para testing"""
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
        'ABC123', 'Producto Test 1', str(proveedor_id), 'https://example.com/ficha1.pdf',
        '2-8°C', '45-65%', 'Protegido', 'Adecuada', 'Alto', 'Vidrio',
        'Analgésicos', '2025-12-31',
        '10.50', '1;2'
    ])
    
    writer.writerow([
        'DEF456', 'Producto Test 2', str(proveedor_id), '',
        '', '', '', '', '', '',
        'Antibióticos', '',
        '25.00', '1'
    ])
    
    return output.getvalue().encode('utf-8')

def crear_csv_invalido() -> bytes:
    """Crear un CSV con errores para testing"""
    output = io.StringIO()
    writer = csv.writer(output, delimiter='|')
    
    # Header incorrecto (falta una columna)
    writer.writerow([
        'sku', 'nombre_producto', 'proveedor_id', 'ficha_tecnica_url',
        'ca_temp', 'ca_humedad', 'ca_luz', 'ca_ventilacion', 'ca_seguridad', 'ca_envase',
        'org_tipo_medicamento', 'org_fecha_vencimiento',
        'valor_unitario_usd'  # Falta certificaciones_sanitarias
    ])
    
    return output.getvalue().encode('utf-8')

def crear_csv_datos_invalidos(proveedor_id: int) -> bytes:
    """Crear un CSV con datos inválidos para testing"""
    output = io.StringIO()
    writer = csv.writer(output, delimiter='|')
    
    # Header correcto
    writer.writerow([
        'sku', 'nombre_producto', 'proveedor_id', 'ficha_tecnica_url',
        'ca_temp', 'ca_humedad', 'ca_luz', 'ca_ventilacion', 'ca_seguridad', 'ca_envase',
        'org_tipo_medicamento', 'org_fecha_vencimiento',
        'valor_unitario_usd', 'certificaciones_sanitarias'
    ])
    
    # Datos inválidos
    writer.writerow([
        'ABC123', 'Producto Test 1', str(proveedor_id), 'https://example.com/ficha1.pdf',
        '2-8°C', '45-65%', 'Protegido', 'Adecuada', 'Alto', 'Vidrio',
        'TipoInvalido', '2025-12-31',  # Tipo de medicamento inválido
        '10.50', '1;2'
    ])
    
    writer.writerow([
        '0BC123', 'Producto Test 2', str(proveedor_id), '',  # SKU con 0
        '', '', '', '', '', '',
        'Antibióticos', '',
        '25.00', '1'
    ])
    
    return output.getvalue().encode('utf-8')

def test_procesar_csv_valido(db_session, proveedor_test):
    """Test procesamiento de CSV válido"""
    processor = CSVProcessor(db_session)
    csv_content = crear_csv_valido(proveedor_test.id)
    
    resultado = processor.procesar_archivo(csv_content, rechazar_lote_ante_errores=True)
    
    assert resultado.total_lineas == 2
    assert resultado.exitosas == 2
    assert resultado.fallidas == 0
    assert len(resultado.errores) == 0
    assert len(resultado.productos_creados) == 2

def test_procesar_csv_columnas_incorrectas(db_session):
    """Test procesamiento de CSV con columnas incorrectas"""
    processor = CSVProcessor(db_session)
    csv_content = crear_csv_invalido()
    
    resultado = processor.procesar_archivo(csv_content, rechazar_lote_ante_errores=True)
    
    assert resultado.total_lineas == 0
    assert resultado.exitosas == 0
    assert resultado.fallidas == 0
    assert len(resultado.errores) > 0
    assert any('Faltan las siguientes columnas' in error.error for error in resultado.errores)

def test_procesar_csv_datos_invalidos_rechazar_lote(db_session, proveedor_test):
    """Test procesamiento de CSV con datos inválidos - rechazar lote"""
    processor = CSVProcessor(db_session)
    csv_content = crear_csv_datos_invalidos(proveedor_test.id)
    
    resultado = processor.procesar_archivo(csv_content, rechazar_lote_ante_errores=True)
    
    # Con rechazar_lote_ante_errores=True, se detiene en el primer error
    assert resultado.total_lineas == 1  # Solo procesa la primera línea
    assert resultado.exitosas == 0
    assert resultado.fallidas == 1
    assert len(resultado.errores) > 0
    assert len(resultado.productos_creados) == 0

def test_procesar_csv_datos_invalidos_procesar_validos(db_session, proveedor_test):
    """Test procesamiento de CSV con datos inválidos - procesar válidos"""
    processor = CSVProcessor(db_session)
    
    # Crear CSV con una línea válida y una inválida
    output = io.StringIO()
    writer = csv.writer(output, delimiter='|')
    
    writer.writerow([
        'sku', 'nombre_producto', 'proveedor_id', 'ficha_tecnica_url',
        'ca_temp', 'ca_humedad', 'ca_luz', 'ca_ventilacion', 'ca_seguridad', 'ca_envase',
        'org_tipo_medicamento', 'org_fecha_vencimiento',
        'valor_unitario_usd', 'certificaciones_sanitarias'
    ])
    
    # Línea válida
    writer.writerow([
        'ABC123', 'Producto Válido', str(proveedor_test.id), 'https://example.com/ficha1.pdf',
        '2-8°C', '45-65%', 'Protegido', 'Adecuada', 'Alto', 'Vidrio',
        'Analgésicos', '2025-12-31',
        '10.50', '1;2'
    ])
    
    # Línea inválida
    writer.writerow([
        '0BC123', 'Producto Inválido', str(proveedor_test.id), '',  # SKU con 0
        '', '', '', '', '', '',
        'Antibióticos', '',
        '25.00', '1'
    ])
    
    csv_content = output.getvalue().encode('utf-8')
    resultado = processor.procesar_archivo(csv_content, rechazar_lote_ante_errores=False)
    
    assert resultado.total_lineas == 2
    assert resultado.exitosas == 1
    assert resultado.fallidas == 1
    assert len(resultado.errores) == 1
    assert len(resultado.productos_creados) == 1

def test_validar_columnas_correctas():
    """Test validación de columnas correctas"""
    processor = CSVProcessor(None)
    columnas_correctas = [
        'sku', 'nombre_producto', 'proveedor_id', 'ficha_tecnica_url',
        'ca_temp', 'ca_humedad', 'ca_luz', 'ca_ventilacion', 'ca_seguridad', 'ca_envase',
        'org_tipo_medicamento', 'org_fecha_vencimiento',
        'valor_unitario_usd', 'certificaciones_sanitarias'
    ]
    
    errores = processor._validar_columnas(columnas_correctas)
    assert len(errores) == 0

def test_validar_columnas_faltantes():
    """Test validación de columnas faltantes"""
    processor = CSVProcessor(None)
    columnas_faltantes = [
        'sku', 'nombre_producto', 'proveedor_id'
    ]
    
    errores = processor._validar_columnas(columnas_faltantes)
    assert len(errores) > 0
    assert any('Faltan las siguientes columnas' in error.error for error in errores)

def test_convertir_fila_a_producto():
    """Test conversión de fila CSV a formato ProductoCSV"""
    processor = CSVProcessor(None)
    
    fila = {
        'sku': 'ABC123',
        'nombre_producto': 'Producto Test',
        'proveedor_id': '1',
        'ficha_tecnica_url': 'https://example.com/ficha.pdf',
        'ca_temp': '2-8°C',
        'ca_humedad': '45-65%',
        'ca_luz': 'Protegido',
        'ca_ventilacion': 'Adecuada',
        'ca_seguridad': 'Alto',
        'ca_envase': 'Vidrio',
        'org_tipo_medicamento': 'Analgésicos',
        'org_fecha_vencimiento': '2025-12-31',
        'valor_unitario_usd': '10.50',
        'certificaciones_sanitarias': '1;2'
    }
    
    resultado = processor._convertir_fila_a_producto(fila)
    
    assert resultado['sku'] == 'ABC123'
    assert resultado['nombre_producto'] == 'Producto Test'
    assert resultado['proveedor_id'] == 1
    assert resultado['ficha_tecnica_url'] == 'https://example.com/ficha.pdf'
    assert resultado['condicion_almacenamiento']['ca_temp'] == '2-8°C'
    assert resultado['organizacion']['org_tipo_medicamento'] == 'Analgésicos'
    assert resultado['valor_unitario_usd'] == 10.50
    assert resultado['certificaciones_sanitarias'] == '1;2'
