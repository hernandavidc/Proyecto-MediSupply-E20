from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.report_schema import ReporteRequest, ReporteResponse
from app.services.report_service import ReportService

router = APIRouter(prefix="/reportes", tags=["Reportes"])

@router.post("/", response_model=ReporteResponse, summary="Consultar reportes de vendedores")
def consultar_reportes(payload: ReporteRequest, db: Session = Depends(get_db)):
    service = ReportService(db)
    return service.generar_reportes(payload)
