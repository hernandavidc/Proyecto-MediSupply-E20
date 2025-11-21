from fastapi import FastAPI

app = FastAPI()

prefix = '/api/v1/orders'

ORDERS = [
    {
        "id": 1,
        "nombre": "Orden 001",
        "fecha_entrega_estimada": "2025-11-20 14:00",
        "vehiculo_asignado": 12,
        "cliente" : 2,
        "estado" : "RECIBIDO"
    },
    {
        "id": 2,
        "nombre": "Orden 002",
        "fecha_entrega_estimada": "2025-11-22 09:30",
        "vehiculo_asignado": 8,
        "cliente": 4,
        "estado": "EN_PREPARACION"
    },
    {
        "id": 3,
        "nombre": "Orden 003",
        "fecha_entrega_estimada": "2025-11-25 12:15",
        "vehiculo_asignado": 15,
        "cliente": 6,
        "estado": "EN_TRANSITO"
    }
]

@app.get("/health")
async def health_check() :
    return {"status" : "ok"}

@app.get(prefix + "/")
async def get_orders() :
    return ORDERS

@app.get(prefix + "/{client_id}/order")
async def get_orders_by_client(client_id) :
    order = None

    for o in ORDERS :
        client = o.get('cliente')

        if client == int(client_id) :
            order = o

    return {"order" : order}
