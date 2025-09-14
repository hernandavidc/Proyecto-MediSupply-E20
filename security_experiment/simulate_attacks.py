#!/usr/bin/env python3
"""
Script to simulate various attack patterns for security testing
"""
import asyncio
import httpx
import time
import random
from typing import List

API_BASE_URL = "http://localhost:8000"

class SecuritySimulator:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=API_BASE_URL)
    
    async def simulate_brute_force_attack(self, username: str, attempts: int = 50):
        """Simulate brute force login attempts"""
        print(f"Simulating brute force attack on user: {username}")
        
        failed_attempts = 0
        for i in range(attempts):
            fake_password = f"wrong_pass_{i}"
            
            start_time = time.time()
            response = await self.client.post("/auth/login", json={
                "username": username,
                "password": fake_password
            })
            end_time = time.time()
            
            if response.status_code == 401:
                failed_attempts += 1
            
            # Check if detection happens within 2 seconds
            detection_time = end_time - start_time
            print(f"Attempt {i+1}: Status {response.status_code}, Time: {detection_time:.3f}s")
            
            # Brief pause to avoid overwhelming the server
            await asyncio.sleep(0.1)
        
        print(f"Brute force simulation complete. Failed attempts: {failed_attempts}/{attempts}")
    
    async def simulate_token_manipulation_attack(self):
        """Simulate various token manipulation attempts"""
        print("Simulating token manipulation attacks")
        
        # Get a valid token first
        login_response = await self.client.post("/auth/login", json={
            "username": "valid_user",
            "password": "valid_pass"
        })
        
        if login_response.status_code == 200:
            valid_token = login_response.json()["access_token"]
            
            # Test various manipulated tokens
            manipulated_tokens = [
                "invalid.token.here",
                valid_token[:-10] + "manipulated",  # Modified signature
                "eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.eyJ1c2VyIjoiYWRtaW4ifQ.",  # None algorithm
                valid_token + "extra_chars",  # Extended token
                "empty_token",  # Empty-like token
                valid_token + "_malicious_suffix"  # Suffix attack
            ]
            
            for i, token in enumerate(manipulated_tokens):
                headers = {"Authorization": f"Bearer {token}"}
                
                start_time = time.time()
                response = await self.client.get("/api/protected", headers=headers)
                end_time = time.time()
                
                detection_time = end_time - start_time
                print(f"Token manipulation {i+1}: Status {response.status_code}, Time: {detection_time:.3f}s")
                
                await asyncio.sleep(0.1)
    
    async def simulate_rate_limit_attack(self, user_count: int = 3):
        """Simulate coordinated rate limiting attack"""
        print(f"Simulating rate limit attack with {user_count} users")
        
        # Get tokens for multiple users
        tokens = []
        for i in range(user_count):
            username = f"attack_user_{i}"
            login_response = await self.client.post("/auth/login", json={
                "username": username,
                "password": "test_pass"
            })
            
            if login_response.status_code == 200:
                tokens.append(login_response.json()["access_token"])
        
        # Rapid-fire requests from all users
        tasks = []
        for token in tokens:
            task = self._rapid_requests(token, 150)  # Above rate limit
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_blocked = sum(result["blocked"] for result in results if isinstance(result, dict))
        total_successful = sum(result["successful"] for result in results if isinstance(result, dict))
        
        print(f"Rate limit attack results: {total_successful} successful, {total_blocked} blocked")
    
    async def _rapid_requests(self, token: str, count: int) -> dict:
        """Make rapid requests with a single token"""
        headers = {"Authorization": f"Bearer {token}"}
        successful = 0
        blocked = 0
        
        for _ in range(count):
            try:
                response = await self.client.get("/api/protected", headers=headers)
                if response.status_code == 200:
                    successful += 1
                elif response.status_code == 429:
                    blocked += 1
            except Exception as e:
                print(f"Request failed: {e}")
            
            # Very brief pause
            await asyncio.sleep(0.01)
        
        return {"successful": successful, "blocked": blocked}
    
    async def run_full_security_test(self):
        """Run comprehensive security test suite"""
        print("Starting comprehensive security simulation")
        print("=" * 50)
        
        # Test 1: Brute force
        await self.simulate_brute_force_attack("admin", 25)
        print("\n")
        
        # Test 2: Token manipulation
        await self.simulate_token_manipulation_attack()
        print("\n")
        
        # Test 3: Rate limiting
        await self.simulate_rate_limit_attack(3)
        print("\n")
        
        print("Security simulation complete!")
    
    async def close(self):
        await self.client.aclose()

async def main():
    simulator = SecuritySimulator()
    try:
        await simulator.run_full_security_test()
    finally:
        await simulator.close()

if __name__ == "__main__":
    asyncio.run(main())
