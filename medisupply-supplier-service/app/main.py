from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import proveedor_routes, producto_routes, catalog_routes, plan_routes, vendedor_routes , report_routes
from app.core.seed_data import seed_data
from app.core.config import settings
from app.core.database import Base, engine



app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Microservicio de proveedores - MediSupply",
    version=settings.VERSION,
    debug=settings.DEBUG,
    docs_url="/supplier-docs",
    redoc_url="/supplier-redoc",
    openapi_url="/supplier-openapi.json"
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
app.include_router(report_routes.router)

@app.get("/")
def root():
    return {
        "message": "MediSupply Supplier Service",
        "version": settings.VERSION,
        "docs": "/supplier-docs",
        "health": "/healthz"
    }

@app.get('/healthz')
def healthz():
    return {"status": "ok"}



@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    seed_data()

