from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.proveedor import Proveedor, ProveedorAuditoria

class ProveedorService:
    def __init__(self, db: Session):
        self.db = db

    def crear_proveedor(self, data: Dict[str, Any], usuario_id: Optional[int] = None) -> Proveedor:
        try:
            proveedor = Proveedor(
                razon_social=data.get('razon_social'),
                paises_operacion=data.get('paises_operacion'),
                certificaciones_sanitarias=data.get('certificaciones_sanitarias'),
                categorias_suministradas=data.get('categorias_suministradas'),
                capacidad_cadena_frio=data.get('capacidad_cadena_frio'),
                created_by=usuario_id
            )
            self.db.add(proveedor)
            self.db.flush()
            # auditoria
            audit = ProveedorAuditoria(
                proveedor_id=proveedor.id,
                operacion='CREATE',
                usuario_id=usuario_id,
                datos_anteriores=None,
                datos_nuevos={
                    'razon_social': proveedor.razon_social,
                    'paises_operacion': proveedor.paises_operacion,
                }
            )
            self.db.add(audit)
            self.db.commit()
            self.db.refresh(proveedor)
            return proveedor
        except IntegrityError:
            self.db.rollback()
            raise
        except Exception:
            self.db.rollback()
            raise

    def obtener_proveedor(self, proveedor_id: int) -> Optional[Proveedor]:
        return self.db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()

    def listar_proveedores(self, skip: int = 0, limit: int = 100) -> List[Proveedor]:
        return self.db.query(Proveedor).offset(skip).limit(limit).all()

    def actualizar_proveedor(self, proveedor: Proveedor, data: Dict[str, Any], usuario_id: Optional[int] = None) -> Proveedor:
        antes = {
            'razon_social': proveedor.razon_social,
            'paises_operacion': proveedor.paises_operacion,
        }
        proveedor.razon_social = data.get('razon_social')
        proveedor.paises_operacion = data.get('paises_operacion')
        self.db.add(proveedor)
        self.db.flush()
        despues = {
            'razon_social': proveedor.razon_social,
            'paises_operacion': proveedor.paises_operacion,
        }
        audit = ProveedorAuditoria(
            proveedor_id=proveedor.id,
            operacion='UPDATE',
            usuario_id=usuario_id,
            datos_anteriores=antes,
            datos_nuevos=despues,
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(proveedor)
        return proveedor

    def eliminar_proveedor(self, proveedor: Proveedor, usuario_id: Optional[int] = None) -> None:
        # regla de negocio: bloquear si tiene productos asociados
        from sqlalchemy import text
        # comprobar existencia de productos asociados
        res = self.db.execute(text("SELECT 1 FROM productos WHERE proveedor_id = :pid LIMIT 1"), {'pid': proveedor.id}).first()
        if res is not None:
            raise ValueError('Proveedor con catálogo activo')
        antes = {'razon_social': proveedor.razon_social}
        self.db.delete(proveedor)
        self.db.flush()
        audit = ProveedorAuditoria(
            proveedor_id=proveedor.id,
            operacion='DELETE',
            usuario_id=usuario_id,
            datos_anteriores=antes,
            datos_nuevos=None,
        )
        self.db.add(audit)
        self.db.commit()
