from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1 import proveedor_routes, producto_routes, catalog_routes, plan_routes, vendedor_routes, report_routes
from app.core.seed_data import seed_data
from app.core.config import settings
from app.core.database import Base, engine
from app.core.auth import require_auth
from app.core.dependencies import get_current_user



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

app.include_router(proveedor_routes.router, dependencies=[Depends(get_current_user)])
app.include_router(producto_routes.router, dependencies=[Depends(get_current_user)])
app.include_router(catalog_routes.router, dependencies=[Depends(get_current_user)])
app.include_router(plan_routes.router, dependencies=[Depends(get_current_user)])
app.include_router(vendedor_routes.router, dependencies=[Depends(get_current_user)])
app.include_router(report_routes.router, dependencies=[Depends(get_current_user)])


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Middleware global que valida el token en Authorization: Bearer <token>

    Exime rutas públicas como health y la documentación.
    Si el token es válido, añade `request.state.user` con el JSON del usuario.
    """
    path = request.url.path
    # Rutas públicas que no requieren autenticación
    exempt_prefixes = [
        '/',
        '/healthz',
        '/supplier-docs',
        '/supplier-redoc',
        '/supplier-openapi.json',
        '/supplier-openapi',
    ]
    if any(path == p or path.startswith(p + '/') for p in exempt_prefixes):
        return await call_next(request)

    try:
        user_json = require_auth(request)
        # attach user info to the request so endpoints can use it if needed
        request.state.user = user_json
    except HTTPException as exc:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return await call_next(request)

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

