from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.product import Producto, ProductoAuditoria
from app.models.proveedor import Proveedor
from datetime import date, datetime
import csv
import io
from app.schemas.product_schema import ProductoBulkResponse, ErrorDetalle, ProductoResponse


def _serialize_dates(obj: Any):
    """Recursively convert date/datetime objects to ISO strings for JSON storage."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _serialize_dates(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize_dates(v) for v in obj]
    return obj

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def crear_producto(self, data: Dict[str, Any], usuario_id: Optional[int] = None, origen: str='MANUAL') -> Producto:
        # verificaciones de negocio: proveedor existe
        proveedor = self.db.query(Proveedor).filter(Proveedor.id == data.get('proveedor_id')).first()
        if not proveedor:
            raise ValueError('Proveedor no encontrado')
        # Validación mínima: el SKU no debe repetirse
        sku_val = data.get('sku')
        if sku_val:
            existing = self.db.query(Producto).filter(Producto.sku == sku_val).first()
            if existing:
                raise ValueError(f"SKU ya existe: {sku_val}")
        # verificar certificaciones compatibles: si producto tiene certificaciones, proveedor debe tener al menos una coincidente
        prod_certs = set(data.get('certificaciones') or [])
        prov_certs = set(proveedor.certificaciones_sanitarias or [])
        if prod_certs and not (prod_certs & prov_certs):
            raise ValueError('Proveedor no tiene certificaciones compatibles')
        try:
            # Serialize any date/datetime inside JSON fields to avoid JSON encoding errors
            condiciones = data.get('condiciones')
            organizacion = data.get('organizacion')
            if condiciones is not None:
                condiciones = _serialize_dates(condiciones)
            if organizacion is not None:
                organizacion = _serialize_dates(organizacion)

            producto = Producto(
                sku=data.get('sku'),
                nombre_producto=data.get('nombre_producto'),
                proveedor_id=data.get('proveedor_id'),
                ficha_tecnica_url=data.get('ficha_tecnica_url'),
                condiciones=condiciones,
                organizacion=organizacion,
                tipo_medicamento=data.get('tipo_medicamento'),
                fecha_vencimiento=data.get('fecha_vencimiento'),
                valor_unitario_usd=data.get('valor_unitario_usd'),
                certificaciones=data.get('certificaciones'),
                tiempo_entrega_dias=data.get('tiempo_entrega_dias'),
                origen=origen,
            )
            self.db.add(producto)
            self.db.flush()
            audit = ProductoAuditoria(
                producto_id=producto.id,
                operacion='CREATE',
                usuario_id=usuario_id,
                datos_nuevos={'sku': producto.sku, 'nombre_producto': producto.nombre_producto},
                origen=origen
            )
            self.db.add(audit)
            self.db.commit()
            self.db.refresh(producto)
            return producto
        except IntegrityError:
            self.db.rollback()
            raise
        except Exception:
            self.db.rollback()
            raise

    def listar_productos(self, skip: int=0, limit: int=100):
        return self.db.query(Producto).offset(skip).limit(limit).all()

    def obtener_producto(self, producto_id: int):
        return self.db.query(Producto).filter(Producto.id == producto_id).first()

    def procesar_carga_masiva(self, csv_content: str, reject_on_errors: bool = True) -> ProductoBulkResponse:
        """
        Procesa carga masiva de productos desde contenido CSV con separador pipeline (|)
        """
        # Columnas esperadas según el requerimiento
        columnas_esperadas = [
            'sku', 'nombre_producto', 'proveedor_id', 'ficha_tecnica_url',
            'ca_temp', 'ca_humedad', 'ca_luz', 'ca_ventilacion', 'ca_seguridad', 'ca_envase',
            'org_tipo_medicamento', 'org_fecha_vencimiento', 'valor_unitario_usd', 'certificaciones_sanitarias'
        ]
        
        productos_creados = []
        errores = []
        total_procesados = 0
        
        try:
            # Parsear CSV con separador pipeline
            csv_reader = csv.DictReader(io.StringIO(csv_content), delimiter='|')
            
            # Validar columnas
            if not csv_reader.fieldnames:
                raise ValueError("El archivo CSV está vacío o no tiene encabezados")
            
            columnas_faltantes = set(columnas_esperadas) - set(csv_reader.fieldnames)
            if columnas_faltantes:
                raise ValueError(f"Faltan las siguientes columnas requeridas: {', '.join(columnas_faltantes)}")
            
            # Procesar cada fila
            for linea_num, fila in enumerate(csv_reader, start=2):  # Empezar en 2 porque línea 1 es encabezado
                total_procesados += 1
                
                try:
                    # Convertir fila a formato de producto
                    producto_data = self._convertir_fila_a_producto(fila)
                    
                    # Crear producto
                    producto = self.crear_producto(
                        producto_data, 
                        usuario_id=None, 
                        origen='BULK_UPLOAD'
                    )
                    
                    # Convertir a response
                    producto_response = ProductoResponse.model_validate(producto)
                    productos_creados.append(producto_response)
                    
                except Exception as e:
                    error_detalle = ErrorDetalle(
                        linea=linea_num,
                        campo="general",
                        valor=str(fila),
                        error=str(e)
                    )
                    errores.append(error_detalle)
                    
                    # Si se debe rechazar el lote ante errores, hacer rollback
                    if reject_on_errors:
                        self.db.rollback()
                        raise ValueError(f"Error en línea {linea_num}: {str(e)}")
            
            # Si hay errores pero no se rechaza el lote, hacer commit parcial
            if errores and not reject_on_errors:
                self.db.commit()
            
            # Generar mensaje de resultado
            if errores:
                mensaje = f"Procesamiento completado con {len(errores)} errores. {len(productos_creados)} productos creados exitosamente."
            else:
                mensaje = f"Procesamiento exitoso. {len(productos_creados)} productos creados."
            
            return ProductoBulkResponse(
                total_procesados=total_procesados,
                exitosos=len(productos_creados),
                fallidos=len(errores),
                productos_creados=productos_creados,
                errores=errores,
                mensaje=mensaje
            )
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error procesando archivo CSV: {str(e)}")

    def _convertir_fila_a_producto(self, fila: Dict[str, str]) -> Dict[str, Any]:
        """
        Convierte una fila del CSV al formato esperado por crear_producto
        """
        # Validar campos obligatorios
        campos_obligatorios = ['sku', 'nombre_producto', 'proveedor_id', 'valor_unitario_usd']
        for campo in campos_obligatorios:
            if not fila.get(campo) or fila[campo].strip() == '':
                raise ValueError(f"Campo obligatorio '{campo}' está vacío")
        
        # Construir condiciones de almacenamiento
        condiciones = {}
        campos_ca = ['ca_temp', 'ca_humedad', 'ca_luz', 'ca_ventilacion', 'ca_seguridad', 'ca_envase']
        mapeo_campos = {
            'ca_temp': 'temperatura',
            'ca_humedad': 'humedad', 
            'ca_luz': 'luz',
            'ca_ventilacion': 'ventilacion',
            'ca_seguridad': 'seguridad',
            'ca_envase': 'envase'
        }
        for campo in campos_ca:
            valor = fila.get(campo, '').strip()
            if valor:
                campo_condicion = mapeo_campos[campo]
                condiciones[campo_condicion] = valor
        
        # Construir organización
        organizacion = {}
        if fila.get('org_tipo_medicamento', '').strip():
            organizacion['tipo_medicamento'] = fila['org_tipo_medicamento'].strip()
        
        if fila.get('org_fecha_vencimiento', '').strip():
            try:
                fecha_str = fila['org_fecha_vencimiento'].strip()
                fecha_vencimiento = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                organizacion['fecha_vencimiento'] = fecha_vencimiento
            except ValueError:
                raise ValueError(f"Formato de fecha inválido en org_fecha_vencimiento: {fila['org_fecha_vencimiento']}")
        
        # Procesar certificaciones (separadas por punto y coma)
        certificaciones = []
        if fila.get('certificaciones_sanitarias', '').strip():
            certs_str = fila['certificaciones_sanitarias'].strip()
            try:
                certificaciones = [int(cert.strip()) for cert in certs_str.split(';') if cert.strip()]
            except ValueError:
                raise ValueError(f"Certificaciones deben ser números enteros separados por punto y coma: {certs_str}")
        
        # Validar y convertir valor unitario
        try:
            valor_unitario = float(fila['valor_unitario_usd'])
            if valor_unitario <= 0:
                raise ValueError("Valor unitario debe ser mayor a 0")
        except ValueError:
            raise ValueError(f"Valor unitario inválido: {fila['valor_unitario_usd']}")
        
        # Validar proveedor_id
        try:
            proveedor_id = int(fila['proveedor_id'])
        except ValueError:
            raise ValueError(f"ID de proveedor inválido: {fila['proveedor_id']}")
        
        return {
            'sku': fila['sku'].strip(),
            'nombre_producto': fila['nombre_producto'].strip(),
            'proveedor_id': proveedor_id,
            'ficha_tecnica_url': fila.get('ficha_tecnica_url', '').strip() or None,
            'condiciones': condiciones if condiciones else None,
            'organizacion': organizacion if organizacion else None,
            'tipo_medicamento': fila.get('org_tipo_medicamento', '').strip() or None,
            'fecha_vencimiento': organizacion.get('fecha_vencimiento') if organizacion else None,
            'valor_unitario_usd': valor_unitario,
            'certificaciones': certificaciones if certificaciones else None,
            'tiempo_entrega_dias': None  # No incluido en el CSV según el requerimiento
        }
