import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.services.product_service import ProductService
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
def proveedor_ejemplo(db_session):
    """Crear un proveedor de ejemplo para los tests"""
    prov_service = ProveedorService(db_session)
    return prov_service.crear_proveedor({
        "razon_social": "Proveedor Test",
        "paises_operacion": [1],
        "certificaciones_sanitarias": [1, 2, 3],
        "categorias_suministradas": [1]
    })

def test_procesar_carga_masiva_exitosa(db_session, proveedor_ejemplo):
    """Test de carga masiva exitosa"""
    csv_content = """sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias
MED1|Paracetamol 500mg|1||2-8°C|45-65%|Protegido de luz|Ventilación normal|Controlado|Envase original|Analgésicos|2025-12-31|15.50|1;2
MED2|Ibuprofeno 400mg|1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|Antiinflamatorios|2025-10-15|18.75|1;3"""
    
    service = ProductService(db_session)
    result = service.procesar_carga_masiva(csv_content, reject_on_errors=True)
    
    assert result.total_procesados == 2
    assert result.exitosos == 2
    assert result.fallidos == 0
    assert len(result.productos_creados) == 2
    assert len(result.errores) == 0
    assert "Procesamiento exitoso" in result.mensaje

def test_procesar_carga_masiva_con_errores_rechazar_lote(db_session, proveedor_ejemplo):
    """Test de carga masiva con errores y rechazo de lote"""
    csv_content = """sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias
MED1|Paracetamol 500mg|1||2-8°C|45-65%|Protegido de luz|Ventilación normal|Controlado|Envase original|Analgésicos|2025-12-31|15.50|1;2
MED2||1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|Antiinflamatorios|2025-10-15|18.75|1;3"""
    
    service = ProductService(db_session)
    
    with pytest.raises(ValueError) as exc_info:
        service.procesar_carga_masiva(csv_content, reject_on_errors=True)
    
    assert "Error en línea 3" in str(exc_info.value)

def test_procesar_carga_masiva_con_errores_continuar(db_session, proveedor_ejemplo):
    """Test de carga masiva con errores pero continuando el procesamiento"""
    csv_content = """sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias
MED1|Paracetamol 500mg|1||2-8°C|45-65%|Protegido de luz|Ventilación normal|Controlado|Envase original|Analgésicos|2025-12-31|15.50|1;2
MED2||1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|Antiinflamatorios|2025-10-15|18.75|1;3"""
    
    service = ProductService(db_session)
    result = service.procesar_carga_masiva(csv_content, reject_on_errors=False)
    
    assert result.total_procesados == 2
    assert result.exitosos == 1
    assert result.fallidos == 1
    assert len(result.productos_creados) == 1
    assert len(result.errores) == 1
    assert "Procesamiento completado con 1 errores" in result.mensaje

def test_procesar_carga_masiva_columnas_faltantes(db_session):
    """Test de carga masiva con columnas faltantes"""
    csv_content = """sku|nombre_producto|proveedor_id|valor_unitario_usd
MED001|Paracetamol 500mg|1|15.50"""
    
    service = ProductService(db_session)
    
    with pytest.raises(ValueError) as exc_info:
        service.procesar_carga_masiva(csv_content, reject_on_errors=True)
    
    assert "Faltan las siguientes columnas requeridas" in str(exc_info.value)

def test_procesar_carga_masiva_archivo_vacio(db_session):
    """Test de carga masiva con archivo vacío"""
    csv_content = ""
    
    service = ProductService(db_session)
    
    with pytest.raises(ValueError) as exc_info:
        service.procesar_carga_masiva(csv_content, reject_on_errors=True)
    
    assert "El archivo CSV está vacío" in str(exc_info.value)

