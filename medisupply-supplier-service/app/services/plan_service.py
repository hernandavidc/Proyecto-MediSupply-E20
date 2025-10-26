from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.plan_venta import PlanVenta, PlanVentaAuditoria
from app.models.product import Producto


class PlanService:
    def __init__(self, db: Session):
        self.db = db

    def crear_plan(
        self,
        data: Dict[str, Any],
        usuario_id: Optional[int] = None,
        origen: str = "MANUAL",
    ) -> PlanVenta:
        # validaciones: productos existen
        prod_ids = set(data.get("productos_objetivo") or [])
        if not prod_ids:
            raise ValueError("productos_objetivo es obligatorio")
        q = self.db.query(Producto.id).filter(Producto.id.in_(list(prod_ids)))
        existentes = {r[0] for r in q.all()}
        if existentes != prod_ids:
            missing = prod_ids - existentes
            raise ValueError(f"Productos no encontrados: {missing}")
        # unicidad vendedor+periodo+anio+pais
        exists = (
            self.db.query(PlanVenta)
            .filter(
                PlanVenta.vendedor_id == data.get("vendedor_id"),
                PlanVenta.periodo == data.get("periodo"),
                PlanVenta.anio == data.get("anio"),
                PlanVenta.pais == data.get("pais"),
            )
            .first()
        )
        if exists:
            raise ValueError("Ya existe un plan para ese vendedor/periodo/año/país")
        try:
            plan = PlanVenta(
                vendedor_id=data.get("vendedor_id"),
                periodo=data.get("periodo"),
                anio=data.get("anio"),
                pais=data.get("pais"),
                productos_objetivo=list(prod_ids),
                meta_monetaria_usd=data.get("meta_monetaria_usd"),
                created_by=usuario_id,
            )
            self.db.add(plan)
            self.db.flush()
            audit = PlanVentaAuditoria(
                plan_id=plan.id,
                operacion="CREATE",
                usuario_id=usuario_id,
                datos_nuevos={"productos_objetivo": plan.productos_objetivo},
                origen=origen,
            )
            self.db.add(audit)
            self.db.commit()
            self.db.refresh(plan)
            return plan
        except IntegrityError:
            self.db.rollback()
            raise
        except Exception:
            self.db.rollback()
            raise

    def listar_planes(self, skip: int = 0, limit: int = 100):
        return self.db.query(PlanVenta).offset(skip).limit(limit).all()

    def obtener_plan(self, plan_id: int):
        return self.db.query(PlanVenta).filter(PlanVenta.id == plan_id).first()

    def eliminar_plan(self, plan: PlanVenta):
        # regla: no permitir eliminar si está en ejecución
        if plan.estado == "EN_EJECUCION":
            raise ValueError("No se puede eliminar un plan en ejecución")
        antes = {"estado": plan.estado}
        self.db.delete(plan)
        self.db.flush()
        audit = PlanVentaAuditoria(
            plan_id=plan.id, operacion="DELETE", datos_anteriores=antes
        )
        self.db.add(audit)
        self.db.commit()
