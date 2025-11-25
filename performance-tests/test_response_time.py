"""
Pruebas de tiempo de respuesta individual de endpoints críticos
Usando pytest-benchmark para medir performance

SLAs a validar:
- Localización ≤1s
- Rutas ≤3s
- Endpoints generales ≤2s
"""
import pytest
import httpx
from config import (
    EDGE_PROXY_URL, 
    LOCALIZATION_THRESHOLD, 
    ROUTE_OPTIMIZATION_THRESHOLD
)


class TestAuthenticationPerformance:
    """Tests de performance para autenticación"""
    
    def test_login_performance(self, benchmark):
        """
        Test: Login debe responder en tiempo razonable
        SLA: ≤2s
        """
        def do_login():
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{EDGE_PROXY_URL}/api/v1/users/generate-token",
                    json={
                        "email": "admin@medisupply.com",
                        "password": "password123"
                    }
                )
                response.raise_for_status()
                return response
        
        result = benchmark(do_login)
        assert result.status_code == 200
        
        # Validar SLA
        stats = benchmark.stats.stats
        assert stats.mean < 2.0, f"Login promedio: {stats.mean:.3f}s, esperado: <2s"


class TestSupplierServicePerformance:
    """Tests de performance para supplier-service"""
    
    def test_list_productos_performance(self, benchmark, http_client, auth_headers):
        """
        Test: Listar productos debe responder rápido
        SLA: ≤2s
        """
        def list_productos():
            response = http_client.get(
                f"{EDGE_PROXY_URL}/api/v1/productos",
                headers=auth_headers,
                params={"limit": 100}
            )
            response.raise_for_status()
            return response
        
        result = benchmark(list_productos)
        assert result.status_code == 200
        
        # Validar SLA
        stats = benchmark.stats.stats
        assert stats.mean < 2.0, f"Listar productos promedio: {stats.mean:.3f}s, esperado: <2s"
    
    def test_list_vendedores_performance(self, benchmark, http_client, auth_headers):
        """
        Test: Listar vendedores debe responder rápido
        SLA: ≤2s
        """
        def list_vendedores():
            response = http_client.get(
                f"{EDGE_PROXY_URL}/api/v1/vendedores",
                headers=auth_headers
            )
            response.raise_for_status()
            return response
        
        result = benchmark(list_vendedores)
        assert result.status_code == 200
        
        # Validar SLA
        stats = benchmark.stats.stats
        assert stats.mean < 2.0, f"Listar vendedores promedio: {stats.mean:.3f}s, esperado: <2s"
    
    @pytest.mark.skip(reason="Requiere vendedor con visitas programadas")
    def test_route_optimization_performance(self, benchmark, http_client, auth_headers, vendedor_id):
        """
        Test: Optimización de rutas debe responder en ≤3s
        SLA: ≤3s (crítico para vendedores en campo)
        """
        def get_route():
            response = http_client.get(
                f"{EDGE_PROXY_URL}/api/v1/rutas-visitas/{vendedor_id}",
                headers=auth_headers
            )
            response.raise_for_status()
            return response
        
        result = benchmark(get_route)
        assert result.status_code == 200
        
        # Validar SLA crítico
        stats = benchmark.stats.stats
        assert stats.mean < ROUTE_OPTIMIZATION_THRESHOLD, \
            f"Optimización de rutas promedio: {stats.mean:.3f}s, SLA: ≤{ROUTE_OPTIMIZATION_THRESHOLD}s"
        assert stats.max < ROUTE_OPTIMIZATION_THRESHOLD * 1.5, \
            f"Tiempo máximo: {stats.max:.3f}s excede 1.5x SLA"


