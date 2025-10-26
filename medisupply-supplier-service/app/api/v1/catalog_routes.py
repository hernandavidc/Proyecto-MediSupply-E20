from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.catalogs import Pais, Certificacion, CategoriaSuministro
from app.api.v1 import proveedor_routes
from app.schemas.catalogs_schema import PaisOut, CertificacionOut, CategoriaOut

router = APIRouter(prefix="/api/v1", tags=["Catalogs"])


@router.get("/paises", response_model=list[PaisOut])
def get_paises(db: Session = Depends(get_db)):
    return db.query(Pais).all()


@router.get("/certificaciones", response_model=list[CertificacionOut])
def get_certificaciones(db: Session = Depends(get_db)):
    return db.query(Certificacion).all()


@router.get("/categorias-suministros", response_model=list[CategoriaOut])
def get_categorias(db: Session = Depends(get_db)):
    return db.query(CategoriaSuministro).all()
