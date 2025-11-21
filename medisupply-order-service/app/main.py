from fastapi import FastAPI

app = FastAPI()

ORDERS = [
    {
        "id": 1,
        "nombre": "Orden 001",
        "fecha_entrega_estimada": "2025-11-20 14:00",
        "vehiculo_asignado": 12
    },
    {
        "id": 2,
        "nombre": "Orden 002",
        "fecha_entrega_estimada": "2025-11-22 09:30",
        "vehiculo_asignado": 8
    },
    {
        "id": 3,
        "nombre": "Orden 003",
        "fecha_entrega_estimada": "2025-11-25 12:15",
        "vehiculo_asignado": 15
    }
]

@app.get("/health")
async def health_check() :
    return {"status" : "ok"}

@app.get("/")
async def get_orders() :
    return ORDERS
