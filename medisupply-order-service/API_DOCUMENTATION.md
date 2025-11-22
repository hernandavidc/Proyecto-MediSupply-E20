# 📦 MediSupply Order Service - API Documentation

## 🌐 Base URLs

- **Directo:** `http://localhost:8003`
- **A través del API Gateway:** `http://localhost:8080`

## 🔐 Autenticación

Todos los endpoints requieren autenticación JWT. Primero obtén un token del user-service:

```bash
# 1. Login para obtener token
curl -X POST "http://localhost:8080/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@medisupply.com",
    "password": "admin123"
  }'

# Respuesta:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Usar el token en todas las peticiones:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" ...
```

---

## 📋 1. ÓRDENES (`/api/v1/ordenes`)

### **Estados de Orden**
Las órdenes pueden tener uno de los siguientes estados:
- **`ABIERTO`**: La orden está abierta y en proceso de captura de información (estado por defecto)
- **`POR_ALISTAR`**: La orden fue creada y está pendiente de alistamiento
- **`EN_ALISTAMIENTO`**: La orden está siendo preparada en bodega
- **`EN_REPARTO`**: La orden está en tránsito hacia el cliente
- **`ENTREGADO`**: La orden fue entregada exitosamente al cliente
- **`DEVUELTO`**: La orden fue devuelta

**⚠️ Importante:** Solo las órdenes en estado `ABIERTO` pueden ser modificadas mediante PUT. Intentar actualizar una orden con cualquier otro estado retornará un error 400 con el mensaje "El estado de la orden no permite modificaciones".

### **GET** - Listar todas las órdenes
```bash
curl -X GET "http://localhost:8080/api/v1/ordenes" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Parámetros de consulta opcionales:**
- `estado`: Filtrar por estado (ej: `ABIERTO`, `POR_ALISTAR`, `EN_REPARTO`, `ENTREGADO`)
- `id_cliente`: Filtrar por ID del cliente
- `id_vendedor`: Filtrar por ID del vendedor
- `fecha_desde`: Filtrar por fecha de creación de la orden (desde esta fecha, formato ISO 8601)
- `fecha_hasta`: Filtrar por fecha de creación de la orden (hasta esta fecha, formato ISO 8601)
- `skip`: Número de registros a saltar (paginación)
- `limit`: Número máximo de registros a retornar

**Nota:** Todos los filtros se pueden combinar para búsquedas más específicas.

**Ejemplos de consultas con filtros:**
```bash
# Filtrar por estado
curl -X GET "http://localhost:8080/api/v1/ordenes?estado=EN_REPARTO" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filtrar por cliente
curl -X GET "http://localhost:8080/api/v1/ordenes?id_cliente=123" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filtrar por vendedor
curl -X GET "http://localhost:8080/api/v1/ordenes?id_vendedor=456" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filtrar por rango de fechas
curl -X GET "http://localhost:8080/api/v1/ordenes?fecha_desde=2024-11-01T00:00:00&fecha_hasta=2024-11-30T23:59:59" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Combinar múltiples filtros: vendedor + estado + fechas
curl -X GET "http://localhost:8080/api/v1/ordenes?id_vendedor=456&estado=ENTREGADO&fecha_desde=2024-11-01T00:00:00&fecha_hasta=2024-11-30T23:59:59" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta (200 OK):**
```json
[
  {
    "id": 1,
    "fecha_entrega_estimada": "2024-12-25T10:00:00",
    "id_vehiculo": 1,
    "id_cliente": 123,
    "id_vendedor": 456,
    "estado": "EN_REPARTO",
    "fecha_creacion": "2024-11-21T20:30:00.123456",
    "productos": [
      {
        "id_producto": 101,
        "cantidad": 50
      },
      {
        "id_producto": 102,
        "cantidad": 25
      }
    ]
  },
  {
    "id": 2,
    "fecha_entrega_estimada": "2024-12-26T14:30:00",
    "id_vehiculo": 2,
    "id_cliente": 124,
    "id_vendedor": 457,
    "estado": "POR_ALISTAR",
    "fecha_creacion": "2024-11-21T21:15:00.789012",
    "productos": [
      {
        "id_producto": 103,
        "cantidad": 100
      }
    ]
  }
]
```

