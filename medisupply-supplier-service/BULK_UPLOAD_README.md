# Carga Masiva de Productos - HU-005

## Descripción
Esta funcionalidad permite cargar productos de forma masiva desde un archivo CSV con separador pipeline (|), cumpliendo con los criterios de aceptación de la historia de usuario HU-005.

## Endpoint
```
POST /api/v1/productos/bulk-upload
```

## Parámetros
- `file`: Archivo CSV (multipart/form-data)
- `reject_on_errors`: Boolean (opcional, default: true) - Si debe rechazar todo el lote ante errores

## Formato del Archivo CSV

### Separador
El archivo debe usar el símbolo pipeline (|) como separador.

### Columnas Requeridas (en orden)
1. `sku` - Identificador único del producto
2. `nombre_producto` - Nombre del producto
3. `proveedor_id` - ID del proveedor (debe existir)
4. `ficha_tecnica_url` - URL de la ficha técnica (opcional)
5. `ca_temp` - Condición de temperatura de almacenamiento
6. `ca_humedad` - Condición de humedad de almacenamiento
7. `ca_luz` - Condición de luz de almacenamiento
8. `ca_ventilacion` - Condición de ventilación de almacenamiento
9. `ca_seguridad` - Condición de seguridad de almacenamiento
10. `ca_envase` - Condición de envase de almacenamiento
11. `org_tipo_medicamento` - Tipo de medicamento
12. `org_fecha_vencimiento` - Fecha de vencimiento (formato: YYYY-MM-DD)
13. `valor_unitario_usd` - Valor unitario en USD
14. `certificaciones_sanitarias` - Certificaciones separadas por punto y coma (;)

### Ejemplo de Archivo CSV
```csv
sku|nombre_producto|proveedor_id|ficha_tecnica_url|ca_temp|ca_humedad|ca_luz|ca_ventilacion|ca_seguridad|ca_envase|org_tipo_medicamento|org_fecha_vencimiento|valor_unitario_usd|certificaciones_sanitarias
MED001|Paracetamol 500mg|1|https://ejemplo.com/ficha.pdf|2-8°C|45-65%|Protegido de luz|Ventilación normal|Controlado|Envase original|Analgésicos|2025-12-31|15.50|1;2
MED002|Ibuprofeno 400mg|1||15-25°C|40-60%|Ambiente normal|Ventilación normal|Estándar|Envase original|Antiinflamatorios|2025-10-15|18.75|1;3
```

## Validaciones

### Campos Obligatorios
- `sku`: No puede estar vacío, no puede contener el carácter '0'
- `nombre_producto`: No puede estar vacío
- `proveedor_id`: Debe ser un número entero válido y el proveedor debe existir
- `valor_unitario_usd`: Debe ser un número mayor a 0

### Validaciones de Negocio
- El proveedor debe existir en la base de datos
- Si el producto tiene certificaciones, el proveedor debe tener al menos una certificación compatible
- El tipo de medicamento debe estar en la lista de tipos válidos
- La fecha de vencimiento debe estar en formato YYYY-MM-DD
- Las certificaciones deben ser números enteros separados por punto y coma

## Respuesta

### Éxito
```json
{
  "total_procesados": 2,
  "exitosos": 2,
  "fallidos": 0,
  "productos_creados": [
    {
      "id": 1,
      "sku": "MED001",
      "nombre_producto": "Paracetamol 500mg",
      "proveedor_id": 1,
      "valor_unitario_usd": 15.50,
      "origen": "BULK_UPLOAD"
    }
  ],
  "errores": [],
  "mensaje": "Procesamiento exitoso. 2 productos creados."
}
```

### Con Errores
```json
{
  "total_procesados": 2,
  "exitosos": 1,
  "fallidos": 1,
  "productos_creados": [...],
  "errores": [
    {
      "linea": 3,
      "campo": "general",
      "valor": "{'sku': '', 'nombre_producto': 'Producto', ...}",
      "error": "Campo obligatorio 'sku' está vacío"
    }
  ],
  "mensaje": "Procesamiento completado con 1 errores. 1 productos creados exitosamente."
}
```

## Modos de Operación

### Rechazar Lote Ante Errores (reject_on_errors=true)
- Si hay algún error, se hace rollback de toda la transacción
- No se crea ningún producto
- Se retorna error con detalles del primer error encontrado

### Continuar Ante Errores (reject_on_errors=false)
- Se procesan todos los productos válidos
- Se crean los productos válidos
- Se retorna reporte con productos creados y errores encontrados

## Archivo de Ejemplo
Se incluye un archivo `ejemplo_productos.csv` con 10 productos de ejemplo que cumplen con todas las validaciones.

## Testing
Los tests unitarios cubren:
- Carga masiva exitosa
- Manejo de errores con rechazo de lote
- Manejo de errores con procesamiento parcial
- Validaciones de columnas faltantes
- Validaciones de campos obligatorios
- Validaciones de formato de datos
- Conversión correcta de filas CSV a productos

## Uso con cURL
```bash
curl -X POST "http://localhost:8000/api/v1/productos/bulk-upload" \
  -F "file=@ejemplo_productos.csv" \
  -F "reject_on_errors=true"
```
