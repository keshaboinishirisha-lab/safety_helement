"""
location.py — GPS Location Simulation & Utilities
Smart Helmet Safety System

Simulates GPS sensor data centered around Hyderabad, India.
Optionally integrates with geocoder for real device location.
"""

import random
import math
from datetime import datetime

# ──────────────────────────── DEFAULT BASE LOCATION ──────────────────────
# Hyderabad city center (Charminar area)

BASE_LAT = 17.3616
BASE_LON = 78.4747

# Notable Hyderabad landmarks for named location simulation
HYDERABAD_LANDMARKS = [
    {"name": "Charminar",          "lat": 17.3616, "lon": 78.4747},
    {"name": "Hitech City",        "lat": 17.4504, "lon": 78.3803},
    {"name": "Golconda Fort",      "lat": 17.3833, "lon": 78.4011},
    {"name": "Hussain Sagar Lake", "lat": 17.4239, "lon": 78.4738},
    {"name": "Banjara Hills",      "lat": 17.4138, "lon": 78.4400},
    {"name": "Jubilee Hills",      "lat": 17.4326, "lon": 78.4071},
    {"name": "Secunderabad",       "lat": 17.4399, "lon": 78.4983},
    {"name": "Begumpet",           "lat": 17.4429, "lon": 78.4696},
]


# ──────────────────────────── CORE GPS SIMULATION ────────────────────────

def simulate_gps_location(
    prev_lat: float = None,
    prev_lon: float = None,
    drift:    float = 0.001,
) -> dict:
    """
    Simulate a GPS location reading, drifting slightly from previous position.

    Args:
        prev_lat: Previous latitude  (None → use base location with jitter).
        prev_lon: Previous longitude (None → use base location with jitter).
        drift:    Max random movement per update in decimal degrees (~100 m).

    Returns:
        Dict with latitude, longitude, accuracy, speed_kmh, heading, timestamp.
    """
    if prev_lat is None or prev_lon is None:
        lat = BASE_LAT + random.uniform(-0.02, 0.02)
        lon = BASE_LON + random.uniform(-0.02, 0.02)
    else:
        lat = prev_lat + random.uniform(-drift, drift)
        lon = prev_lon + random.uniform(-drift, drift)

    return {
        "latitude":  round(lat, 6),
        "longitude": round(lon, 6),
        "accuracy":  round(random.uniform(3.0, 15.0), 1),    # metres
        "speed_kmh": round(random.uniform(0.0, 60.0), 1),
        "heading":   round(random.uniform(0.0, 359.9), 1),   # degrees
        "altitude":  round(random.uniform(500.0, 560.0), 1), # Hyderabad ~500 m ASL
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


# ──────────────────────────── ROUTE GENERATOR ────────────────────────────

def generate_route_history(n: int = 20) -> list[dict]:
    """
    Generate a list of GPS points simulating a continuous route.

    Args:
        n: Number of points to generate.

    Returns:
        List of dicts with 'lat' and 'lon' keys.
    """
    route = []
    lat, lon = BASE_LAT + random.uniform(-0.01, 0.01), BASE_LON + random.uniform(-0.01, 0.01)
    heading  = random.uniform(0, 360)     # initial heading

    for _ in range(n):
        # Gradually turn (random walk in heading)
        heading += random.uniform(-15, 15)
        heading %= 360

        speed = random.uniform(0.0003, 0.0008)  # ~30-80 m per step
        lat  += speed * math.cos(math.radians(heading))
        lon  += speed * math.sin(math.radians(heading))
        route.append({"lat": round(lat, 6), "lon": round(lon, 6)})

    return route


# ──────────────────────────── GOOGLE MAPS LINK ───────────────────────────

def google_maps_url(latitude: float, longitude: float) -> str:
    """Return a Google Maps URL for the given coordinates."""
    return f"https://maps.google.com/?q={latitude},{longitude}"


def google_maps_embed_url(latitude: float, longitude: float, zoom: int = 15) -> str:
    """Return a Google Maps embed URL for use in iframes."""
    return (
        f"https://www.google.com/maps?q={latitude},{longitude}"
        f"&z={zoom}&output=embed"
    )


# ──────────────────────────── NEAREST LANDMARK ───────────────────────────

def nearest_landmark(latitude: float, longitude: float) -> dict:
    """
    Find the nearest named landmark to the given coordinates.

    Returns:
        Dict with name, lat, lon, and distance_m.
    """
    def haversine(lat1, lon1, lat2, lon2):
        R = 6_371_000  # Earth radius in metres
        φ1, φ2 = math.radians(lat1), math.radians(lat2)
        dφ     = math.radians(lat2 - lat1)
        dλ     = math.radians(lon2 - lon1)
        a = math.sin(dφ/2)**2 + math.cos(φ1)*math.cos(φ2)*math.sin(dλ/2)**2
        return R * 2 * math.asin(math.sqrt(a))

    best = min(
        HYDERABAD_LANDMARKS,
        key=lambda lm: haversine(latitude, longitude, lm["lat"], lm["lon"])
    )
    return {
        **best,
        "distance_m": round(haversine(latitude, longitude, best["lat"], best["lon"])),
    }


# ──────────────────────────── REAL DEVICE LOCATION (optional) ────────────

def get_real_device_location() -> dict | None:
    """
    Attempt to fetch the real device location using the 'geocoder' package.
    Returns None if geocoder is not installed or location is unavailable.

    Install: pip install geocoder
    """
    try:
        import geocoder
        g = geocoder.ip("me")
        if g.ok:
            return {
                "latitude":  round(g.latlng[0], 6),
                "longitude": round(g.latlng[1], 6),
                "accuracy":  1000.0,        # IP-based — low accuracy
                "speed_kmh": 0.0,
                "heading":   0.0,
                "altitude":  0.0,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source":    "ip-geolocation",
                "city":      g.city or "Unknown",
                "country":   g.country or "Unknown",
            }
    except ImportError:
        pass
    except Exception:
        pass
    return None


# ──────────────────────────── QUICK TEST ────────────────────────────────

if __name__ == "__main__":
    loc = simulate_gps_location()
    print(f"Simulated: {loc}")
    print(f"Maps URL:  {google_maps_url(loc['latitude'], loc['longitude'])}")
    lm = nearest_landmark(loc["latitude"], loc["longitude"])
    print(f"Nearest:   {lm['name']} ({lm['distance_m']} m away)")

    real = get_real_device_location()
    if real:
        print(f"Real IP:   {real['latitude']}, {real['longitude']} ({real.get('city')})")
    else:
        print("Real location unavailable (geocoder not installed or IP lookup failed).")