### **POST** - Crear nueva orden
**Nota:** El campo `estado` es opcional. Si no se especifica, el estado por defecto es `ABIERTO`.

```bash
curl -X POST "http://localhost:8080/api/v1/ordenes" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fecha_entrega_estimada": "2024-12-25T10:00:00",
    "id_vehiculo": 1,
    "id_cliente": 123,
    "id_vendedor": 456,
    "productos": [
      {
        "id_producto": 101,
        "cantidad": 50
      },
      {
        "id_producto": 102,
        "cantidad": 25
      }
    ]
  }'
```

**Respuesta (201 Created):**
```json
{
  "id": 1,
  "fecha_entrega_estimada": "2024-12-25T10:00:00",
  "id_vehiculo": 1,
  "id_cliente": 123,
  "id_vendedor": 456,
  "estado": "ABIERTO",
  "fecha_creacion": "2024-11-21T20:30:00.123456",
  "productos": [
    {
      "id_producto": 101,
      "cantidad": 50
    },
    {
      "id_producto": 102,
      "cantidad": 25
    }
  ]
}
```

### **GET** - Obtener orden por ID
```bash
curl -X GET "http://localhost:8080/api/v1/ordenes/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta (200 OK):**
```json
{
  "id": 1,
  "fecha_entrega_estimada": "2024-12-25T10:00:00",
  "id_vehiculo": 1,
  "id_cliente": 123,
  "id_vendedor": 456,
  "estado": "EN_REPARTO",
  "fecha_creacion": "2024-11-21T20:30:00.123456",
  "productos": [
    {
      "id_producto": 101,
      "cantidad": 50
    },
    {
      "id_producto": 102,
      "cantidad": 25
    }
  ]
}
```

**Respuesta (404 Not Found):**
```json
{
  "detail": "Orden not found"
}
```

### **PUT** - Actualizar orden
**⚠️ Restricción:** Solo las órdenes en estado `ABIERTO` pueden ser actualizadas.

```bash
curl -X PUT "http://localhost:8080/api/v1/ordenes/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fecha_entrega_estimada": "2024-12-26T15:00:00",
    "id_vehiculo": 2,
    "id_cliente": 123,
    "id_vendedor": 456,
    "estado": "POR_ALISTAR",
    "productos": [
      {
        "id_producto": 101,
        "cantidad": 75
      },
      {
        "id_producto": 103,
        "cantidad": 30
      }
    ]
  }'
```

**Respuesta (200 OK):** (Solo si la orden está en estado ABIERTO)
```json
{
  "id": 1,
  "fecha_entrega_estimada": "2024-12-26T15:00:00",
  "id_vehiculo": 2,
  "id_cliente": 123,
  "id_vendedor": 456,
  "estado": "POR_ALISTAR",
  "fecha_creacion": "2024-11-21T20:30:00.123456",
  "productos": [
    {
      "id_producto": 101,
      "cantidad": 75
    },
    {
      "id_producto": 103,
      "cantidad": 30
    }
  ]
}
```

**Respuesta (400 Bad Request):** (Si la orden NO está en estado ABIERTO)
```json
{
  "detail": "El estado de la orden no permite modificaciones"
}
```

### **DELETE** - Eliminar orden
```bash
curl -X DELETE "http://localhost:8080/api/v1/ordenes/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta (200 OK):**
```json
{
  "message": "Orden deleted successfully"
}
```

---

## 🚛 2. VEHÍCULOS (`/api/v1/vehiculos`)

### **GET** - Listar todos los vehículos
```bash
curl -X GET "http://localhost:8080/api/v1/vehiculos" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta (200 OK):**
```json
[
  {
    "id": 1,
    "id_conductor": 789,
    "placa": "ABC123",
    "tipo": "CAMION"
  },
  {
    "id": 2,
    "id_conductor": 790,
    "placa": "XYZ789",
    "tipo": "VAN"
  },
  {
    "id": 3,
    "id_conductor": 791,
    "placa": "DEF456",
    "tipo": "TRACTOMULA"
  }
]
```

### **POST** - Crear nuevo vehículo
```bash
curl -X POST "http://localhost:8080/api/v1/vehiculos" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id_conductor": 789,
    "placa": "ABC123",
    "tipo": "CAMION"
  }'
