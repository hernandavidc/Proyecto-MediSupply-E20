from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, Optional
import logging
from datetime import datetime
import asyncio

from security_service import security_service
from redis_client import redis_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Security Experiment API", version="1.0.0")
security = HTTPBearer()

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class SecurityEvent(BaseModel):
    event_type: str
    user_id: str
    timestamp: str
    metadata: Dict

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Startup and shutdown events
@app.on_event("startup")
async def startup():
    await redis_client.connect()
    logger.info("Security Experiment API started")

@app.on_event("shutdown")
async def shutdown():
    await redis_client.disconnect()
    logger.info("Security Experiment API stopped")

# Dependency for token validation
async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """Validate JWT token and return user data"""
    return await security_service.validate_token(credentials.credentials, request)

# Authentication endpoints
@app.post("/auth/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, request: Request):
    """Simulate user login and return JWT token"""
    # In real implementation, validate credentials against database
    # For demo purposes, accept any non-empty credentials
    
    if not login_data.username or not login_data.password:
        raise HTTPException(
            status_code=400,
            detail="Username and password required"
        )
    
    # Simulate user validation (always success for demo)
    if login_data.password == "invalid":
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    # Generate token
    token = security_service.create_access_token(
        user_id=login_data.username,
        additional_claims={"role": "user"}
    )
    
    return TokenResponse(access_token=token)

# Protected endpoints
@app.get("/api/protected")
async def protected_endpoint(current_user: Dict = Depends(get_current_user)):
    """Protected endpoint that requires valid JWT"""
    return {
        "message": "Access granted",
        "user_id": current_user["sub"],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/inventory/{sku}")
async def get_inventory(
    sku: str, 
    current_user: Dict = Depends(get_current_user)
):
    """Simulate inventory check - protected endpoint"""
    # Simulate inventory data
    inventory_data = {
        "sku": sku,
        "quantity": 100,
        "location": "Warehouse A",
        "last_updated": datetime.utcnow().isoformat(),
        "accessed_by": current_user["sub"]
    }
    return inventory_data

@app.get("/api/orders/status/{order_id}")
async def get_order_status(
    order_id: str, 
    current_user: Dict = Depends(get_current_user)
):
    """Simulate order status check - protected endpoint"""
    order_data = {
        "order_id": order_id,
        "status": "processing",
        "created_at": "2024-01-01T10:00:00Z",
        "accessed_by": current_user["sub"]
    }
    return order_data

# Security monitoring endpoints
@app.get("/admin/security/events/{user_id}")
async def get_security_events(user_id: str):
    """Get security events for a user (admin endpoint)"""
    # In production, this would require admin authentication
    events = []
    event_keys = await redis_client.redis.keys(f"security_event:{user_id}:*")
    
    for key in event_keys:
        event_data = await redis_client.redis.lrange(key, 0, -1)
        events.extend([eval(event) for event in event_data])
    
    return {"user_id": user_id, "events": events}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        await redis_client.redis.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