class TestOrderServicePerformance:
    """Tests de performance para order-service"""
    
    def test_list_ordenes_performance(self, benchmark, http_client, auth_headers):
        """
        Test: Listar órdenes debe responder rápido
        SLA: ≤2s
        """
        def list_ordenes():
            response = http_client.get(
                f"{EDGE_PROXY_URL}/api/v1/ordenes",
                headers=auth_headers,
                params={"limit": 100}
            )
            response.raise_for_status()
            return response
        
        result = benchmark(list_ordenes)
        assert result.status_code == 200
        
        # Validar SLA
        stats = benchmark.stats.stats
        assert stats.mean < 2.0, f"Listar órdenes promedio: {stats.mean:.3f}s, esperado: <2s"
    
    def test_list_bodegas_performance(self, benchmark, http_client, auth_headers):
        """
        Test: Listar bodegas debe responder rápido (para localización)
        SLA: ≤1s (localización debe ser instantánea)
        """
        def list_bodegas():
            response = http_client.get(
                f"{EDGE_PROXY_URL}/api/v1/bodegas",
                headers=auth_headers
            )
            response.raise_for_status()
            return response
        
        result = benchmark(list_bodegas)
        assert result.status_code == 200
        
        # Validar SLA de localización
        stats = benchmark.stats.stats
        assert stats.mean < LOCALIZATION_THRESHOLD, \
            f"Localización bodegas promedio: {stats.mean:.3f}s, SLA: ≤{LOCALIZATION_THRESHOLD}s"
    
    def test_list_vehiculos_performance(self, benchmark, http_client, auth_headers):
        """
        Test: Listar vehículos con localización debe ser rápido
        SLA: ≤1s (localización debe ser instantánea)
        """
        def list_vehiculos():
            response = http_client.get(
                f"{EDGE_PROXY_URL}/api/v1/vehiculos",
                headers=auth_headers
            )
            response.raise_for_status()
            return response
        
        result = benchmark(list_vehiculos)
        assert result.status_code == 200
        
        # Validar SLA de localización
        stats = benchmark.stats.stats
        assert stats.mean < LOCALIZATION_THRESHOLD, \
            f"Localización vehículos promedio: {stats.mean:.3f}s, SLA: ≤{LOCALIZATION_THRESHOLD}s"


class TestClientServicePerformance:
    """Tests de performance para client-service"""
    
    def test_list_clientes_performance(self, benchmark, http_client, auth_headers):
        """
        Test: Listar clientes debe responder rápido
        SLA: ≤2s
        """
        def list_clientes():
            response = http_client.get(
                f"{EDGE_PROXY_URL}/api/v1/clientes/",
                headers=auth_headers,
                params={"limit": 100}
            )
            response.raise_for_status()
            return response
        
        result = benchmark(list_clientes)
        assert result.status_code == 200
        
        # Validar SLA
        stats = benchmark.stats.stats
        assert stats.mean < 2.0, f"Listar clientes promedio: {stats.mean:.3f}s, esperado: <2s"


class TestReportPerformance:
    """Tests de performance para reportes"""
    
    @pytest.mark.skip(reason="Reportes pueden tardar más dependiendo del volumen de datos")
    def test_generar_reporte_performance(self, benchmark, http_client, auth_headers):
        """
        Test: Generar reporte debe completarse en tiempo razonable
        SLA: ≤5s (reportes pueden ser más lentos pero no excesivos)
        """
        def generate_report():
            response = http_client.post(
                f"{EDGE_PROXY_URL}/api/v1/reportes/",
                headers=auth_headers,
                json={
                    "vendedor_id": None,
                    "pais": [1],
                    "zona_geografica": [],
                    "periodo_tiempo": "MES_ACTUAL",
                    "tipo_reporte": ["DESEMPENO_VENDEDOR"]
                }
            )
            response.raise_for_status()
            return response
        
        result = benchmark(generate_report)
        assert result.status_code == 200
        
        # Validar SLA para reportes
        stats = benchmark.stats.stats
        assert stats.mean < 5.0, f"Generar reporte promedio: {stats.mean:.3f}s, esperado: <5s"