```

**Tipos de vehículo válidos:**
- `CAMION`
- `VAN`
- `TRACTOMULA`

**Respuesta (201 Created):**
```json
{
  "id": 1,
  "id_conductor": 789,
  "placa": "ABC123",
  "tipo": "CAMION"
}
```

**Respuesta (422 Validation Error - Placa duplicada):**
```json
{
  "detail": "Placa already exists"
}
```

### **GET** - Obtener vehículo por ID
```bash
curl -X GET "http://localhost:8080/api/v1/vehiculos/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta (200 OK):**
```json
{
  "id": 1,
  "id_conductor": 789,
  "placa": "ABC123",
  "tipo": "CAMION"
}
```

**Respuesta (404 Not Found):**
```json
{
  "detail": "Vehiculo not found"
}
```

### **PUT** - Actualizar vehículo
```bash
curl -X PUT "http://localhost:8080/api/v1/vehiculos/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id_conductor": 789,
    "placa": "XYZ789",
    "tipo": "VAN"
  }'
```

**Respuesta (200 OK):**
```json
{
  "id": 1,
  "id_conductor": 789,
  "placa": "XYZ789",
  "tipo": "VAN"
}
```

### **DELETE** - Eliminar vehículo
```bash
curl -X DELETE "http://localhost:8080/api/v1/vehiculos/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta (200 OK):**
```json
{
  "message": "Vehiculo deleted successfully"
}
```

**Nota:** Los productos de una orden ahora se gestionan directamente a través de los endpoints de órdenes. Al crear o actualizar una orden, se puede incluir la lista de productos en el campo `productos`.

---

## 🏢 3. BODEGAS (`/api/v1/bodegas`)

### **GET** - Listar todas las bodegas
```bash
curl -X GET "http://localhost:8080/api/v1/bodegas" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Parámetros de consulta opcionales:**
- `id_pais`: Filtrar bodegas por ID del país
- `id_producto`: Filtrar bodegas que tienen el producto en inventario (usa relación con bodega_producto)
- `skip`: Número de registros a saltar (paginación)
- `limit`: Número máximo de registros a retornar

**Ejemplos de consultas con filtros:**
```bash
# Filtrar por país
curl -X GET "http://localhost:8080/api/v1/bodegas?id_pais=1" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filtrar por producto (retorna solo bodegas que tienen ese producto)
curl -X GET "http://localhost:8080/api/v1/bodegas?id_producto=101" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Combinar filtros (bodegas de un país que tienen un producto específico)
curl -X GET "http://localhost:8080/api/v1/bodegas?id_pais=1&id_producto=101" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta (200 OK):**
```json
[
  {
    "id": 1,
    "nombre": "Bodega Central",
    "direccion": "Calle 123 #45-67",
    "id_pais": 1,
    "ciudad": "Bogotá",
    "latitud": 4.6097,
    "longitud": -74.0817
  },
  {
    "id": 2,
    "nombre": "Bodega Norte",
    "direccion": "Carrera 456 #78-90",
    "id_pais": 1,
    "ciudad": "Medellín",
    "latitud": 6.2442,
    "longitud": -75.5812
  },
  {
    "id": 3,
    "nombre": "Bodega Costa",
    "direccion": "Avenida 789 #12-34",
    "id_pais": 1,
    "ciudad": "Cartagena",
    "latitud": 10.3910,
    "longitud": -75.4794
  }
]
```

### **POST** - Crear nueva bodega
```bash
curl -X POST "http://localhost:8080/api/v1/bodegas" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Bodega Central",
    "direccion": "Calle 123 #45-67",
    "id_pais": 1,
    "ciudad": "Bogotá",
    "latitud": 4.6097,
    "longitud": -74.0817
  }'
```

**Respuesta (201 Created):**
```json
{
  "id": 1,
  "nombre": "Bodega Central",
  "direccion": "Calle 123 #45-67",
  "id_pais": 1,
  "ciudad": "Bogotá",
  "latitud": 4.6097,
  "longitud": -74.0817
}
```

### **GET** - Obtener bodega por ID
```bash
curl -X GET "http://localhost:8080/api/v1/bodegas/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta (200 OK):**
```json
{
  "id": 1,
  "nombre": "Bodega Central",
  "direccion": "Calle 123 #45-67",
  "id_pais": 1,
  "ciudad": "Bogotá",
  "latitud": 4.6097,
  "longitud": -74.0817
}
```

