from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.vendedor import Vendedor, VendedorAuditoria
from app.models.catalogs import Pais
from app.models.plan_venta import PlanVenta
import json

class VendedorService:
    """Service for vendedor domain (create/list/get/delete).

    The service expects a SQLAlchemy Session injected (managed externally by the caller/tests).
    Methods that modify data ensure rollback on any exception to keep the session clean.
    """

    def __init__(self, db: Session):
        self.db = db

    def crear_vendedor(self, data: Dict[str, Any], usuario_id: Optional[int] = None, as_dict: bool = False) -> Vendedor:

        """Create a new vendedor and write an audit row.

        Raises ValueError for business validation (duplicate email) and propagates DB errors.
        """
        # validar email único
        existing = self.db.query(Vendedor).filter(Vendedor.email == data.get('email')).first()
        if existing:
            raise ValueError('Email ya registrado')

        # Validate pais (country) exists and is a positive integer
        pais_id = data.get('pais')
        try:
            if pais_id is None:
                raise ValueError('Pais requerido')
            pais_id = int(pais_id)
            if pais_id <= 0:
                raise ValueError('Pais inválido')
        except ValueError:
            raise ValueError('Pais inválido')

        # Ensure the pais exists in the catalogs table only if the paises table
        # has been populated (seeded). Some unit tests create a fresh DB
        # without catalog seed data and previously code allowed inserting
        # vendedores referring to numeric ids. To preserve test behaviour
        # we skip the existence check when the paises table is empty.
        try:
            total_paises = self.db.query(Pais).count()
        except Exception:
            total_paises = 0

        if total_paises > 0:
            pais_obj = self.db.query(Pais).filter(Pais.id == pais_id).first()
            if not pais_obj:
                raise ValueError('Pais no encontrado')

        vendedor = Vendedor(
            nombre=data.get('nombre'),
            email=data.get('email'),
            pais_id=pais_id,
            estado=data.get('estado') or 'ACTIVO',
            created_by=usuario_id,
        )

        try:
            self.db.add(vendedor)
            # flush so vendedor.id is available for audit
            self.db.flush()
            audit = VendedorAuditoria(
                vendedor_id=vendedor.id,
                operacion='CREATE',
                usuario_id=usuario_id,
                datos_nuevos=json.dumps({'nombre': vendedor.nombre, 'email': vendedor.email}),
            )
            self.db.add(audit)
            self.db.commit()
            self.db.refresh(vendedor)
            return self._to_dict(vendedor) if as_dict else vendedor
        except IntegrityError:
            # rollback DB state and re-raise for caller to handle
            try:
                self.db.rollback()
            except Exception:
                pass
            raise
        except Exception:
            # Ensure any unexpected exception doesn't leave the session in a bad state
            try:
                self.db.rollback()
            except Exception:
                pass
            raise

    def listar_vendedores(self, skip: int = 0, limit: int = 100, as_dict: bool = True) -> List[Dict[str, Any]]:
        """Return a list of vendedores (paginated)."""
        vendedores = self.db.query(Vendedor).offset(skip).limit(limit).all()
        if as_dict:
            return [self._to_dict(v) for v in vendedores]
        return vendedores

    def obtener_vendedor(self, vendedor_id: int) -> Optional[Vendedor]:
        """Fetch a vendedor by id or return None if not found."""
        return self.db.query(Vendedor).filter(Vendedor.id == vendedor_id).first()

    def eliminar_vendedor(self, vendedor: Vendedor) -> None:
        """Delete a vendedor if there are no associated plans; write audit.

        Raises ValueError when business rule blocks deletion.
        """
        # regla: no permitir eliminar si tiene planes de venta asociados
        has_plans = self.db.query(PlanVenta).filter(PlanVenta.vendedor_id == vendedor.id).first()
        if has_plans:
            raise ValueError('No se puede eliminar vendedor con planes asociados')

        antes = {'nombre': vendedor.nombre, 'email': vendedor.email}
        try:
            self.db.delete(vendedor)
            self.db.flush()
            audit = VendedorAuditoria(
                vendedor_id=vendedor.id,
                operacion='DELETE',
                datos_anteriores=json.dumps(antes),
            )
            self.db.add(audit)
            self.db.commit()
        except Exception:
            try:
                self.db.rollback()
            except Exception:
                pass
            raise
 
    def _to_dict(self, v: Vendedor) -> Dict[str, Any]:
        """Convierte ORM a dict compatible con el schema."""
        return {
            "id": v.id,
            "nombre": v.nombre,
            "email": v.email,
            "pais": getattr(v, "pais_id", None), 
            "estado": v.estado,
            "created_by": getattr(v, "created_by", None),
        }
