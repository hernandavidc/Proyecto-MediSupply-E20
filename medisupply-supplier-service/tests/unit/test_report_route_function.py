import pytest
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, Mock
from app.core.database import Base
from app.models.catalogs import Pais
from app.models.vendedor import Vendedor
from app.models.product import Producto
from app.models.plan_venta import PlanVenta
from app.api.v1.report_routes import consultar_reportes
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
def test_consultar_reportes_endpoint(mock_httpx_client):
    """Test: Endpoint consultar_reportes funciona correctamente con mocks"""
    db = setup_inmemory_db()
    try:
        # Setup: Crear datos de prueba
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
            nombre_producto='Producto Test',
            proveedor_id=1,
            valor_unitario_usd=75.0
        )
        db.add(producto)
        db.commit()
        
        plan = PlanVenta(
            vendedor_id=vendedor.id,
            periodo='Q4',
            anio=2025,
            pais=pais.id,
            productos_objetivo=[1],
            meta_monetaria_usd=15000.0,
            estado='ACTIVO'
        )
        db.add(plan)
        db.commit()
        
        # Mock: Configurar respuesta HTTP del order-service
        now = datetime.now()
        mock_ordenes = [
            {
                "id": 1,
                "id_vendedor": vendedor.id,
                "id_cliente": 1,
                "estado": "ENTREGADO",
                "fecha_creacion": (now - timedelta(days=3)).isoformat() + 'Z',
                "fecha_entrega_estimada": now.isoformat(),
                "productos": [
                    {"id_producto": producto.id, "cantidad": 30}
                ]
            }
        ]
        
        mock_response = create_mock_httpx_response(mock_ordenes)
        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=False)
        mock_client_instance.get = Mock(return_value=mock_response)
        mock_httpx_client.return_value = mock_client_instance
        
        # Test: Llamar al endpoint
        request = ReporteRequest(
            vendedor_id=None,
            pais=[pais.id],
            zona_geografica=[],
            periodo_tiempo='MES_ACTUAL',
            tipo_reporte=['DESEMPENO_VENDEDOR']
        )
        
        response = consultar_reportes(payload=request, db=db)
        
        # Assertions
        assert response is not None
        assert response.kpis is not None
        assert response.kpis.ventas_totales == 2250.0  # 30 * $75
        assert response.kpis.pedidos_mes == 1
        assert response.meta_objetivo_usd == 15000.0
        assert response.kpis.cumplimiento == 0.15  # 2250/15000
        assert response.kpis.tiempo_entrega_promedio_h == 72.0
        assert len(response.desempeno_vendedores) == 1
        assert response.desempeno_vendedores[0].vendedor == 'Juan Pérez'
        assert response.desempeno_vendedores[0].pais == 'COL'
        
    finally:
        db.close()


@patch('app.services.report_service.httpx.Client')
def test_consultar_reportes_filtro_por_vendedor(mock_httpx_client):
    """Test: Filtrar reporte por vendedor específico"""
    db = setup_inmemory_db()
    try:
        # Setup
        pais = Pais(id=1, nombre='México')
        db.add(pais)
        db.commit()
        
        v1 = Vendedor(id=1, nombre='Vendedor 1', email='v1@test.com', pais_id=1)
        v2 = Vendedor(id=2, nombre='Vendedor 2', email='v2@test.com', pais_id=1)
        db.add_all([v1, v2])
        db.commit()
        
        prod = Producto(id=1, sku='P1', nombre_producto='Prod 1', proveedor_id=1, valor_unitario_usd=50.0)
        db.add(prod)
        db.commit()
        
        plan = PlanVenta(vendedor_id=1, periodo='Q4', anio=2025, pais=1, productos_objetivo=[1], meta_monetaria_usd=3000.0, estado='ACTIVO')
        db.add(plan)
        db.commit()
        
        # Mock: Solo órdenes del vendedor 1
        now = datetime.now()
        mock_ordenes = [
            {
                "id": 1,
                "id_vendedor": 1,
                "id_cliente": 1,
                "estado": "ENTREGADO",
                "fecha_creacion": (now - timedelta(days=1)).isoformat() + 'Z',
                "fecha_entrega_estimada": now.isoformat(),
                "productos": [{"id_producto": 1, "cantidad": 15}]
            }
        ]
        
        mock_response = create_mock_httpx_response(mock_ordenes)
        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=False)
        mock_client_instance.get = Mock(return_value=mock_response)
        mock_httpx_client.return_value = mock_client_instance
        
        # Test: Filtrar por vendedor_id=1
        request = ReporteRequest(
            vendedor_id=1,
            pais=[],
            zona_geografica=[],
            periodo_tiempo='MES_ACTUAL',
            tipo_reporte=['DESEMPENO_VENDEDOR']
        )
        
        response = consultar_reportes(payload=request, db=db)
        
        # Assertions
        assert response.kpis.ventas_totales == 750.0  # 15 * $50
        assert response.kpis.pedidos_mes == 1
        assert len(response.desempeno_vendedores) == 1
        assert response.desempeno_vendedores[0].vendedor == 'Vendedor 1'
        
    finally:
        db.close()


