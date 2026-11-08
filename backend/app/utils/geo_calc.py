import math

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two GPS coordinates in kilometers."""
    R = 6371.0 # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def calculate_speed_kmh(lat1: float, lon1: float, t1: float, lat2: float, lon2: float, t2: float) -> float:
    """Calculates implied physical travel velocity in km/h between two transactions."""
    dist_km = haversine_distance(lat1, lon1, lat2, lon2)
    time_diff_hours = abs(t2 - t1) / 3600.0
    if time_diff_hours <= 0.0001:
        return 99999.0 if dist_km > 10.0 else 0.0
    return round(dist_km / time_diff_hours, 2)

