"""
Servicio de Proveedor para MediSupply
Implementa lógica de negocio según HU-001
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import json

from app.models.proveedor import Proveedor, ProveedorAuditoria
from app.schemas.proveedor_schema import ProveedorCreate, ProveedorUpdate
from app.core.enums import EstadoProveedor


class ProveedorService:
    """Servicio para manejar operaciones de proveedores"""

    def __init__(self, db: Session):
        self.db = db

    def crear_proveedor(
        self,
        proveedor_data: ProveedorCreate,
        usuario_id: int,
        ip_usuario: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Proveedor:
        """
        Crear un nuevo proveedor
        Incluye auditoría automática
        """
        try:
            # Crear instancia del proveedor
            nuevo_proveedor = Proveedor(
                razon_social=proveedor_data.razon_social,
                paises_operacion=proveedor_data.paises_operacion,
                certificaciones_sanitarias=proveedor_data.certificaciones_sanitarias,
                categorias_suministradas=proveedor_data.categorias_suministradas,
                capacidad_cadena_frio=proveedor_data.capacidad_cadena_frio or [],
                contacto_principal=proveedor_data.contacto_principal,
                email_contacto=proveedor_data.email_contacto,
                telefono_contacto=proveedor_data.telefono_contacto,
                notas=proveedor_data.notas,
                estado=EstadoProveedor.PENDIENTE_APROBACION,
                created_by=usuario_id,
                tiene_productos_activos=False,
            )

            # Guardar en base de datos
            self.db.add(nuevo_proveedor)
            self.db.flush()  # Para obtener el ID sin hacer commit

            # Registrar auditoría
            self._registrar_auditoria(
                proveedor_id=nuevo_proveedor.id,
                operacion="CREATE",
                usuario_id=usuario_id,
                datos_anteriores=None,
                datos_nuevos=self._proveedor_to_dict(nuevo_proveedor),
                ip_usuario=ip_usuario,
                user_agent=user_agent,
            )

            self.db.commit()
            self.db.refresh(nuevo_proveedor)
            return nuevo_proveedor

        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Error de integridad: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error al crear proveedor: {str(e)}")

    def obtener_proveedor(self, proveedor_id: int) -> Optional[Proveedor]:
        """Obtener proveedor por ID"""
        return self.db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()

    def listar_proveedores(
        self,
        skip: int = 0,
        limit: int = 100,
        estado: Optional[EstadoProveedor] = None,
        pais: Optional[str] = None,
    ) -> List[Proveedor]:
        """
        Listar proveedores con filtros opcionales
        """
        query = self.db.query(Proveedor)

        if estado:
            query = query.filter(Proveedor.estado == estado)

        if pais:
            query = query.filter(Proveedor.paises_operacion.contains([pais]))

        return query.offset(skip).limit(limit).all()

    def actualizar_proveedor(
        self,
        proveedor_id: int,
        proveedor_data: ProveedorUpdate,
        usuario_id: int,
        ip_usuario: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Optional[Proveedor]:
        """
        Actualizar proveedor existente
        Incluye auditoría de cambios
        """
        try:
            proveedor = self.obtener_proveedor(proveedor_id)
            if not proveedor:
                return None

            # Guardar estado anterior para auditoría
            datos_anteriores = self._proveedor_to_dict(proveedor)
            campos_modificados = []

            # Actualizar solo campos proporcionados
            update_data = proveedor_data.dict(exclude_unset=True)

            for field, value in update_data.items():
                if hasattr(proveedor, field):
                    old_value = getattr(proveedor, field)
                    if old_value != value:
                        setattr(proveedor, field, value)
                        campos_modificados.append(field)

            # Si hay cambios en categorias_suministradas, aplicar inmediatamente
            if "categorias_suministradas" in campos_modificados:
                # Aquí se podría implementar lógica adicional para validar productos
                pass

            # Actualizar campos de auditoría
            proveedor.updated_by = usuario_id

            # Guardar cambios
            self.db.flush()

            # Registrar auditoría solo si hubo cambios
            if campos_modificados:
                datos_nuevos = self._proveedor_to_dict(proveedor)
                self._registrar_auditoria(
                    proveedor_id=proveedor.id,
                    operacion="UPDATE",
                    usuario_id=usuario_id,
                    datos_anteriores=datos_anteriores,
                    datos_nuevos=datos_nuevos,
                    campos_modificados=campos_modificados,
                    ip_usuario=ip_usuario,
                    user_agent=user_agent,
                )

            self.db.commit()
            self.db.refresh(proveedor)
            return proveedor

        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error al actualizar proveedor: {str(e)}")

    def eliminar_proveedor(
        self,
        proveedor_id: int,
        usuario_id: int,
        ip_usuario: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> bool:
        """
        Eliminar proveedor
        Valida regla de negocio: no eliminar si tiene productos activos
        """
        try:
            proveedor = self.obtener_proveedor(proveedor_id)
            if not proveedor:
                return False

            # Validar regla de negocio según HU-001
            if proveedor.tiene_productos_activos:
                raise ValueError("Proveedor con catálogo activo")

            # Guardar datos para auditoría
            datos_anteriores = self._proveedor_to_dict(proveedor)

            # Registrar auditoría antes de eliminar
            self._registrar_auditoria(
                proveedor_id=proveedor.id,
                operacion="DELETE",
                usuario_id=usuario_id,
                datos_anteriores=datos_anteriores,
                datos_nuevos=None,
                ip_usuario=ip_usuario,
                user_agent=user_agent,
            )

            # Eliminar proveedor
            self.db.delete(proveedor)
            self.db.commit()
            return True

        except ValueError:
            # Re-lanzar errores de negocio sin modificar
            raise
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error al eliminar proveedor: {str(e)}")

    def obtener_auditoria_proveedor(
        self, proveedor_id: int
    ) -> List[ProveedorAuditoria]:
        """Obtener historial de auditoría de un proveedor"""
        return (
            self.db.query(ProveedorAuditoria)
            .filter(ProveedorAuditoria.proveedor_id == proveedor_id)
            .order_by(ProveedorAuditoria.timestamp.desc())
            .all()
        )

    def _proveedor_to_dict(self, proveedor: Proveedor) -> Dict[str, Any]:
        """Convertir proveedor a diccionario para auditoría"""
        return {
            "id": proveedor.id,
            "razon_social": proveedor.razon_social,
            "paises_operacion": proveedor.paises_operacion,
            "certificaciones_sanitarias": proveedor.certificaciones_sanitarias,
            "categorias_suministradas": proveedor.categorias_suministradas,
            "capacidad_cadena_frio": proveedor.capacidad_cadena_frio,
            "estado": proveedor.estado,
            "contacto_principal": proveedor.contacto_principal,
            "email_contacto": proveedor.email_contacto,
            "telefono_contacto": proveedor.telefono_contacto,
            "notas": proveedor.notas,
            "tiene_productos_activos": proveedor.tiene_productos_activos,
        }

    def _registrar_auditoria(
        self,
        proveedor_id: int,
        operacion: str,
        usuario_id: int,
        datos_anteriores: Optional[Dict[str, Any]],
        datos_nuevos: Optional[Dict[str, Any]],
        campos_modificados: Optional[List[str]] = None,
        ip_usuario: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Registrar entrada de auditoría"""
        auditoria = ProveedorAuditoria(
            proveedor_id=proveedor_id,
            operacion=operacion,
            usuario_id=usuario_id,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos,
            campos_modificados=campos_modificados,
            ip_usuario=ip_usuario,
            user_agent=user_agent,
        )
        self.db.add(auditoria)
