# gps_simulator.py
import asyncio, json, random, time
import redis.asyncio as redis

REDIS_URL = "redis://localhost:6379"
CHANNEL = "gps_updates"

async def run(n_trucks=20, period_s=0.5, duration_s=60):
    r = redis.from_url(REDIS_URL)
    seed_lat, seed_lon = 4.6482837, -74.0880836
    positions = [[seed_lat + random.uniform(-0.01, 0.01), seed_lon + random.uniform(-0.01, 0.01)] for _ in range(n_trucks)]

    start = time.time()
    seq = 0
    while time.time() - start < duration_s:
        for t in range(n_trucks):
            positions[t][0] += random.uniform(-0.0005, 0.0005)
            positions[t][1] += random.uniform(-0.0005, 0.0005)
            payload = {
                "truck_id": t,
                "lat": positions[t][0],
                "lon": positions[t][1],
                "ts_publish": time.time(),
                "seq": seq
            }
            await r.publish(CHANNEL, json.dumps(payload))
            seq += 1
        await asyncio.sleep(period_s)

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=20)
    p.add_argument("--period", type=float, default=0.5)
    p.add_argument("--duration", type=int, default=60)
    args = p.parse_args()
    asyncio.run(run(n_trucks=args.n, period_s=args.period, duration_s=args.duration))
