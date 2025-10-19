from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.vendedor import Vendedor, VendedorAuditoria
from app.models.plan_venta import PlanVenta
import json

class VendedorService:
    def __init__(self, db: Session):
        self.db = db

    def crear_vendedor(self, data: Dict[str, Any], usuario_id: Optional[int] = None) -> Vendedor:
        # validar email único
        existing = self.db.query(Vendedor).filter(Vendedor.email == data.get('email')).first()
        if existing:
            raise ValueError('Email ya registrado')
        vendedor = Vendedor(
            nombre=data.get('nombre'),
            email=data.get('email'),
            pais=data.get('pais'),
            estado=data.get('estado') or 'ACTIVO',
            created_by=usuario_id
        )
        try:
            self.db.add(vendedor)
            self.db.flush()
            audit = VendedorAuditoria(
                vendedor_id=vendedor.id,
                operacion='CREATE',
                usuario_id=usuario_id,
                datos_nuevos=json.dumps({'nombre': vendedor.nombre, 'email': vendedor.email})
            )
            self.db.add(audit)
            self.db.commit()
            self.db.refresh(vendedor)
            return vendedor
        except IntegrityError:
            self.db.rollback()
            raise

    def listar_vendedores(self, skip: int = 0, limit: int = 100) -> List[Vendedor]:
        return self.db.query(Vendedor).offset(skip).limit(limit).all()

    def obtener_vendedor(self, vendedor_id: int) -> Optional[Vendedor]:
        return self.db.query(Vendedor).filter(Vendedor.id == vendedor_id).first()

    def eliminar_vendedor(self, vendedor: Vendedor) -> None:
        # regla: no permitir eliminar si tiene planes de venta asociados
        has_plans = self.db.query(PlanVenta).filter(PlanVenta.vendedor_id == vendedor.id).first()
        if has_plans:
            raise ValueError('No se puede eliminar vendedor con planes asociados')
        antes = {'nombre': vendedor.nombre, 'email': vendedor.email}
        self.db.delete(vendedor)
        self.db.flush()
        audit = VendedorAuditoria(
            vendedor_id=vendedor.id,
            operacion='DELETE',
            datos_anteriores=json.dumps(antes)
        )
        self.db.add(audit)
        self.db.commit()
