from datetime import datetime, timedelta
from app.services.route_service import (
    haversine_distance_km,
    estimate_travel_time_minutes,
    nearest_neighbor_order,
    compute_route,
)


def test_haversine_distance_zero():
    d = haversine_distance_km(0, 0, 0, 0)
    assert d == 0.0


def test_estimate_travel_time_rounding_and_min():
    # small distance yields at least 1 minute
    m = estimate_travel_time_minutes(0.01, avg_speed_kmh=40)
    assert isinstance(m, int) and m >= 1

    # zero distance returns 0
    assert estimate_travel_time_minutes(0.0, avg_speed_kmh=40) == 0

    # invalid speed
    try:
        estimate_travel_time_minutes(10, avg_speed_kmh=0)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_nearest_neighbor_simple():
    pts = [
        {'lat': 0.0, 'lon': 0.0},
        {'lat': 0.0, 'lon': 1.0},
        {'lat': 1.0, 'lon': 0.0},
    ]
    order = nearest_neighbor_order(pts)
    assert set(order) == {0, 1, 2}
    assert order[0] == 0


def test_compute_route_with_schedule_and_durations():
    now = datetime.utcnow()
    pts = [
        {'id': 1, 'lat': 0.0, 'lon': 0.0, 'scheduled_at': now, 'duration_minutes': 10},
        {'id': 2, 'lat': 0.0, 'lon': 0.1, 'scheduled_at': None, 'duration_minutes': 5},
        {'id': 3, 'lat': 0.1, 'lon': 0.0, 'scheduled_at': None, 'duration_minutes': 0},
    ]
    route = compute_route(pts, avg_speed_kmh=60.0)
    assert 'total_distance_km' in route
    assert route['total_travel_time_minutes'] >= 0
    assert len(route['items']) == 3
    # first item's distance_from_prev_km should be 0
    assert route['items'][0]['distance_from_prev_km'] == 0.0
