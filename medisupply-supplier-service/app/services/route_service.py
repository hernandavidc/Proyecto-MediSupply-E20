import math
from typing import List, Dict, Tuple
from datetime import datetime, timedelta


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two points (in km) using Haversine."""
    R = 6371.0  # Earth radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def estimate_travel_time_minutes(distance_km: float, avg_speed_kmh: float = 40.0) -> int:
    """Estimate travel time in whole minutes given an average speed (km/h)."""
    if avg_speed_kmh <= 0:
        raise ValueError("avg_speed_kmh must be > 0")
    hours = distance_km / avg_speed_kmh
    minutes = int(round(hours * 60))
    return max(minutes, 1) if distance_km > 0 else 0


def nearest_neighbor_order(points: List[Dict]) -> List[int]:
    """Simple nearest-neighbor heuristic returning an ordering of point indices.

    points: list of dicts with 'lat' and 'lon'
    """
    if not points:
        return []
    n = len(points)
    unvisited = set(range(n))
    order = []
    current = 0
    order.append(current)
    unvisited.remove(current)
    while unvisited:
        best = None
        best_dist = None
        for v in unvisited:
            d = haversine_distance_km(points[current]['lat'], points[current]['lon'], points[v]['lat'], points[v]['lon'])
            if best is None or d < best_dist:
                best = v
                best_dist = d
        order.append(best)
        unvisited.remove(best)
        current = best
    return order


def compute_route(points: List[Dict], avg_speed_kmh: float = 40.0):
    """Compute an ordered route and estimated travel times.

    points: list of dicts with keys: id, lat, lon, scheduled_at (optional datetime), duration_minutes (optional)
    Returns dict with total distance and items in sequence.
    """
    if not points:
        return {'total_distance_km': 0.0, 'total_travel_time_minutes': 0, 'items': []}

    # initial order: nearest neighbor
    order = nearest_neighbor_order(points)

    total_distance = 0.0
    total_travel_time = 0
    items = []

    # Build items with distance from previous and travel time estimates
    prev = None
    current_time = None
    for seq, idx in enumerate(order, start=1):
        p = points[idx]
        if prev is None:
            dist = 0.0
            travel_minutes = 0
            # If scheduled_at exists, start from it; otherwise keep None
            current_time = p.get('scheduled_at')
            est_arrival = current_time
        else:
            dist = haversine_distance_km(prev['lat'], prev['lon'], p['lat'], p['lon'])
            travel_minutes = estimate_travel_time_minutes(dist, avg_speed_kmh)
            total_distance += dist
            total_travel_time += travel_minutes
            # estimate arrival time as previous estimated arrival + prev duration + travel
            if current_time is None:
                est_arrival = None
            else:
                prev_duration = prev.get('duration_minutes') or 0
                est_arrival = current_time + timedelta(minutes=prev_duration + travel_minutes)
                current_time = est_arrival

        items.append({
            'visita': p,
            'sequence': seq,
            'distance_from_prev_km': round(dist, 3),
            'travel_time_minutes': travel_minutes,
            'estimated_arrival': est_arrival,
        })
        prev = p

    return {
        'total_distance_km': round(total_distance, 3),
        'total_travel_time_minutes': total_travel_time,
        'items': items,
    }
