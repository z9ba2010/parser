import math
from typing import Tuple, Optional

def calculate_haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on the earth in kilometers
    using the Haversine formula.
    """
    r = 6371.0 # Earth's radius in kilometers

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    distance = r * c
    return round(distance, 2)

def calculate_bounding_box(lat: float, lon: float, radius_km: float) -> Tuple[float, float, float, float]:
    """
    Calculate a rough bounding box (min_lat, max_lat, min_lon, max_lon)
    for indexed SQL filtering before computing exact haversine distances.
    """
    # 1 deg latitude is approx 111 km
    lat_delta = radius_km / 111.0
    min_lat = lat - lat_delta
    max_lat = lat + lat_delta

    # 1 deg longitude varies with latitude
    lon_delta = radius_km / (111.0 * max(0.1, math.cos(math.radians(lat))))
    min_lon = lon - lon_delta
    max_lon = lon + lon_delta

    return (min_lat, max_lat, min_lon, max_lon)