**Respuesta (404 Not Found):**
```json
{
  "detail": "Bodega not found"
}
```

### **PUT** - Actualizar bodega
```bash
curl -X PUT "http://localhost:8080/api/v1/bodegas/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Bodega Central Actualizada",
    "direccion": "Carrera 456 #78-90",
    "id_pais": 1,
    "ciudad": "Medellín",
    "latitud": 6.2442,
    "longitud": -75.5812
  }'
```

**Respuesta (200 OK):**
```json
{
  "id": 1,
  "nombre": "Bodega Central Actualizada",
  "direccion": "Carrera 456 #78-90",
  "id_pais": 1,
  "ciudad": "Medellín",
  "latitud": 6.2442,
  "longitud": -75.5812
}
```

### **DELETE** - Eliminar bodega
```bash
curl -X DELETE "http://localhost:8080/api/v1/bodegas/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta (200 OK):**
```json
{
  "message": "Bodega deleted successfully"
}
```

---

## 📊 4. BODEGA-PRODUCTOS (`/api/v1/bodega-productos`)

### **GET** - Listar todas las relaciones bodega-producto
```bash
curl -X GET "http://localhost:8080/api/v1/bodega-productos" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Parámetros de consulta opcionales:**
- `id_bodega`: Filtrar por ID de bodega
- `id_producto`: Filtrar por ID de producto
- `lote`: Filtrar por número de lote
- `latitud`: Latitud del punto de origen (para calcular pronóstico de entrega)
- `longitud`: Longitud del punto de origen (para calcular pronóstico de entrega)
- `skip`: Número de registros a saltar (paginación)
- `limit`: Número máximo de registros a retornar

**Nota sobre pronóstico de entrega:**
Si se proporcionan `latitud` y `longitud`, la respuesta incluirá el campo `pronostico_entrega` calculado con:
- Distancia desde el punto de origen hasta la bodega (fórmula de Haversine)
- Velocidad de transporte: 20 km/h
- Tiempo de alistamiento del producto

**Ejemplos de consultas con filtros:**
```bash
# Filtrar por bodega
curl -X GET "http://localhost:8080/api/v1/bodega-productos?id_bodega=1" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filtrar por producto
curl -X GET "http://localhost:8080/api/v1/bodega-productos?id_producto=101" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filtrar por lote
curl -X GET "http://localhost:8080/api/v1/bodega-productos?lote=LOTE-2024-001" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Combinar filtros (bodega y producto)
curl -X GET "http://localhost:8080/api/v1/bodega-productos?id_bodega=1&id_producto=101" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Consultar con ubicación para obtener pronóstico de entrega
curl -X GET "http://localhost:8080/api/v1/bodega-productos?latitud=4.6097&longitud=-74.0817" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta (200 OK):**
```json
[
  {
    "id_bodega": 1,
    "id_producto": 101,
    "lote": "LOTE-2024-001",
    "cantidad": 1000,
    "dias_alistamiento": 2,
    "pronostico_entrega": "2024-11-24T15:30:00"
  },
  {
    "id_bodega": 1,
    "id_producto": 102,
    "lote": "LOTE-2024-002",
    "cantidad": 500,
    "dias_alistamiento": 1,
    "pronostico_entrega": "2024-11-23T14:15:00"
  },
  {
    "id_bodega": 2,
    "id_producto": 101,
    "lote": "LOTE-2024-003",
    "cantidad": 750,
    "dias_alistamiento": 3,
    "pronostico_entrega": "2024-11-25T18:45:00"
  },
  {
    "id_bodega": 2,
    "id_producto": 103,
    "lote": "LOTE-2024-004",
    "cantidad": 300,
    "dias_alistamiento": 0,
    "pronostico_entrega": "2024-11-22T10:30:00"
  }
]
```

### **POST** - Agregar producto a una bodega
```bash
curl -X POST "http://localhost:8080/api/v1/bodega-productos" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id_bodega": 1,
    "id_producto": 101,
    "lote": "LOTE-2024-001",
    "cantidad": 1000,
    "dias_alistamiento": 2
  }'