@patch('app.services.report_service.httpx.Client')
def test_consultar_reportes_multiples_tipos(mock_httpx_client):
    """Test: Generar múltiples tipos de reportes simultáneamente"""
    db = setup_inmemory_db()
    try:
        # Setup
        pais = Pais(id=1, nombre='Perú')
        db.add(pais)
        db.commit()
        
        vendedor = Vendedor(id=1, nombre='Test Vendedor', email='test@test.com', pais_id=1)
        db.add(vendedor)
        db.commit()
        
        prod1 = Producto(id=1, sku='P1', nombre_producto='Producto A', proveedor_id=1, valor_unitario_usd=100.0, tipo_medicamento='Medicamentos')
        prod2 = Producto(id=2, sku='P2', nombre_producto='Producto B', proveedor_id=1, valor_unitario_usd=150.0, tipo_medicamento='Insumos Hospitalarios')
        db.add_all([prod1, prod2])
        db.commit()
        
        plan = PlanVenta(vendedor_id=1, periodo='Q4', anio=2025, pais=1, productos_objetivo=[1, 2], meta_monetaria_usd=10000.0, estado='ACTIVO')
        db.add(plan)
        db.commit()
        
        # Mock
        now = datetime.now()
        mock_ordenes = [
            {
                "id": 1,
                "id_vendedor": 1,
                "id_cliente": 1,
                "estado": "ENTREGADO",
                "fecha_creacion": (now - timedelta(days=2)).isoformat() + 'Z',
                "fecha_entrega_estimada": now.isoformat(),
                "productos": [
                    {"id_producto": 1, "cantidad": 10},
                    {"id_producto": 2, "cantidad": 5}
                ]
            }
        ]
        
        mock_response = create_mock_httpx_response(mock_ordenes)
        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=False)
        mock_client_instance.get = Mock(return_value=mock_response)
        mock_httpx_client.return_value = mock_client_instance
        
        # Test: Solicitar múltiples tipos de reporte
        request = ReporteRequest(
            vendedor_id=None,
            pais=[1],
            zona_geografica=[],
            periodo_tiempo='MES_ACTUAL',
            tipo_reporte=['DESEMPENO_VENDEDOR', 'VENTAS_POR_ZONA', 'VENTAS_POR_PRODUCTO']
        )
        
        response = consultar_reportes(payload=request, db=db)
        
        # Assertions
        assert response.kpis.ventas_totales == 1750.0  # (10*100) + (5*150)
        assert response.desempeno_vendedores is not None
        assert response.ventas_por_region is not None
        assert response.productos_por_categoria is not None
        assert len(response.ventas_por_region) >= 1
        assert len(response.productos_por_categoria) >= 1
        
    finally:
        db.close()


@patch('app.services.report_service.httpx.Client')
def test_consultar_reportes_validacion_filtros(mock_httpx_client):
    """Test: Verificar que la función valida correctamente los filtros"""
    db = setup_inmemory_db()
    try:
        pais = Pais(id=1, nombre='Ecuador')
        db.add(pais)
        db.commit()
        
        vendedor = Vendedor(id=1, nombre='Test', email='test@test.com', pais_id=1)
        db.add(vendedor)
        db.commit()
        
        # Mock vacío
        mock_response = create_mock_httpx_response([])
        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=False)
        mock_client_instance.get = Mock(return_value=mock_response)
        mock_httpx_client.return_value = mock_client_instance
        
        # Test: Request con filtros válidos
        request = ReporteRequest(
            vendedor_id=1,
            pais=[],
            zona_geografica=[],
            periodo_tiempo='MES_ACTUAL',
            tipo_reporte=['DESEMPENO_VENDEDOR']
        )
        
        response = consultar_reportes(payload=request, db=db)
        
        # Assertions: Debe ejecutarse sin errores
        assert response is not None
        assert response.filtros_aplicados is not None
        assert response.filtros_aplicados['vendedor_id'] == 1
        assert response.filtros_aplicados['periodo_tiempo'] == 'MES_ACTUAL'
        
    finally:
        db.close()
