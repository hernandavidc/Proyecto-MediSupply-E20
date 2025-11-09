# Script de Stress Testing - MediSupply

Este script está diseñado para estresar el sistema MediSupply ejecutando múltiples requests a diferentes endpoints de la API.

## 📋 Descripción

El script realiza las siguientes operaciones:

- **Registro de usuarios**: Crea usuarios de prueba para testing
- **Generación de tokens**: Obtiene tokens JWT para autenticación
- **Consultas a catálogos**: 
  - Certificaciones sanitarias
  - Categorías de suministros
  - Países
- **Consultas a recursos**:
  - Listar proveedores
  - Listar productos
  - Listar planes
- **Health checks**: Verifica el estado del sistema
- **Endpoints protegidos**: Prueba endpoints que requieren autenticación

## 🚀 Cómo ejecutar el script

### Prerrequisitos

1. Tener `bash` instalado (viene por defecto en macOS y Linux)
2. Tener `curl` instalado (viene por defecto en macOS y Linux)
3. Tener `jq` instalado para formatear JSON (opcional pero recomendado)

#### Instalar jq (si no lo tienes)

**macOS:**
```bash
brew install jq
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install jq
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install jq
```

### Ejecución

1. **Navegar a la carpeta del proyecto:**
   ```bash
   cd /Users/proyects/Proyecto-MediSupply-E20
   ```

2. **Dar permisos de ejecución al script (solo la primera vez):**
   ```bash
   chmod +x scripts/stress-test/stress_test.sh
   ```

3. **Ejecutar el script:**
   ```bash
   ./scripts/stress-test/stress_test.sh
   ```

   O desde la carpeta del script:
   ```bash
   cd scripts/stress-test
   ./stress_test.sh
   ```

## ⚙️ Configuración

Puedes modificar las variables al inicio del script para ajustar el comportamiento:

```bash
BASE_URL="https://medisupply-edge-proxy-n5jhaxtfma-uc.a.run.app/api/v1"
BASE_URL_NO_API="https://medisupply-edge-proxy-n5jhaxtfma-uc.a.run.app"
ITERATIONS=5          # Número de iteraciones por ciclo
PARALLEL_REQUESTS=5   # Requests en paralelo (actualmente no usado)
```

Y también el número de ciclos:
```bash
CYCLES=3  # Número de ciclos de stress test
```

## 📊 Interpretación de los resultados

El script muestra:

- ✅ **Verde**: Request exitoso (HTTP 200-299)
- ❌ **Rojo**: Request fallido (HTTP 400+ o error)
- ⚠️ **Amarillo**: Advertencia (usuario ya existe, etc.)

Al final de cada ciclo verás un resumen:
- ✅ Exitosos: Número de requests exitosos
- ❌ Fallidos: Número de requests fallidos
- 📈 Total: Total de requests realizados

## 📝 Notas

- El script está configurado para usar el dominio de producción de Cloud Run
- Los usuarios de prueba se crean con el dominio `@mail.com`
- El script hace pausas pequeñas entre requests para no sobrecargar el sistema
- Algunos endpoints pueden no existir (como `/planes`) y mostrarán 404, esto es normal

## 🛑 Detener el script

Para detener el script mientras se ejecuta, presiona `Ctrl + C` en la terminal.

