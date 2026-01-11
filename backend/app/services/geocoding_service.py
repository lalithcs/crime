"""
Geocoding service to convert coordinates to area names
"""
from typing import Tuple, Optional

# Hyderabad area boundaries (lat_min, lat_max, lng_min, lng_max)
HYDERABAD_AREAS = {
    "Madhapur": {"lat": (17.445, 17.455), "lng": (78.385, 78.400)},
    "Gachibowli": {"lat": (17.435, 17.445), "lng": (78.345, 78.360)},
    "Hitech City": {"lat": (17.445, 17.455), "lng": (78.370, 78.390)},
    "Begumpet": {"lat": (17.440, 17.450), "lng": (78.460, 78.475)},
    "Secunderabad": {"lat": (17.435, 17.445), "lng": (78.495, 78.510)},
    "Banjara Hills": {"lat": (17.410, 17.425), "lng": (78.440, 78.455)},
    "Kukatpally": {"lat": (17.485, 17.500), "lng": (78.390, 78.405)},
    "LB Nagar": {"lat": (17.335, 17.350), "lng": (78.545, 78.560)},
    "Dilsukhnagar": {"lat": (17.365, 17.380), "lng": (78.520, 78.535)},
    "Charminar": {"lat": (17.355, 17.370), "lng": (78.465, 78.480)},
    "Jubilee Hills": {"lat": (17.420, 17.435), "lng": (78.405, 78.420)},
    "Ameerpet": {"lat": (17.435, 17.445), "lng": (78.440, 78.455)},
    "Kondapur": {"lat": (17.460, 17.475), "lng": (78.355, 78.370)},
    "Miyapur": {"lat": (17.495, 17.510), "lng": (78.350, 78.365)},
    "Uppal": {"lat": (17.395, 17.410), "lng": (78.550, 78.565)},
}

# Chicago neighborhoods (simplified)
CHICAGO_AREAS = {
    "Loop": {"lat": (41.875, 41.885), "lng": (-87.635, -87.625)},
    "Lincoln Park": {"lat": (41.910, 41.935), "lng": (-87.650, -87.630)},
    "Hyde Park": {"lat": (41.785, 41.810), "lng": (-87.610, -87.585)},
    "South Loop": {"lat": (41.855, 41.870), "lng": (-87.635, -87.620)},
    "West Loop": {"lat": (41.880, 41.895), "lng": (-87.655, -87.640)},
    "Wicker Park": {"lat": (41.905, 41.915), "lng": (-87.680, -87.665)},
}

def get_area_name(latitude: float, longitude: float) -> str:
    """
    Convert coordinates to area name
    Returns area name or formatted coordinates if no match
    """
    # Check Hyderabad areas
    for area_name, bounds in HYDERABAD_AREAS.items():
        if (bounds["lat"][0] <= latitude <= bounds["lat"][1] and 
            bounds["lng"][0] <= longitude <= bounds["lng"][1]):
            return f"{area_name}, Hyderabad"
    
    # Check Chicago areas
    for area_name, bounds in CHICAGO_AREAS.items():
        if (bounds["lat"][0] <= latitude <= bounds["lat"][1] and 
            bounds["lng"][0] <= longitude <= bounds["lng"][1]):
            return f"{area_name}, Chicago"
    
    # Check if in general Hyderabad area
    if 17.2 <= latitude <= 17.6 and 78.2 <= longitude <= 78.7:
        return f"Hyderabad ({latitude:.3f}, {longitude:.3f})"
    
    # Check if in general Chicago area
    if 41.6 <= latitude <= 42.1 and -87.9 <= longitude <= -87.5:
        return f"Chicago ({latitude:.3f}, {longitude:.3f})"
    
    # Default to coordinates
    return f"({latitude:.4f}, {longitude:.4f})"

def get_nearby_areas(latitude: float, longitude: float, radius_km: float = 2.0) -> list:
    """Get list of nearby area names within radius"""
    nearby = []
    
    # Rough degree approximation (1 degree ≈ 111 km)
    lat_range = radius_km / 111.0
    lng_range = radius_km / (111.0 * abs(latitude) / 90.0) if latitude != 0 else radius_km / 111.0
    
    for area_name, bounds in {**HYDERABAD_AREAS, **CHICAGO_AREAS}.items():
        area_lat_center = (bounds["lat"][0] + bounds["lat"][1]) / 2
        area_lng_center = (bounds["lng"][0] + bounds["lng"][1]) / 2
        
        if (abs(area_lat_center - latitude) <= lat_range and 
            abs(area_lng_center - longitude) <= lng_range):
            nearby.append(area_name)
    
    return nearby