def test_convertir_fila_a_producto_valida(db_session):
    """Test de conversión de fila válida a producto"""
    fila = {
        'sku': 'MED1',
        'nombre_producto': 'Paracetamol 500mg',
        'proveedor_id': '1',
        'ficha_tecnica_url': 'https://ejemplo.com/ficha.pdf',
        'ca_temp': '2-8°C',
        'ca_humedad': '45-65%',
        'ca_luz': 'Protegido de luz',
        'ca_ventilacion': 'Ventilación normal',
        'ca_seguridad': 'Controlado',
        'ca_envase': 'Envase original',
        'org_tipo_medicamento': 'Analgésicos',
        'org_fecha_vencimiento': '2025-12-31',
        'valor_unitario_usd': '15.50',
        'certificaciones_sanitarias': '1;2;3'
    }
    
    service = ProductService(db_session)
    producto_data = service._convertir_fila_a_producto(fila)
    
    assert producto_data['sku'] == 'MED1'
    assert producto_data['nombre_producto'] == 'Paracetamol 500mg'
    assert producto_data['proveedor_id'] == 1
    assert producto_data['ficha_tecnica_url'] == 'https://ejemplo.com/ficha.pdf'
    assert producto_data['valor_unitario_usd'] == 15.50
    assert producto_data['certificaciones'] == [1, 2, 3]
    
    # Verificar condiciones
    assert producto_data['condiciones']['temperatura'] == '2-8°C'
    assert producto_data['condiciones']['humedad'] == '45-65%'
    
    # Verificar organización
    assert producto_data['organizacion']['tipo_medicamento'] == 'Analgésicos'
    assert producto_data['organizacion']['fecha_vencimiento'].year == 2025

def test_convertir_fila_a_producto_campos_obligatorios_vacios(db_session):
    """Test de conversión con campos obligatorios vacíos"""
    fila = {
        'sku': '',
        'nombre_producto': 'Paracetamol 500mg',
        'proveedor_id': '1',
        'valor_unitario_usd': '15.50'
    }
    
    service = ProductService(db_session)
    
    with pytest.raises(ValueError) as exc_info:
        service._convertir_fila_a_producto(fila)
    
    assert "Campo obligatorio 'sku' está vacío" in str(exc_info.value)

def test_convertir_fila_a_producto_fecha_invalida(db_session):
    """Test de conversión con fecha inválida"""
    fila = {
        'sku': 'MED1',
        'nombre_producto': 'Paracetamol 500mg',
        'proveedor_id': '1',
        'valor_unitario_usd': '15.50',
        'org_fecha_vencimiento': 'fecha-invalida'
    }
    
    service = ProductService(db_session)
    
    with pytest.raises(ValueError) as exc_info:
        service._convertir_fila_a_producto(fila)
    
    assert "Formato de fecha inválido" in str(exc_info.value)

def test_convertir_fila_a_producto_certificaciones_invalidas(db_session):
    """Test de conversión con certificaciones inválidas"""
    fila = {
        'sku': 'MED1',
        'nombre_producto': 'Paracetamol 500mg',
        'proveedor_id': '1',
        'valor_unitario_usd': '15.50',
        'certificaciones_sanitarias': 'abc;def'
    }
    
    service = ProductService(db_session)
    
    with pytest.raises(ValueError) as exc_info:
        service._convertir_fila_a_producto(fila)
    
    assert "Certificaciones deben ser números enteros" in str(exc_info.value)

def test_convertir_fila_a_producto_valor_unitario_invalido(db_session):
    """Test de conversión con valor unitario inválido"""
    fila = {
        'sku': 'MED1',
        'nombre_producto': 'Paracetamol 500mg',
        'proveedor_id': '1',
        'valor_unitario_usd': 'abc'
    }
    
    service = ProductService(db_session)
    
    with pytest.raises(ValueError) as exc_info:
        service._convertir_fila_a_producto(fila)
    
    assert "Valor unitario inválido" in str(exc_info.value)

def test_convertir_fila_a_producto_proveedor_id_invalido(db_session):
    """Test de conversión con proveedor_id inválido"""
    fila = {
        'sku': 'MED1',
        'nombre_producto': 'Paracetamol 500mg',
        'proveedor_id': 'abc',
        'valor_unitario_usd': '15.50'
    }
    
    service = ProductService(db_session)
    
    with pytest.raises(ValueError) as exc_info:
        service._convertir_fila_a_producto(fila)
    
    assert "ID de proveedor inválido" in str(exc_info.value)
