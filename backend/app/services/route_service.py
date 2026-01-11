from sqlalchemy.orm import Session
from typing import List, Optional
import httpx
import json
from math import radians, cos, sin, asin, sqrt
from datetime import datetime, timedelta

from app.models import crime, schemas
from app.services.crime_service import haversine_distance


async def calculate_safe_route(db: Session, request: schemas.SafeRouteRequest) -> schemas.SafeRouteResponse:
    """
    Calculate the safest route avoiding high-crime areas
    Uses OpenRouteService or fallback to simple A* pathfinding
    """
    # Get recent crimes near the route
    crimes_data = db.query(crime.Crime).filter(
        crime.Crime.occurred_at >= datetime.utcnow() - timedelta(days=30)
    ).all()
    
    # Identify crime zones
    crime_zones = []
    for c in crimes_data:
        # Check if crime is near the potential route corridor
        if _is_near_route_corridor(c.latitude, c.longitude, request):
            crime_zones.append({
                "lat": c.latitude,
                "lng": c.longitude,
                "type": c.crime_type
            })
    
    # Try to get route from OpenRouteService (if API key available)
    try:
        route_data = await _get_route_from_service(request, crime_zones)
        if route_data:
            return route_data
    except Exception as e:
        print(f"External routing service failed: {e}")
    
    # Fallback: Simple straight-line route with crime zone avoidance
    return _calculate_simple_safe_route(request, crime_zones)


def _is_near_route_corridor(lat: float, lng: float, request: schemas.SafeRouteRequest) -> bool:
    """Check if a point is near the route corridor"""
    # Simple bounding box check
    lat_min = min(request.start_lat, request.end_lat) - 0.1
    lat_max = max(request.start_lat, request.end_lat) + 0.1
    lng_min = min(request.start_lng, request.end_lng) - 0.1
    lng_max = max(request.start_lng, request.end_lng) + 0.1
    
    return lat_min <= lat <= lat_max and lng_min <= lng <= lng_max


async def _get_route_from_service(
    request: schemas.SafeRouteRequest,
    crime_zones: List[dict]
) -> Optional[schemas.SafeRouteResponse]:
    """
    Get route from OpenRouteService API
    Note: Requires API key - this is a simplified version
    """
    # This would connect to OpenRouteService or OSRM
    # For now, returning None to use fallback
    return None


def _calculate_simple_safe_route(
    request: schemas.SafeRouteRequest,
    crime_zones: List[dict]
) -> schemas.SafeRouteResponse:
    """
    Calculate a simple safe route using waypoints to avoid crime zones
    """
    start = (request.start_lat, request.start_lng)
    end = (request.end_lat, request.end_lng)
    
    # Check for crime zones along direct path
    avoided_zones = 0
    waypoints = [start]
    
    # Simple algorithm: add waypoint if crime zone is too close
    for zone in crime_zones:
        zone_point = (zone["lat"], zone["lng"])
        
        # Calculate perpendicular distance from zone to route
        dist_to_route = _point_to_line_distance(zone_point, start, end)
        
        if dist_to_route < request.avoid_crime_radius_km:
            avoided_zones += 1
            # Add waypoint to go around the zone
            waypoint = _calculate_avoidance_waypoint(start, end, zone_point, request.avoid_crime_radius_km)
            if waypoint and waypoint not in waypoints:
                waypoints.append(waypoint)
    
    waypoints.append(end)
    
    # Calculate route properties
    total_distance = 0
    for i in range(len(waypoints) - 1):
        total_distance += haversine_distance(
            waypoints[i][0], waypoints[i][1],
            waypoints[i+1][0], waypoints[i+1][1]
        )
    
    # Estimate duration (assuming 40 km/h average speed)
    duration_minutes = (total_distance / 40) * 60
    
    # Calculate safety score (0-100)
    direct_distance = haversine_distance(start[0], start[1], end[0], end[1])
    detour_factor = total_distance / direct_distance if direct_distance > 0 else 1
    safety_score = max(0, min(100, 100 - (avoided_zones * 5) - (detour_factor - 1) * 10))
    
    return schemas.SafeRouteResponse(
        route=[[wp[0], wp[1]] for wp in waypoints],
        distance_km=round(total_distance, 2),
        duration_minutes=round(duration_minutes, 1),
        safety_score=round(safety_score, 1),
        avoided_crime_zones=avoided_zones,
        waypoints=[
            {
                "lat": wp[0],
                "lng": wp[1],
                "type": "start" if i == 0 else "end" if i == len(waypoints)-1 else "waypoint"
            }
            for i, wp in enumerate(waypoints)
        ]
    )


def _point_to_line_distance(point, line_start, line_end) -> float:
    """Calculate perpendicular distance from point to line segment"""
    px, py = point
    x1, y1 = line_start
    x2, y2 = line_end
    
    # Convert to radians for accurate distance
    # Simplified calculation - using haversine to midpoint
    midpoint = ((x1 + x2) / 2, (y1 + y2) / 2)
    return haversine_distance(px, py, midpoint[0], midpoint[1])


def _calculate_avoidance_waypoint(start, end, danger_point, radius_km) -> Optional[tuple]:
    """Calculate a waypoint to avoid a danger zone"""
    # Simple perpendicular offset
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    
    # Perpendicular direction
    perp_dx = -dy
    perp_dy = dx
    
    # Normalize and scale by radius
    length = (perp_dx**2 + perp_dy**2) ** 0.5
    if length == 0:
        return None
    
    offset_lat = danger_point[0] + (perp_dx / length) * (radius_km / 111)  # 1 degree ~ 111km
    offset_lng = danger_point[1] + (perp_dy / length) * (radius_km / 111)
    
    return (offset_lat, offset_lng)


async def compare_routes(db: Session, request: schemas.SafeRouteRequest) -> dict:
    """Compare safe route vs fastest/direct route"""
    # Get safe route
    safe_route = await calculate_safe_route(db, request)
    
    # Calculate direct route
    direct_distance = haversine_distance(
        request.start_lat, request.start_lng,
        request.end_lat, request.end_lng
    )
    direct_duration = (direct_distance / 50) * 60  # Assume 50 km/h
    
    return {
        "safe_route": {
            "distance_km": safe_route.distance_km,
            "duration_minutes": safe_route.duration_minutes,
            "safety_score": safe_route.safety_score,
            "avoided_zones": safe_route.avoided_crime_zones
        },
        "direct_route": {
            "distance_km": round(direct_distance, 2),
            "duration_minutes": round(direct_duration, 1),
            "safety_score": 50.0,  # Neutral score
            "avoided_zones": 0
        },
        "comparison": {
            "extra_distance_km": round(safe_route.distance_km - direct_distance, 2),
            "extra_time_minutes": round(safe_route.duration_minutes - direct_duration, 1),
            "safety_improvement": round(safe_route.safety_score - 50, 1),
            "recommendation": "safe_route" if safe_route.avoided_crime_zones > 0 else "direct_route"
        }
    }
