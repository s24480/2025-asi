import requests
import json

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError


def _get_coordinates_from_address(address: str) -> tuple[float, float] | None:
    geolocator = Nominatim(user_agent="taxi_fare_app", timeout=20)
    try:
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
        else:
            return None
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        return None
    except Exception as e:
        return None


def _get_travel_time_osrm(start_coords: tuple[float, float], end_coords: tuple[float, float]) -> dict | None:
    lon_a, lat_a = start_coords[1], start_coords[0]
    lon_b, lat_b = end_coords[1], end_coords[0]

    osrm_url = f"http://router.project-osrm.org/route/v1/driving/{lon_a},{lat_a};{lon_b},{lat_b}"

    params = {
        "overview": "false",
        "alternatives": "false",
        "steps": "false",
        "geometries": "polyline",
        "annotations": "false"
    }

    try:
        response = requests.get(osrm_url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data and data['code'] == 'Ok' and data['routes']:
            duration_seconds = data['routes'][0]['duration']
            distance_meters = data['routes'][0]['distance']
            return {
                "duration": duration_seconds,
                "distance": distance_meters
            }
        elif data and data['code'] != 'Ok':
            return None
        else:
            return None

    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.RequestException as e:
        return None
    except json.JSONDecodeError:
        return None
    except Exception as e:
        return None


def calculate_full_route_info(address_a: str, address_b: str) -> dict | None:
    start_coords = _get_coordinates_from_address(address_a)
    if not start_coords:
        return None

    end_coords = _get_coordinates_from_address(address_b)
    if not end_coords:
        return None

    route_info = _get_travel_time_osrm(start_coords, end_coords)
    if route_info:
        duration_minutes = route_info['duration'] / 60
        distance_km = route_info['distance'] / 1000
        return {
            "duration_minutes": duration_minutes,
            "distance_km": distance_km,
        }
    else:
        return None