```

**Respuesta (201 Created):**
```json
{
  "id_bodega": 1,
  "id_producto": 101,
  "lote": "LOTE-2024-001",
  "cantidad": 1000,
  "dias_alistamiento": 2,
  "pronostico_entrega": null
}
```

**Respuesta (422 Validation Error - Relación ya existe):**
```json
{
  "detail": "BodegaProducto already exists"
}
```

### **GET** - Obtener productos de una bodega específica
```bash
curl -X GET "http://localhost:8080/api/v1/bodega-productos/bodega/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta (200 OK):**
```json
[
  {
    "id_bodega": 1,
    "id_producto": 101,
    "lote": "LOTE-2024-001",
    "cantidad": 1000,
    "dias_alistamiento": 2,
    "pronostico_entrega": null
  },
  {
    "id_bodega": 1,
    "id_producto": 102,
    "lote": "LOTE-2024-002",
    "cantidad": 500,
    "dias_alistamiento": 1,
    "pronostico_entrega": null
  },
  {
    "id_bodega": 1,
    "id_producto": 103,
    "lote": "LOTE-2024-005",
    "cantidad": 250,
    "dias_alistamiento": 0,
    "pronostico_entrega": null
  }
]
```

**Respuesta (404 Not Found):**
```json
{
  "detail": "No products found for this bodega"
}
```

### **PUT** - Actualizar producto en bodega
```bash
curl -X PUT "http://localhost:8080/api/v1/bodega-productos/1/101/LOTE-2024-001" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cantidad": 1500,
    "dias_alistamiento": 3
  }'
```

**Nota:** Puedes actualizar `cantidad`, `dias_alistamiento` o ambos campos.

**Respuesta (200 OK):**
```json
{
  "id_bodega": 1,
  "id_producto": 101,
  "lote": "LOTE-2024-001",
  "cantidad": 1500,
  "dias_alistamiento": 3,
  "pronostico_entrega": null
}
```

### **DELETE** - Eliminar producto de bodega
```bash
curl -X DELETE "http://localhost:8080/api/v1/bodega-productos/1/101/LOTE-2024-001" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta (204 No Content):**
```
(Sin contenido)
```

---

## 📝 5. NOVEDADES (`/api/v1/novedades`)

### **GET** - Listar todas las novedades
```bash
curl -X GET "http://localhost:8080/api/v1/novedades" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta (200 OK):**
```json
[
  {
    "id": 1,
    "id_pedido": 1,
    "tipo": "DEVOLUCION",
    "descripcion": "Cliente devolvió producto por defecto de fábrica"
  },
  {
    "id": 2,
    "id_pedido": 1,
    "tipo": "CANTIDAD_DIFERENTE",
    "descripcion": "Se entregaron 45 unidades en lugar de 50"
  }
]
```

### **POST** - Crear nueva novedad
```bash
curl -X POST "http://localhost:8080/api/v1/novedades" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id_pedido": 1,
    "tipo": "DEVOLUCION",
    "descripcion": "Cliente devolvió producto por defecto de fábrica"
  }'
```

**Tipos de novedad válidos:**
- `DEVOLUCION`
- `CANTIDAD_DIFERENTE`
- `MAL_ESTADO`
- `PRODUCTO_NO_COINCIDE`

**Respuesta (201 Created):**
```json
{
  "id": 1,
  "id_pedido": 1,
  "tipo": "DEVOLUCION",
  "descripcion": "Cliente devolvió producto por defecto de fábrica"
}
```

### **GET** - Obtener novedad por ID
```bash
curl -X GET "http://localhost:8080/api/v1/novedades/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta (200 OK):**
```json
{
  "id": 1,
  "id_pedido": 1,
  "tipo": "DEVOLUCION",
  "descripcion": "Cliente devolvió producto por defecto de fábrica"
}
```

### **GET** - Obtener novedades de una orden específica
```bash
curl -X GET "http://localhost:8080/api/v1/novedades/orden/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta (200 OK):**
```json
[
  {
    "id": 1,
    "id_pedido": 1,
    "tipo": "DEVOLUCION",
    "descripcion": "Cliente devolvió producto por defecto de fábrica"
  },
  {
    "id": 2,
    "id_pedido": 1,
    "tipo": "CANTIDAD_DIFERENTE",
    "descripcion": "Se entregaron 45 unidades en lugar de 50"
  }
]
```

