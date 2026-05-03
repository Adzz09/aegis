import math
import numpy as np
from shapely.geometry import Point, Polygon
from shapely.ops import transform
import pyproj

# WGS84 coordinate system
WGS84 = pyproj.CRS('EPSG:4326')
# Web Mercator for planar calculations (meters)
WEB_MERCATOR = pyproj.CRS('EPSG:3857')

PROJECT_TO_METERS = pyproj.Transformer.from_crs(WGS84, WEB_MERCATOR, always_xy=True).transform
PROJECT_TO_LATLON = pyproj.Transformer.from_crs(WEB_MERCATOR, WGS84, always_xy=True).transform

def get_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates Haversine distance between two points in meters."""
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def create_range_circle(lat: float, lon: float, radius_m: float) -> Polygon:
    """Creates a circular Polygon around a point with a given radius in meters."""
    center = Point(lon, lat)
    # Project to meters
    center_m = transform(PROJECT_TO_METERS, center)
    # Create buffer in meters
    circle_m = center_m.buffer(radius_m)
    # Project back to lat/lon
    circle_latlon = transform(PROJECT_TO_LATLON, circle_m)
    return circle_latlon

def is_point_in_zone(lat: float, lon: float, zone_polygon: Polygon) -> bool:
    """Checks if a lat/lon point is inside a zone polygon."""
    return zone_polygon.contains(Point(lon, lat))

def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates initial bearing from point 1 to point 2 in degrees."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlambda = math.radians(lon2 - lon1)
    
    y = math.sin(dlambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlambda)
    
    bearing = math.atan2(y, x)
    return (math.degrees(bearing) + 360) % 360
