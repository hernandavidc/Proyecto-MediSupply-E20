from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import (
    proveedor_routes,
    producto_routes,
    catalog_routes,
    plan_routes,
    vendedor_routes,
)
from app.core.database import create_tables
from app.core.config import settings

# Crear las tablas en la base de datos al iniciar (mismo patrón que user-service)
create_tables()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Microservicio de proveedores - MediSupply",
    version=settings.VERSION,
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(proveedor_routes.router)
app.include_router(producto_routes.router)
app.include_router(catalog_routes.router)
app.include_router(plan_routes.router)
app.include_router(vendedor_routes.router)


@app.get("/")
def root():
    return {"message": "medisupply-supplier-service", "version": settings.VERSION}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
