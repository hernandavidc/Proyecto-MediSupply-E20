FROM python:3.11-slim

# Establecer variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema y herramientas necesarias
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    libpq-dev \
    netcat-traditional \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip

# Copiar y instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Crear usuario no-root para seguridad
RUN adduser --disabled-password --gecos '' appuser

# Copiar el código de la aplicación y scripts
COPY . .
COPY start.sh /app/start.sh

# Dar permisos de ejecución a los scripts
RUN chmod +x /app/start.sh && \
    chown -R appuser:appuser /app

USER appuser

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["/app/start.sh"]
