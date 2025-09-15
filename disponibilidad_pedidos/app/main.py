from fastapi import FastAPI
from .routes import router as pedidos_router

app = FastAPI(title="Servicio Pedidos", version="1.0")

app.include_router(pedidos_router, prefix="/api", tags=["Pedidos"])

@app.get("/health")
def health_check():
    return {"status": "OK"}