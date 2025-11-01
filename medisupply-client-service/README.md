# MediSupply Client Service

Client management microservice for institutional client registration and NIT validation.

## Overview

The Client Service handles the registration and management of institutional clients for the MediSupply platform. It provides automatic tax identification (NIT) validation and integrates with national business registries.

## Features

- **Client Registration**: Register institutional clients with comprehensive contact information
- **Automatic NIT Validation**: Validate tax identification numbers against business registries
- **CRUD Operations**: Complete management of client information
- **Swagger Documentation**: Full OpenAPI/Swagger documentation
- **Health Checks**: Kubernetes-ready health and readiness probes

## User Story Implementation

**MSCM-HU-CL-001-MOV**: Register Institutional Client

As a future MediSupply client, I want to register quickly with automatic validation, so I can start using the products offered by the company.

## Technology Stack

- **Python**: 3.13+
- **Framework**: FastAPI
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Testing**: pytest
- **Containerization**: Docker

## API Endpoints

### Client Management

- `POST /api/v1/clientes` - Register new client
- `GET /api/v1/clientes` - List all clients (paginated)
- `GET /api/v1/clientes/{client_id}` - Get client by ID
- `GET /api/v1/clientes/by-nit/{nit}` - Get client by NIT
- `PUT /api/v1/clientes/{client_id}` - Update client
- `DELETE /api/v1/clientes/{client_id}` - Delete client
- `POST /api/v1/clientes/{client_id}/validate` - Mark as validated

### NIT Validation

- `GET /api/v1/clientes/validate-nit/{nit}` - Validate NIT and get company info

### System

- `GET /health` - Health check
- `GET /docs` - Swagger documentation
- `GET /redoc` - ReDoc documentation

## Data Model

### Client

```python
{
    "id": "uuid",
    "nombre": "Company Name",
    "nit": "1234567890",
    "direccion": "Company Address",
    "nombre_contacto": "Contact Name",
    "telefono_contacto": "+1234567890",
    "email_contacto": "contact@company.com",
    "is_validated": boolean,
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

## Development

### Prerequisites

- Python 3.13+
- PostgreSQL 15
- Docker and Docker Compose (for local development)

### Local Setup with Docker

1. **Start all services**
   ```bash
   docker-compose up -d
   ```

2. **View logs**
   ```bash
   docker-compose logs -f medisupply-client-service
   ```

3. **Stop services**
   ```bash
   docker-compose down
   ```

The service will be available at http://localhost:8002

### Local Setup without Docker

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   export DATABASE_URL="postgresql://client_user:client_password@localhost:5435/clients_db"
   export DEBUG=true
   ```

4. **Run the service**
   ```bash
   uvicorn app.main:app --reload --port 8002
   ```

5. **Access documentation**
   - Swagger UI: http://localhost:8002/docs
   - ReDoc: http://localhost:8002/redoc

## Testing

### Run all tests
```bash
pytest tests/ -v
```

### Run with coverage
```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

### Run specific test types
```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `sqlite:///./clients.db` |
| `DEBUG` | Enable debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `NIT_VALIDATION_SERVICE_URL` | External NIT validation service | `None` |

## Deployment

### Docker Compose

The service is configured in `docker-compose.yml` and can be started with:

```bash
docker-compose up -d medisupply-client-service
```

### Kubernetes

The service is deployed to Google Kubernetes Engine (GKE) using the manifests in `k8s/services/client-service/`.

```bash
# Apply all manifests
kubectl apply -f k8s/services/client-service/

# Check deployment status
kubectl get pods -n medisupply -l app=client-service

# View logs
kubectl logs -n medisupply -l app=client-service --tail=100
```

### CI/CD

Automatic deployment is handled by GitHub Actions on push to `main` branch.

## NIT Validation Integration

The service includes a mock NIT validation implementation. For production, integrate with your country's business registry:

- **Colombia**: DIAN API
- **Chile**: SII API
- **Peru**: SUNAT API
- **etc.**

Update `app/services/client_service.py` with the actual API integration.

## Security Considerations

- All sensitive configuration stored in Kubernetes Secrets
- Input validation using Pydantic schemas
- Email validation for contact information
- NIT format validation
- SQL injection prevention through SQLAlchemy ORM

## Monitoring

- Health checks available at `/health`
- Kubernetes liveness and readiness probes configured
- Horizontal Pod Autoscaler (HPA) for auto-scaling

## Contributing

1. Follow the MediSupply coding standards
2. Write tests for new features
3. Update documentation
4. Ensure all tests pass before committing

## License

Copyright © 2024 MediSupply. All rights reserved.

