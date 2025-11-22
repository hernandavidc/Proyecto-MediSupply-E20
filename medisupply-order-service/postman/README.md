# 📮 Colecciones de Postman - MediSupply Order Service

## 📁 Archivos Incluidos

- **`MediSupply_Order_Service.postman_collection.json`** - Colección completa con todos los endpoints
- **`MediSupply_Environment.postman_environment.json`** - Environment con variables configuradas
- **`README.md`** - Este archivo con instrucciones

## 🚀 Cómo Importar en Postman

### 1. **Importar la Colección**
1. Abre Postman
2. Click en **"Import"** (botón superior izquierdo)
3. Arrastra el archivo `MediSupply_Order_Service.postman_collection.json`
4. Click **"Import"**

### 2. **Importar el Environment**
1. Click en **"Import"** nuevamente
2. Arrastra el archivo `MediSupply_Environment.postman_environment.json`
3. Click **"Import"**

### 3. **Activar el Environment**
1. En la esquina superior derecha, selecciona **"MediSupply Environment"**
2. Verifica que las variables estén configuradas correctamente

## 🔧 Configuración Inicial

### **Variables del Environment**

| Variable | Valor por Defecto | Descripción |
|----------|-------------------|-------------|
| `base_url` | `http://localhost:8080` | API Gateway |
| `direct_url` | `http://localhost:8003` | Order Service directo |
| `user_service_url` | `http://localhost:8001` | User Service directo |
| `auth_token` | *(vacío)* | Se llena automáticamente |
| `admin_email` | `admin@medisupply.com` | Email para login |
| `admin_password` | `admin123` | Password para login |

## 🔐 Autenticación

### **Paso 1: Obtener Token**
1. Ejecuta la request **"🔐 Authentication > Login - Get Token"**
2. El token se guardará automáticamente en la variable `auth_token`
3. Todas las demás requests usarán este token automáticamente

### **Configuración Manual del Token**
Si necesitas configurar el token manualmente:
1. Ve a **Environment > MediSupply Environment**
2. Edita la variable `auth_token`
3. Pega tu JWT token

## 📋 Estructura de la Colección

### **🔐 Authentication**
- **Login - Get Token** - Obtiene JWT token del user-service

### **📋 Órdenes**
- Listar Órdenes
- Crear Orden
- Obtener Orden por ID
- Actualizar Orden
- Eliminar Orden

### **🚛 Vehículos**
- Listar Vehículos
- Crear Vehículo (tipos: CAMION, VAN, TRACTOMULA)
- Obtener Vehículo por ID
- Actualizar Vehículo
- Eliminar Vehículo

### **📦 Orden-Productos**
- Listar Orden-Productos
- Agregar Producto a Orden
- Productos de una Orden
- Actualizar Cantidad en Orden
- Eliminar Producto de Orden

### **🏢 Bodegas**
- Listar Bodegas
- Crear Bodega
- Obtener Bodega por ID
- Actualizar Bodega
- Eliminar Bodega

### **📊 Bodega-Productos**
- Listar Bodega-Productos
- Agregar Producto a Bodega
- Productos de una Bodega
- Actualizar Cantidad en Bodega
- Eliminar Producto de Bodega

### **📝 Novedades**
- Listar Novedades
- Crear Novedad (tipos: DEVOLUCION, CANTIDAD_DIFERENTE, MAL_ESTADO, PRODUCTO_NO_COINCIDE)
- Obtener Novedad por ID
- Novedades de una Orden
- Actualizar Novedad
- Eliminar Novedad

### **🏥 Health & Docs**
- Health Check (a través del gateway)
- Health Check (directo)
- OpenAPI JSON

## 🔄 Flujo de Trabajo Recomendado

### **1. Configuración Inicial**
```
1. Importar colección y environment
2. Ejecutar "Login - Get Token"
3. Verificar que el token se guardó correctamente
```

### **2. Crear Datos Base**
```
1. Crear Vehículo
2. Crear Bodega
3. Agregar Productos a Bodega
```

### **3. Gestionar Órdenes**
```
1. Crear Orden
2. Agregar Productos a la Orden
3. Crear Novedades si es necesario
```

## 📝 Ejemplos de Datos

### **Crear Vehículo**
```json
{
    "id_conductor": 789,
    "placa": "ABC123",
    "tipo": "CAMION"
}
```

### **Crear Bodega**
```json
{
    "nombre": "Bodega Central",
    "direccion": "Calle 123 #45-67",
    "id_pais": 1,
    "ciudad": "Bogotá",
    "latitud": 4.6097,
    "longitud": -74.0817
}
```

### **Crear Orden**
```json
{
    "fecha_entrega_estimada": "2024-12-25T10:00:00",
    "id_vehiculo": 1,
    "id_cliente": 123,
    "id_vendedor": 456
}
```

### **Agregar Producto a Orden**
```json
{
    "id_orden": 1,
    "id_producto": 101,
    "cantidad": 50
}
```

### **Crear Novedad**
```json
{
    "id_pedido": 1,
    "tipo": "DEVOLUCION",
    "descripcion": "Cliente devolvió producto por defecto de fábrica"
}
```

## ⚠️ Notas Importantes

### **Autenticación**
- Todos los endpoints (excepto health y docs) requieren token JWT
- El token se obtiene del user-service
- El token se incluye automáticamente en las requests

### **Validaciones**
- Las placas de vehículos deben ser únicas
- Los tipos de vehículo son: `CAMION`, `VAN`, `TRACTOMULA`
- Los tipos de novedad son: `DEVOLUCION`, `CANTIDAD_DIFERENTE`, `MAL_ESTADO`, `PRODUCTO_NO_COINCIDE`
- Las fechas deben estar en formato ISO 8601: `YYYY-MM-DDTHH:MM:SS`

### **Relaciones**
- Para crear una orden, el vehículo debe existir
- Para agregar productos a orden/bodega, ambos deben existir
- Para crear novedades, la orden debe existir

### **URLs**
- **Gateway (recomendado):** `http://localhost:8080` - Incluye balanceador y CORS
- **Directo:** `http://localhost:8003` - Acceso directo al servicio

## 🐛 Troubleshooting

### **Error 401 - Unauthorized**
- Verificar que el token esté configurado
- Ejecutar nuevamente "Login - Get Token"
- Verificar que el user-service esté corriendo

### **Error 404 - Not Found**
- Verificar que el ID del recurso exista
- Verificar la URL del endpoint

### **Error 422 - Validation Error**
- Verificar el formato de los datos
- Revisar tipos de datos requeridos
- Verificar campos obligatorios

### **Error 502 - Bad Gateway**
- Verificar que el order-service esté corriendo
- Verificar que Docker Compose esté activo
- Revisar logs: `docker logs medisupply-order-service`

## 📚 Recursos Adicionales

- **Swagger UI:** `http://localhost:8080/order-docs`
- **ReDoc:** `http://localhost:8080/order-redoc`
- **API Documentation:** `API_DOCUMENTATION.md`
- **Health Check:** `http://localhost:8080/healthz`

---

*Colecciones creadas para MediSupply Order Service v1.0.0*