### **PUT** - Actualizar novedad
```bash
curl -X PUT "http://localhost:8080/api/v1/novedades/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id_pedido": 1,
    "tipo": "MAL_ESTADO",
    "descripcion": "Producto llegó dañado durante el transporte"
  }'
```

**Respuesta (200 OK):**
```json
{
  "id": 1,
  "id_pedido": 1,
  "tipo": "MAL_ESTADO",
  "descripcion": "Producto llegó dañado durante el transporte"
}
```

### **DELETE** - Eliminar novedad
```bash
curl -X DELETE "http://localhost:8080/api/v1/novedades/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta (200 OK):**
```json
{
  "message": "NovedadOrden deleted successfully"
}
```

---

## 📦 6. ORDEN-PRODUCTOS (`/api/v1/orden-productos`)

Los productos asociados a órdenes se pueden gestionar directamente mediante los endpoints de órdenes (al crear/actualizar una orden), pero también están disponibles estos endpoints específicos para consultas y operaciones directas.

### **GET** - Listar todas las relaciones orden-producto

**Parámetros de consulta opcionales:**
- `id_vendedor`: Filtrar productos de órdenes de un vendedor específico (usa JOIN con tabla órdenes)
- `fecha_desde`: Filtrar por fecha de creación de la orden (desde esta fecha, formato ISO 8601)
- `fecha_hasta`: Filtrar por fecha de creación de la orden (hasta esta fecha, formato ISO 8601)
- `skip`: Número de registros a saltar (paginación)
- `limit`: Número máximo de registros a retornar

**Nota:** Los filtros `id_vendedor`, `fecha_desde` y `fecha_hasta` se pueden combinar para búsquedas más específicas.

```bash
# Listar todos los productos en órdenes
curl -X GET "http://localhost:8080/api/v1/orden-productos" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filtrar por vendedor (obtiene productos de todas las órdenes de ese vendedor)
curl -X GET "http://localhost:8080/api/v1/orden-productos?id_vendedor=456" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filtrar por rango de fechas
curl -X GET "http://localhost:8080/api/v1/orden-productos?fecha_desde=2024-11-01T00:00:00&fecha_hasta=2024-11-30T23:59:59" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Combinar filtros: vendedor + rango de fechas
curl -X GET "http://localhost:8080/api/v1/orden-productos?id_vendedor=456&fecha_desde=2024-11-01T00:00:00&fecha_hasta=2024-11-30T23:59:59" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta (200 OK):**
```json
[
  {
    "id_orden": 1,
    "id_producto": 101,
    "cantidad": 50
  },
  {
    "id_orden": 1,
    "id_producto": 102,
    "cantidad": 25
  },
  {
    "id_orden": 2,
    "id_producto": 103,
    "cantidad": 100
  }
]
```

### **GET** - Listar productos por orden específica
```bash
curl -X GET "http://localhost:8080/api/v1/orden-productos/orden/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta (200 OK):**
```json
[
  {
    "id_orden": 1,
    "id_producto": 101,
    "cantidad": 50
  },
  {
    "id_orden": 1,
    "id_producto": 102,
    "cantidad": 25
  }
]
```

### **GET** - Obtener un producto específico de una orden
```bash
curl -X GET "http://localhost:8080/api/v1/orden-productos/1/101" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta (200 OK):**
```json
{
  "id_orden": 1,
  "id_producto": 101,
  "cantidad": 50
}
```

**Respuesta (404 Not Found):**
```json
{
  "detail": "OrdenProducto no encontrado"
}
```

### **POST** - Agregar producto a una orden
```bash
curl -X POST "http://localhost:8080/api/v1/orden-productos" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id_orden": 1,
    "id_producto": 104,
    "cantidad": 30
  }'
```

**Respuesta (201 Created):**
```json
{
  "id_orden": 1,
  "id_producto": 104,
  "cantidad": 30
}
```

### **PUT** - Actualizar cantidad de un producto en una orden
```bash
curl -X PUT "http://localhost:8080/api/v1/orden-productos/1/101" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cantidad": 75
  }'
```

**Respuesta (200 OK):**
```json
{
  "id_orden": 1,
  "id_producto": 101,
  "cantidad": 75
}
```

