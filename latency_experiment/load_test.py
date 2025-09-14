#!/usr/bin/env python3
"""
Load testing script for Critical Query Latency Experiment
"""
import asyncio
import httpx
import time
import random
import json
import numpy as np
from typing import List, Dict
from datetime import datetime

class LatencyTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
        self.results = {
            "inventory_queries": [],
            "order_status_queries": [],
            "product_location_queries": []
        }
    
    async def test_inventory_latency(self, concurrent_users: int = 50, duration: int = 60):
        """Test inventory query latency under load"""
        print(f"Testing inventory queries with {concurrent_users} concurrent users for {duration}s")
        
        # Generate test SKUs
        test_skus = [f"MED{i:06d}" for i in range(1, 1001)]
        
        async def worker():
            start_time = time.time()
            local_results = []
            
            while time.time() - start_time < duration:
                sku = random.choice(test_skus)
                query_start = time.time()
                
                try:
                    response = await self.client.get(f"/api/inventory/{sku}")
                    query_time = time.time() - query_start
                    
                    local_results.append({
                        "sku": sku,
                        "response_time": query_time,
                        "status_code": response.status_code,
                        "cache_hit": query_time < 0.1,  # Assume cache if very fast
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                    # Small delay to avoid overwhelming
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    local_results.append({
                        "sku": sku,
                        "response_time": -1,
                        "status_code": 500,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            return local_results
        
        # Run concurrent workers
        tasks = [worker() for _ in range(concurrent_users)]
        worker_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        for worker_result in worker_results:
            if isinstance(worker_result, list):
                self.results["inventory_queries"].extend(worker_result)
    
    async def test_order_status_latency(self, concurrent_users: int = 30, duration: int = 60):
        """Test order status query latency under load"""
        print(f"Testing order status queries with {concurrent_users} concurrent users for {duration}s")
        
        # Generate test order numbers
        test_orders = [f"ORD{i:06d}" for i in range(1, 501)]
        
        async def worker():
            start_time = time.time()
            local_results = []
            
            while time.time() - start_time < duration:
                order_number = random.choice(test_orders)
                query_start = time.time()
                
                try:
                    response = await self.client.get(f"/api/orders/{order_number}/status")
                    query_time = time.time() - query_start
                    
                    local_results.append({
                        "order_number": order_number,
                        "response_time": query_time,
                        "status_code": response.status_code,
                        "cache_hit": query_time < 0.05,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                    await asyncio.sleep(0.08)
                    
                except Exception as e:
                    local_results.append({
                        "order_number": order_number,
                        "response_time": -1,
                        "status_code": 500,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            return local_results
        
        # Run concurrent workers
        tasks = [worker() for _ in range(concurrent_users)]
        worker_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        for worker_result in worker_results:
            if isinstance(worker_result, list):
                self.results["order_status_queries"].extend(worker_result)
    
    async def test_product_location_latency(self, concurrent_users: int = 20, duration: int = 60):
        """Test product location query latency"""
        print(f"Testing product location queries with {concurrent_users} concurrent users for {duration}s")
        
        test_skus = [f"MED{i:06d}" for i in range(1, 101)]  # Smaller set for location queries
        
        async def worker():
            start_time = time.time()
            local_results = []
            
            while time.time() - start_time < duration:
                sku = random.choice(test_skus)
                query_start = time.time()
                
                try:
                    response = await self.client.get(f"/api/inventory/{sku}/locations")
                    query_time = time.time() - query_start
                    
                    local_results.append({
                        "sku": sku,
                        "response_time": query_time,
                        "status_code": response.status_code,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                    await asyncio.sleep(0.2)
                    
                except Exception as e:
                    local_results.append({
                        "sku": sku,
                        "response_time": -1,
                        "status_code": 500,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            return local_results
        
        tasks = [worker() for _ in range(concurrent_users)]
        worker_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for worker_result in worker_results:
            if isinstance(worker_result, list):
                self.results["product_location_queries"].extend(worker_result)
    
    def analyze_results(self):
        """Analyze and report test results"""
        print("\n" + "="*60)
        print("LATENCY EXPERIMENT RESULTS")
        print("="*60)
        
        for query_type, results in self.results.items():
            if not results:
                continue
                
            print(f"\n{query_type.upper()}")
            print("-" * 40)
            
            # Filter successful queries
            successful = [r for r in results if r["response_time"] > 0]
            
            if not successful:
                print("No successful queries recorded")
                continue
            
            response_times = [r["response_time"] for r in successful]
            
            # Calculate percentiles
            p50 = np.percentile(response_times, 50)
            p95 = np.percentile(response_times, 95)
            p99 = np.percentile(response_times, 99)
            avg = np.mean(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            # Determine SLA based on query type
            if "inventory" in query_type:
                sla = 2.0
            else:
                sla = 1.0
            
            # Calculate SLA compliance
            compliant = sum(1 for t in response_times if t <= sla)
            compliance_rate = (compliant / len(response_times)) * 100
            
            # Cache hit rate for applicable queries
            cache_hits = sum(1 for r in successful if r.get("cache_hit", False))
            cache_hit_rate = (cache_hits / len(successful)) * 100 if successful else 0
            
            print(f"Total queries: {len(results)}")
            print(f"Successful queries: {len(successful)}")
            print(f"Average response time: {avg:.3f}s")
            print(f"P50 response time: {p50:.3f}s")
            print(f"P95 response time: {p95:.3f}s")
            print(f"P99 response time: {p99:.3f}s")
            print(f"Min response time: {min_time:.3f}s")
            print(f"Max response time: {max_time:.3f}s")
            print(f"SLA ({sla}s) compliance: {compliance_rate:.1f}%")
            
            if "inventory" in query_type or "order_status" in query_type:
                print(f"Cache hit rate: {cache_hit_rate:.1f}%")
            
            # SLA validation
            if compliance_rate >= 95:
                print(f"✅ SLA PASSED: {compliance_rate:.1f}% >= 95%")
            else:
                print(f"❌ SLA FAILED: {compliance_rate:.1f}% < 95%")
    
    async def run_comprehensive_test(self):
        """Run all latency tests"""
        print("Starting Comprehensive Latency Testing")
        print("=" * 60)
        
        # Test inventory queries
        await self.test_inventory_latency(concurrent_users=50, duration=120)
        
        # Brief pause
        await asyncio.sleep(5)
        
        # Test order status queries  
        await self.test_order_status_latency(concurrent_users=30, duration=120)
        
        # Brief pause
        await asyncio.sleep(5)
        
        # Test product location queries
        await self.test_product_location_latency(concurrent_users=20, duration=60)
        
        # Analyze and report results
        self.analyze_results()
        
        # Save detailed results
        with open("latency_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nDetailed results saved to: latency_test_results.json")
    
    async def close(self):
        await self.client.aclose()

async def main():
    tester = LatencyTester()
    try:
        await tester.run_comprehensive_test()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())
