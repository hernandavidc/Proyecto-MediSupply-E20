echo "🚀 Iniciando script de inicialización de base de datos..."

# Ejecutar el script de inicialización (ya esperamos en wait-for-db)
echo "📊 Ejecutando inicialización de datos..."
cd /app

# Intentar conectar varias veces antes de fallar
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    echo "Intento $((RETRY_COUNT + 1)) de $MAX_RETRIES..."
    
    if python scripts/init_database.py; then
        echo "🎉 Inicialización completada exitosamente"
        exit 0
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            echo "Reintentando en 3 segundos..."
            sleep 3
        fi
    fi
done

echo "❌ Falló después de $MAX_RETRIES intentos"
exit 1
