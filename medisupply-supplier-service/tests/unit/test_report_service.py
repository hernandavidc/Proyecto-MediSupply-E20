import pytest
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock, Mock
from app.core.database import Base
from app.models.catalogs import Pais
from app.models.vendedor import Vendedor
from app.models.product import Producto
from app.models.plan_venta import PlanVenta
from app.services.report_service import ReportService
from app.schemas.report_schema import ReporteRequest


def setup_inmemory_db():
    """Configura una base de datos SQLite en memoria para pruebas"""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


def create_mock_httpx_response(ordenes_data):
    """Crea un mock de respuesta HTTP con los datos de órdenes"""
    mock_response = Mock()
    mock_response.json.return_value = ordenes_data
    mock_response.raise_for_status = Mock()
    return mock_response


@patch('app.services.report_service.httpx.Client')
def test_calcular_valor_orden(mock_httpx_client):
    """Test: Calcula correctamente el valor total de una orden basándose en productos"""
    db = setup_inmemory_db()
    try:
        # Setup: Crear producto
        prod = Producto(
            id=1,
            sku='TEST-001',
            nombre_producto='Producto Test',
            proveedor_id=1,
            valor_unitario_usd=100.0
        )
        db.add(prod)
        db.commit()
        db.refresh(prod)
        
        # Crear servicio
        svc = ReportService(db)
        
        # Test: Orden con 10 unidades del producto
        orden = {
            "id": 1,
            "id_vendedor": 1,
            "id_cliente": 1,
            "productos": [
                {"id_producto": prod.id, "cantidad": 10}
            ]
        }
        
        valor = svc._calcular_valor_orden(orden)
        
        # Assert: 10 * $100 = $1000
        assert valor == 1000.0
        
    finally:
        db.close()


@patch('app.services.report_service.httpx.Client')
def test_calcular_tiempo_entrega_promedio(mock_httpx_client):
    """Test: Calcula correctamente el tiempo promedio de entrega en horas"""
    db = setup_inmemory_db()
    try:
        svc = ReportService(db)
        
        now = datetime.now()
        ordenes = [
            {
                "id": 1,
                "fecha_creacion": (now - timedelta(days=2)).isoformat() + 'Z',
                "fecha_entrega_estimada": now.isoformat()
            },
            {
                "id": 2,
                "fecha_creacion": (now - timedelta(days=1)).isoformat() + 'Z',
                "fecha_entrega_estimada": now.isoformat()
            }
        ]
        
        tiempo = svc._calcular_tiempo_entrega_promedio(ordenes)
        
        # Assert: Promedio de 48h y 24h = 36h
        assert tiempo == 36.0
        
    finally:
        db.close()


@patch('app.services.report_service.httpx.Client')
def test_generar_reportes_con_mock_http(mock_httpx_client):
    """Test: Genera reportes correctamente usando mock de HTTP"""
    db = setup_inmemory_db()
    try:
        # Setup: Crear datos en BD
        pais = Pais(id=1, nombre='Colombia')
        db.add(pais)
        db.commit()
        
        vendedor = Vendedor(
            id=1,
            nombre='Juan Pérez',
            email='juan@example.com',
            pais_id=pais.id
        )
        db.add(vendedor)
        db.commit()
        
        producto = Producto(
            id=1,
            sku='PROD-001',
            nombre_producto='Producto 1',
            proveedor_id=1,
            valor_unitario_usd=50.0
        )
        db.add(producto)
        db.commit()
        
        plan = PlanVenta(
            vendedor_id=vendedor.id,
            periodo='Q4',
            anio=2025,
            pais=pais.id,
            productos_objetivo=[1],
            meta_monetaria_usd=10000.0,
            estado='ACTIVO'
        )
        db.add(plan)
        db.commit()
        
        # Mock: Configurar respuesta HTTP
        now = datetime.now()
        mock_ordenes = [
            {
                "id": 1,
                "id_vendedor": vendedor.id,
                "id_cliente": 1,
                "estado": "ENTREGADO",
                "fecha_creacion": (now - timedelta(days=2)).isoformat() + 'Z',
                "fecha_entrega_estimada": now.isoformat(),
                "productos": [
                    {"id_producto": producto.id, "cantidad": 20}
                ]
            }
        ]
        
        mock_response = create_mock_httpx_response(mock_ordenes)
        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=False)
        mock_client_instance.get = Mock(return_value=mock_response)
        mock_httpx_client.return_value = mock_client_instance
        
        # Test: Generar reporte
        svc = ReportService(db)
        req = ReporteRequest(
            vendedor_id=None,
            pais=[pais.id],
            zona_geografica=[],
            periodo_tiempo='MES_ACTUAL',
            tipo_reporte=['DESEMPENO_VENDEDOR']
        )
        
        resp = svc.generar_reportes(req)
        
        # Assertions
        assert resp is not None
        assert resp.kpis is not None
        assert resp.kpis.ventas_totales == 1000.0  # 20 * $50
        assert resp.kpis.pedidos_mes == 1
        assert resp.meta_objetivo_usd == 10000.0
        assert resp.kpis.cumplimiento == 0.1  # 1000/10000
        assert resp.kpis.tiempo_entrega_promedio_h == 48.0
        assert len(resp.desempeno_vendedores) == 1
        assert resp.desempeno_vendedores[0].vendedor == 'Juan Pérez'
        assert resp.desempeno_vendedores[0].ventas_usd == 1000.0
        
    finally:
        db.close()


