# route_engine.py
import math, random, time, asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import Summary, Counter, start_http_server

# Métricas Prometheus
REQUEST_LATENCY = Summary('route_compute_seconds', 'Tiempo de cálculo de rutas (s)')
REQUEST_COUNT = Counter('route_requests_total', 'Total de solicitudes de ruta')

app = FastAPI()

# Servidor de métricas en puerto 8002
start_http_server(8002)

class RouteRequest(BaseModel):
    origin: tuple
    destination: tuple
    waypoints: list = None

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

@app.post("/route")
async def compute_route(req: RouteRequest):
    REQUEST_COUNT.inc()
    t0 = time.time()

    # Simular cálculo de ruta
    dist = haversine(req.origin[0], req.origin[1], req.destination[0], req.destination[1])
    wp = len(req.waypoints) if req.waypoints else 0
    base = 0.15 + 0.05 * wp
    jitter = random.uniform(0, 0.4)
    heavy = random.uniform(0.5, 1.2) if random.random() < 0.05 else 0.0
    compute_time = base + jitter + heavy
    await asyncio.sleep(compute_time)

    eta = dist / 11.11 if dist > 0 else 0
    elapsed = time.time() - t0
    REQUEST_LATENCY.observe(elapsed)

    return {"distance_m": dist, "eta_s": eta, "compute_time_s": compute_time}
