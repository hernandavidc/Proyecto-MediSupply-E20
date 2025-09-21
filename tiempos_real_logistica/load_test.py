# load_test.py
import asyncio, aiohttp, random, time

ROUTE_ENGINE = "http://localhost:8100/route"

async def call_route(session):
    origin = (4.648 + random.uniform(-0.02, 0.02), -74.088 + random.uniform(-0.02, 0.02))
    dest = (4.7 + random.uniform(-0.02, 0.02), -74.05 + random.uniform(-0.02, 0.02))
    payload = {"origin": origin, "destination": dest, "waypoints": []}
    t0 = time.time()
    async with session.post(ROUTE_ENGINE, json=payload, timeout=30) as r:
        await r.json()
    return time.time() - t0

async def run(n=100, concurrency=10):
    sem = asyncio.Semaphore(concurrency)
    async with aiohttp.ClientSession() as session:
        async def worker(i):
            async with sem:
                return await call_route(session)
        tasks = [worker(i) for i in range(n)]
        results = await asyncio.gather(*tasks)

    results.sort()
    p50 = results[int(len(results)*0.5)]
    p95 = results[int(len(results)*0.95)-1]
    p99 = results[int(len(results)*0.99)-1] if len(results) >= 100 else max(results)

    print(f"P50: {p50:.3f}s  P95: {p95:.3f}s  P99: {p99:.3f}s")
    print(f"<=3s: {len([r for r in results if r<=3.0])}/{len(results)}")
    print(f"<=5s: {len([r for r in results if r<=5.0])}/{len(results)}")

if __name__ == "__main__":
    asyncio.run(run(n=200, concurrency=20))
