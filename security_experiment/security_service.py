import jwt
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional
from fastapi import HTTPException, Request
from config import settings
from redis_client import redis_client
import logging

logger = logging.getLogger(__name__)

class SecurityService:
    
    def __init__(self):
        self.private_key = settings.JWT_PRIVATE_KEY
        self.public_key = settings.JWT_PUBLIC_KEY
        self.algorithm = settings.JWT_ALGORITHM
    
    def create_access_token(self, user_id: str, additional_claims: Dict = None) -> str:
        """Generate JWT access token"""
        to_encode = {
            "sub": user_id,
            "exp": datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES),
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        if additional_claims:
            to_encode.update(additional_claims)
        
        encoded_jwt = jwt.encode(
            to_encode, 
            self.private_key, 
            algorithm=self.algorithm
        )
        return encoded_jwt
    
    async def validate_token(self, token: str, request: Request) -> Dict:
        """Validate JWT token and check for suspicious activity"""
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith("Bearer "):
                token = token[7:]
            
            # Decode and validate token
            payload = jwt.decode(
                token, 
                self.public_key, 
                algorithms=[self.algorithm]
            )
            
            user_id = payload.get("sub")
            client_ip = request.client.host
            
            # Check rate limiting
            await self._check_rate_limit(user_id, client_ip)
            
            # Log successful access
            await self._log_access_event(user_id, "valid_access", {
                "ip": client_ip,
                "timestamp": datetime.utcnow().isoformat(),
                "user_agent": request.headers.get("user-agent", "")
            })
            
            return payload
            
        except jwt.ExpiredSignatureError:
            await self._handle_security_violation("expired_token", token, request)
            raise HTTPException(status_code=401, detail="Token expired")
        
        except jwt.InvalidTokenError as e:
            await self._handle_security_violation("invalid_token", str(e), request)
            raise HTTPException(status_code=401, detail="Invalid token")
        
        except HTTPException:
            raise
        
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            raise HTTPException(status_code=500, detail="Authentication service error")
    
    async def _check_rate_limit(self, user_id: str, client_ip: str):
        """Check rate limiting for user and IP"""
        user_key = f"rate_limit:user:{user_id}"
        ip_key = f"rate_limit:ip:{client_ip}"
        
        # Check user rate limit
        user_count = await redis_client.increment_rate_limit(
            user_key, 
            settings.RATE_LIMIT_WINDOW
        )
        
        # Check IP rate limit
        ip_count = await redis_client.increment_rate_limit(
            ip_key, 
            settings.RATE_LIMIT_WINDOW
        )
        
        if user_count > settings.RATE_LIMIT_REQUESTS:
            await self._handle_security_violation("user_rate_limit_exceeded", user_id, None)
            raise HTTPException(
                status_code=429, 
                detail="User rate limit exceeded"
            )
        
        if ip_count > settings.RATE_LIMIT_REQUESTS * 2:  # More lenient for IP
            await self._handle_security_violation("ip_rate_limit_exceeded", client_ip, None)
            raise HTTPException(
                status_code=429, 
                detail="IP rate limit exceeded"
            )
    
    async def _handle_security_violation(self, violation_type: str, identifier: str, request: Optional[Request]):
        """Handle security violations with immediate alerting"""
        violation_data = {
            "type": violation_type,
            "identifier": identifier,
            "timestamp": datetime.utcnow().isoformat(),
            "ip": request.client.host if request else "unknown",
            "user_agent": request.headers.get("user-agent", "") if request else ""
        }
        
        # Log to Redis
        await redis_client.log_access_event("system", violation_type, violation_data)
        
        # Immediate alert (in real implementation, this would send to monitoring system)
        if settings.SECURITY_ALERTS_ENABLED:
            logger.warning(f"SECURITY ALERT: {violation_type} - {json.dumps(violation_data)}")
        
        # Could add webhook, email, or Slack notification here
    
    async def _log_access_event(self, user_id: str, event_type: str, metadata: Dict):
        """Log regular access events"""
        await redis_client.log_access_event(user_id, event_type, metadata)

# Global security service instance
security_service = SecurityService()
