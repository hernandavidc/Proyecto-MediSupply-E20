"""
Pruebas de carga y throughput con Locust
Simula usuarios concurrentes realizando operaciones en el sistema

Ejecutar:
    locust -f locustfile.py --host=https://medisupply-edge-proxy-n5jhaxtfma-uc.a.run.app

O con headless mode:
    locust -f locustfile.py --host=https://medisupply-edge-proxy-n5jhaxtfma-uc.a.run.app \
           --users 10 --spawn-rate 2 --run-time 1m --headless

SLA objetivo: 100-400 pedidos/min
"""
from locust import HttpUser, task, between, events
from faker import Faker
import random
import json

fake = Faker()


class MediSupplyUser(HttpUser):
    """
    Simula un usuario del sistema MediSupply
    """
    wait_time = between(1, 3)  # Espera entre 1-3 segundos entre tareas
    
    def on_start(self):
        """
        Se ejecuta al inicio de cada usuario simulado
        Obtiene un token de autenticación
        """
        self.login()
    
    def login(self):
        """Autenticación del usuario"""
        response = self.client.post("/api/v1/users/generate-token", json={
            "email": "admin@medisupply.com",
            "password": "password123"
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
        else:
            print(f"Login failed: {response.status_code}")
            self.token = None
            self.headers = {}
    
    @task(3)
    def list_productos(self):
        """Listar productos (tarea común)"""
        if not self.token:
            return
        
        self.client.get(
            "/api/v1/productos",
            headers=self.headers,
            params={"limit": 50},
            name="/api/v1/productos [LIST]"
        )
    
    @task(2)
    def list_clientes(self):
        """Listar clientes"""
        if not self.token:
            return
        
        self.client.get(
            "/api/v1/clientes/",
            headers=self.headers,
            params={"limit": 50},
            name="/api/v1/clientes [LIST]"
        )
    
    @task(2)
    def list_ordenes(self):
        """Listar órdenes"""
        if not self.token:
            return
        
        self.client.get(
            "/api/v1/ordenes",
            headers=self.headers,
            params={"limit": 50},
            name="/api/v1/ordenes [LIST]"
        )
    
    @task(1)
    def list_vendedores(self):
        """Listar vendedores"""
        if not self.token:
            return
        
        self.client.get(
            "/api/v1/vendedores",
            headers=self.headers,
            name="/api/v1/vendedores [LIST]"
        )
    
    @task(1)
    def list_bodegas(self):
        """Listar bodegas (localización)"""
        if not self.token:
            return
        
        self.client.get(
            "/api/v1/bodegas",
            headers=self.headers,
            name="/api/v1/bodegas [LOCALIZATION]"
        )
    
    @task(1)
    def list_vehiculos(self):
        """Listar vehículos (localización)"""
        if not self.token:
            return
        
        self.client.get(
            "/api/v1/vehiculos",
            headers=self.headers,
            name="/api/v1/vehiculos [LOCALIZATION]"
        )


class OrderCreationUser(HttpUser):
    """
    Usuario especializado en crear órdenes
    Para medir throughput de 100-400 pedidos/min
    """
    wait_time = between(0.5, 1)  # Más agresivo para generar carga
    
    def on_start(self):
        """Autenticación"""
        self.login()
        self.load_initial_data()
    
    def login(self):
        """Autenticación del usuario"""
        response = self.client.post("/api/v1/users/generate-token", json={
            "email": "admin@medisupply.com",
            "password": "password123"
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
        else:
            self.token = None
            self.headers = {}
    
    def load_initial_data(self):
        """Carga IDs necesarios para crear órdenes"""
        if not self.token:
            return
        
        # Obtener IDs de clientes
        response = self.client.get(
            "/api/v1/clientes/",
            headers=self.headers,
            params={"limit": 10}
        )
        if response.status_code == 200:
            clientes = response.json()
            self.cliente_ids = [c.get("id") for c in clientes if c.get("id")]
        else:
            self.cliente_ids = []
        
        # Obtener IDs de vehículos
        response = self.client.get(
            "/api/v1/vehiculos",
            headers=self.headers,
            params={"limit": 10}
        )
        if response.status_code == 200:
            vehiculos = response.json()
            self.vehiculo_ids = [v.get("id") for v in vehiculos if v.get("id")]
        else:
            self.vehiculo_ids = []
    
    @task(10)
    def create_orden(self):
        """
        Crear una orden (tarea principal)
        SLA: 100-400 órdenes/min
        """
        if not self.token or not self.cliente_ids or not self.vehiculo_ids:
            return
        
        payload = {
            "fecha_entrega_estimada": "2025-12-31T23:59:59",
            "id_vehiculo": random.choice(self.vehiculo_ids),
            "id_cliente": random.choice(self.cliente_ids),
            "id_vendedor": 1,
            "estado": "ABIERTO"
        }
        
        with self.client.post(
            "/api/v1/ordenes",
            headers=self.headers,
            json=payload,
            name="/api/v1/ordenes [CREATE]",
            catch_response=True
        ) as response:
            if response.status_code == 201:
                response.success()
            else:
                response.failure(f"Failed to create order: {response.status_code}")


# Eventos para medir SLAs
orders_created = 0
test_start_time = None


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Se ejecuta al inicio del test"""
    global test_start_time, orders_created
    import time
    test_start_time = time.time()
    orders_created = 0
    print("\n🚀 Iniciando pruebas de carga...")
    print(f"📊 SLA objetivo: 100-400 órdenes/minuto\n")


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Se ejecuta después de cada request"""
    global orders_created
    
    # Contar órdenes creadas exitosamente
    if name == "/api/v1/ordenes [CREATE]" and not exception:
        orders_created += 1


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Se ejecuta al final del test - calcula throughput"""
    global test_start_time, orders_created
    import time
    
    if test_start_time:
        elapsed_time = time.time() - test_start_time
        elapsed_minutes = elapsed_time / 60.0
        
        if elapsed_minutes > 0:
            orders_per_minute = orders_created / elapsed_minutes
            
            print("\n" + "="*70)
            print("📊 RESULTADOS DE PERFORMANCE")
            print("="*70)
            print(f"⏱️  Tiempo de ejecución: {elapsed_time:.2f}s ({elapsed_minutes:.2f} min)")
            print(f"📦 Órdenes creadas: {orders_created}")
            print(f"🚀 Throughput: {orders_per_minute:.2f} órdenes/minuto")
            print("-"*70)
            
            # Validar SLA
            if 100 <= orders_per_minute <= 400:
                print(f"✅ SLA CUMPLIDO: {orders_per_minute:.2f} está dentro del rango 100-400 órdenes/min")
            elif orders_per_minute > 400:
                print(f"✅ SLA SUPERADO: {orders_per_minute:.2f} excede el objetivo máximo de 400 órdenes/min")
            else:
                print(f"❌ SLA NO CUMPLIDO: {orders_per_minute:.2f} está por debajo del mínimo de 100 órdenes/min")
            
            print("="*70 + "\n")

