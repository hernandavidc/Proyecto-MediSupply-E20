FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

# Establecer variables de entorno para FastAPI y PostgreSQL
ENV DATABASE_URL=postgresql://admin:admin123@postgres-db:5432/pedidos_db
ENV PYTHONUNBUFFERED=1

# Exponer el puerto en el que correrá FastAPI
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