@patch('app.services.report_service.httpx.Client')
def test_reporte_con_multiples_vendedores(mock_httpx_client):
    """Test: Reporte con múltiples vendedores y productos"""
    db = setup_inmemory_db()
    try:
        # Setup: Crear múltiples países y vendedores
        pais1 = Pais(id=1, nombre='Colombia')
        pais2 = Pais(id=2, nombre='México')
        db.add_all([pais1, pais2])
        db.commit()
        
        v1 = Vendedor(id=1, nombre='Vendedor 1', email='v1@test.com', pais_id=1)
        v2 = Vendedor(id=2, nombre='Vendedor 2', email='v2@test.com', pais_id=2)
        db.add_all([v1, v2])
        db.commit()
        
        prod1 = Producto(id=1, sku='P1', nombre_producto='Prod 1', proveedor_id=1, valor_unitario_usd=100.0)
        prod2 = Producto(id=2, sku='P2', nombre_producto='Prod 2', proveedor_id=1, valor_unitario_usd=200.0)
        db.add_all([prod1, prod2])
        db.commit()
        
        plan1 = PlanVenta(vendedor_id=1, periodo='Q4', anio=2025, pais=1, productos_objetivo=[1], meta_monetaria_usd=5000.0, estado='ACTIVO')
        plan2 = PlanVenta(vendedor_id=2, periodo='Q4', anio=2025, pais=2, productos_objetivo=[2], meta_monetaria_usd=8000.0, estado='ACTIVO')
        db.add_all([plan1, plan2])
        db.commit()
        
        # Mock: Órdenes de ambos vendedores
        now = datetime.now()
        mock_ordenes = [
            {
                "id": 1,
                "id_vendedor": 1,
                "id_cliente": 1,
                "estado": "ENTREGADO",
                "fecha_creacion": (now - timedelta(days=1)).isoformat() + 'Z',
                "fecha_entrega_estimada": now.isoformat(),
                "productos": [{"id_producto": 1, "cantidad": 10}]
            },
            {
                "id": 2,
                "id_vendedor": 2,
                "id_cliente": 2,
                "estado": "ENTREGADO",
                "fecha_creacion": (now - timedelta(days=2)).isoformat() + 'Z',
                "fecha_entrega_estimada": now.isoformat(),
                "productos": [{"id_producto": 2, "cantidad": 15}]
            }
        ]
        
        mock_response = create_mock_httpx_response(mock_ordenes)
        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=False)
        mock_client_instance.get = Mock(return_value=mock_response)
        mock_httpx_client.return_value = mock_client_instance
        
        # Test
        svc = ReportService(db)
        req = ReporteRequest(
            vendedor_id=None,
            pais=[1, 2],
            zona_geografica=[],
            periodo_tiempo='MES_ACTUAL',
            tipo_reporte=['DESEMPENO_VENDEDOR', 'VENTAS_POR_ZONA']
        )
        
        resp = svc.generar_reportes(req)
        
        # Assertions
        assert resp.kpis.ventas_totales == 4000.0  # (10*100) + (15*200)
        assert resp.kpis.pedidos_mes == 2
        assert resp.meta_objetivo_usd == 13000.0  # 5000 + 8000
        assert len(resp.desempeno_vendedores) == 2
        assert len(resp.ventas_por_region) == 2
        
    finally:
        db.close()


@patch('app.services.report_service.httpx.Client')
def test_reporte_sin_ordenes(mock_httpx_client):
    """Test: Reporte cuando no hay órdenes devuelve valores en cero"""
    db = setup_inmemory_db()
    try:
        pais = Pais(id=1, nombre='Colombia')
        db.add(pais)
        db.commit()
        
        vendedor = Vendedor(id=1, nombre='Test', email='test@test.com', pais_id=1)
        db.add(vendedor)
        db.commit()
        
        plan = PlanVenta(vendedor_id=1, periodo='Q4', anio=2025, pais=1, productos_objetivo=[1], meta_monetaria_usd=5000.0, estado='ACTIVO')
        db.add(plan)
        db.commit()
        
        # Mock: Sin órdenes
        mock_response = create_mock_httpx_response([])
        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=False)
        mock_client_instance.get = Mock(return_value=mock_response)
        mock_httpx_client.return_value = mock_client_instance
        
        # Test
        svc = ReportService(db)
        req = ReporteRequest(
            vendedor_id=None,
            pais=[1],
            zona_geografica=[],
            periodo_tiempo='MES_ACTUAL',
            tipo_reporte=['DESEMPENO_VENDEDOR']
        )
        
        resp = svc.generar_reportes(req)
        
        # Assertions
        assert resp.kpis.ventas_totales == 0.0
        assert resp.kpis.pedidos_mes == 0
        assert resp.kpis.cumplimiento == 0.0
        assert resp.meta_objetivo_usd == 5000.0
        
    finally:
        db.close()


@patch('app.services.report_service.httpx.Client')
def test_meta_default_cuando_no_hay_planes(mock_httpx_client):
    """Test: Meta por defecto de 100000 cuando no hay planes de venta"""
    db = setup_inmemory_db()
    try:
        pais = Pais(id=1, nombre='Colombia')
        db.add(pais)
        db.commit()
        
        vendedor = Vendedor(id=1, nombre='Test', email='test@test.com', pais_id=1)
        db.add(vendedor)
        db.commit()
        
        # Mock: Sin órdenes
        mock_response = create_mock_httpx_response([])
        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=False)
        mock_client_instance.get = Mock(return_value=mock_response)
        mock_httpx_client.return_value = mock_client_instance
        
        # Test
        svc = ReportService(db)
        req = ReporteRequest(
            vendedor_id=None,
            pais=[1],
            zona_geografica=[],
            periodo_tiempo='MES_ACTUAL',
            tipo_reporte=['DESEMPENO_VENDEDOR']
        )
        
        resp = svc.generar_reportes(req)
        
        # Assertions: Meta por defecto
        assert resp.meta_objetivo_usd == 100000.0
        
    finally:
        db.close()