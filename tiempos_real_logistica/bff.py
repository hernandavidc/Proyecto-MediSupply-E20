# bff.py
import asyncio, json, time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import redis.asyncio as redis
from prometheus_client import Counter, Summary, start_http_server
import httpx

# Configuración
REDIS_URL = "redis://localhost:6379"
REDIS_CHANNEL = "gps_updates"
ROUTE_ENGINE_URL = "http://localhost:8100/route"

# Métricas
start_http_server(8001)
GPS_MSG_COUNTER = Counter('bff_gps_messages_total', 'Mensajes GPS recibidos por BFF')
GPS_DELIVERY_LATENCY = Summary('bff_delivery_latency_seconds', 'Latencia de entrega a clientes')

app = FastAPI()

clients = set()

async def redis_subscribe_loop():
    r = redis.from_url(REDIS_URL)
    pubsub = r.pubsub()
    await pubsub.subscribe(REDIS_CHANNEL)
    async for message in pubsub.listen():
        if message['type'] == 'message':
            payload = json.loads(message['data'])
            GPS_MSG_COUNTER.inc()
            latency = time.time() - payload.get("ts_publish", time.time())
            GPS_DELIVERY_LATENCY.observe(latency)
            await broadcast_to_clients(payload)

async def broadcast_to_clients(data):
    """Envía actualización a todos los clientes conectados"""
    for ws in list(clients):
        try:
            await ws.send_text(json.dumps(data))
        except:
            clients.discard(ws)

@app.websocket("/ws/client")
async def client_ws(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # keep-alive
    except WebSocketDisconnect:
        clients.discard(websocket)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(redis_subscribe_loop())

@app.get("/route-test")
async def route_test():
    """Probar cálculo de ruta desde el BFF"""
    payload = {
        "origin": [4.648, -74.088],
        "destination": [4.7, -74.05],
        "waypoints": []
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(ROUTE_ENGINE_URL, json=payload)
        return resp.json()
