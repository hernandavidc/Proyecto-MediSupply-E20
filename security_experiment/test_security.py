import pytest
import asyncio
import httpx
import time
from security_service import security_service

# Test configuration
API_BASE_URL = "http://localhost:8000"

class TestSecurityExperiment:
    
    @pytest.fixture
    def client(self):
        return httpx.AsyncClient(base_url=API_BASE_URL)
    
    @pytest.mark.asyncio
    async def test_valid_login_and_access(self, client):
        """Test normal authentication flow"""
        # Login
        login_response = await client.post("/auth/login", json={
            "username": "test_user",
            "password": "test_pass"
        })
        
        assert login_response.status_code == 200
        token_data = login_response.json()
        assert "access_token" in token_data
        
        # Access protected endpoint
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        protected_response = await client.get("/api/protected", headers=headers)
        
        assert protected_response.status_code == 200
        data = protected_response.json()
        assert data["user_id"] == "test_user"
    
    @pytest.mark.asyncio
    async def test_invalid_token_detection(self, client):
        """Test detection of invalid tokens"""
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = await client.get("/api/protected", headers=headers)
        
        assert response.status_code == 401
        assert "invalid token" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, client):
        """Test rate limiting functionality"""
        # Get valid token
        login_response = await client.post("/auth/login", json={
            "username": "rate_test_user",
            "password": "test_pass"
        })
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Make requests quickly to trigger rate limit
        success_count = 0
        rate_limited_count = 0
        
        for i in range(105):  # More than rate limit
            response = await client.get("/api/protected", headers=headers)
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                rate_limited_count += 1
        
        assert rate_limited_count > 0  # Should trigger rate limiting
        print(f"Success: {success_count}, Rate Limited: {rate_limited_count}")
    
    @pytest.mark.asyncio
    async def test_expired_token_detection(self, client):
        """Test expired token detection"""
        # Create token with very short expiration
        expired_token = security_service.create_access_token(
            "test_user", 
            {"exp": int(time.time()) - 100}  # Already expired
        )
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = await client.get("/api/protected", headers=headers)
        
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_response_time_requirement(self, client):
        """Test that security validation happens within 2 seconds"""
        # Get valid token
        login_response = await client.post("/auth/login", json={
            "username": "timing_test_user",
            "password": "test_pass"
        })
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Measure response time for protected endpoint
        start_time = time.time()
        response = await client.get("/api/protected", headers=headers)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0  # Must be under 2 seconds
        print(f"Security validation response time: {response_time:.3f}s")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