### **DELETE** - Eliminar producto de una orden
```bash
curl -X DELETE "http://localhost:8080/api/v1/orden-productos/1/101" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta (204 No Content):**
Sin contenido.

**Respuesta (404 Not Found):**
```json
{
  "detail": "OrdenProducto no encontrado"
}
```

---

## 🏥 7. HEALTH CHECK

### **GET** - Verificar estado del servicio
```bash
curl -X GET "http://localhost:8080/healthz"
# o directamente:
curl -X GET "http://localhost:8003/healthz"
```

**Respuesta (200 OK - Servicio saludable):**
```json
{
  "status": "healthy",
  "service": "order-service",
  "database": "connected",
  "tables": "ready"
}
```

**Respuesta (503 Service Unavailable - Servicio degradado):**
```json
{
  "status": "degraded",
  "service": "order-service",
  "database": "connected",
  "tables": "not_ready",
  "message": "Database connected but tables not created yet"
}
```

**Respuesta (503 Service Unavailable - Servicio no disponible):**
```json
{
  "status": "unhealthy",
  "service": "order-service",
  "database": "disconnected",
  "error": "Connection to database failed"
}
```

---

## 📚 8. DOCUMENTACIÓN

### **Swagger UI**
```
http://localhost:8080/order-docs
```

### **ReDoc**
```
http://localhost:8080/order-redoc
```

### **OpenAPI JSON**
```
http://localhost:8080/order-openapi.json
```

---

## 🔧 Ejemplos de Flujo Completo

### **1. Crear una orden completa con productos**

```bash
# 1. Crear vehículo
curl -X POST "http://localhost:8080/api/v1/vehiculos" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id_conductor": 789,
    "placa": "ABC123",
    "tipo": "CAMION"
  }'

# 2. Crear bodega
curl -X POST "http://localhost:8080/api/v1/bodegas" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Bodega Principal",
    "direccion": "Calle 123 #45-67",
    "id_pais": 1,
    "ciudad": "Bogotá",
    "latitud": 4.6097,
    "longitud": -74.0817
  }'

# 3. Agregar productos a la bodega
curl -X POST "http://localhost:8080/api/v1/bodega-productos" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id_bodega": 1,
    "id_producto": 101,
    "lote": "LOTE-2024-001",
    "cantidad": 1000,
    "dias_alistamiento": 2
  }'

# 4. Crear orden con productos
curl -X POST "http://localhost:8080/api/v1/ordenes" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fecha_entrega_estimada": "2024-12-25T10:00:00",
    "id_vehiculo": 1,
    "id_cliente": 123,
    "id_vendedor": 456,
    "productos": [
      {
        "id_producto": 101,
        "cantidad": 50
      }
    ]
  }'

# 5. Crear novedad si es necesario
curl -X POST "http://localhost:8080/api/v1/novedades" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id_pedido": 1,
    "tipo": "CANTIDAD_DIFERENTE",
    "descripcion": "Se entregaron 45 unidades en lugar de 50"
  }'
```

---

## ⚠️ Códigos de Error Comunes

| Código | Descripción | Solución |
|--------|-------------|----------|
| `401` | No autorizado | Verificar token JWT |
| `404` | Recurso no encontrado | Verificar ID del recurso |
| `422` | Error de validación | Verificar formato de datos |
| `500` | Error interno del servidor | Revisar logs del servicio |

---

## 🐳 Comandos Docker Útiles

```bash
# Ver logs del servicio
docker logs medisupply-order-service -f

# Reiniciar solo el servicio de órdenes
docker-compose -f docker-compose-dario.yml restart medisupply-order-service

# Ver estado de todos los contenedores
docker-compose -f docker-compose-dario.yml ps
```

---

## 📋 Notas Importantes

1. **Autenticación requerida:** Todos los endpoints requieren token JWT válido
2. **Validaciones:** Los datos se validan automáticamente con Pydantic
3. **Relaciones:** Las llaves foráneas deben existir antes de crear relaciones
4. **Placas únicas:** Las placas de vehículos deben ser únicas
5. **Fechas:** Usar formato ISO 8601 (`YYYY-MM-DDTHH:MM:SS`)
6. **Coordenadas:** Latitud y longitud en formato decimal

---

*Documentación generada para MediSupply Order Service v1.0.0*
