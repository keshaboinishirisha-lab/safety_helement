"""
utils.py - Helper functions for accident detection, simulation, and alerts
Smart Safety Helmet with Accident Detection
"""

import random
import math
import time
from datetime import datetime, timedelta
import database as db

# ──────────────────────────── THRESHOLDS ─────────────────────────────────

IMPACT_THRESHOLD = 2.5      # g-force — above this means possible accident
GYRO_THRESHOLD   = 250.0    # °/s  — rapid rotation may indicate a fall
FALL_ACCEL_LOW   = 0.3      # g-force below this may mean free-fall

# ──────────────────────────── SENSOR SIMULATION ──────────────────────────

def simulate_normal_sensor_data():
    """
    Simulate normal riding/walking sensor readings.
    Returns a dict with accelerometer (g) and gyroscope (°/s) values.
    """
    return {
        "accel_x": round(random.uniform(-0.3, 0.3), 3),
        "accel_y": round(random.uniform(-0.3, 0.3), 3),
        "accel_z": round(random.uniform(0.9, 1.1), 3),   # gravity ~1g
        "gyro_x":  round(random.uniform(-15, 15), 2),
        "gyro_y":  round(random.uniform(-15, 15), 2),
        "gyro_z":  round(random.uniform(-15, 15), 2),
        "timestamp": datetime.now().strftime("%H:%M:%S"),
    }

def simulate_accident_sensor_data(accident_type="impact"):
    """
    Simulate sensor readings during an accident event.
    accident_type: 'impact' | 'fall'
    """
    if accident_type == "fall":
        return {
            "accel_x": round(random.uniform(-0.1, 0.1), 3),
            "accel_y": round(random.uniform(-0.1, 0.1), 3),
            "accel_z": round(random.uniform(0.05, 0.2), 3),   # near-zero = free-fall
            "gyro_x":  round(random.uniform(200, 350), 2),
            "gyro_y":  round(random.uniform(200, 350), 2),
            "gyro_z":  round(random.uniform(200, 350), 2),
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        }
    else:  # impact
        return {
            "accel_x": round(random.uniform(2.5, 5.0), 3),
            "accel_y": round(random.uniform(2.5, 5.0), 3),
            "accel_z": round(random.uniform(3.0, 6.0), 3),
            "gyro_x":  round(random.uniform(100, 300), 2),
            "gyro_y":  round(random.uniform(100, 300), 2),
            "gyro_z":  round(random.uniform(100, 300), 2),
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        }

# ──────────────────────────── DETECTION LOGIC ────────────────────────────

def compute_total_acceleration(ax, ay, az):
    """Compute the magnitude of the acceleration vector (in g)."""
    return math.sqrt(ax**2 + ay**2 + az**2)

def compute_total_gyro(gx, gy, gz):
    """Compute the magnitude of the gyroscope reading (in °/s)."""
    return math.sqrt(gx**2 + gy**2 + gz**2)

def detect_accident(sensor_data):
    """
    Core accident detection function.
    Returns a dict: { detected: bool, type: str, confidence: int, reason: str }
    """
    ax = sensor_data["accel_x"]
    ay = sensor_data["accel_y"]
    az = sensor_data["accel_z"]
    gx = sensor_data["gyro_x"]
    gy = sensor_data["gyro_y"]
    gz = sensor_data["gyro_z"]

    total_accel = compute_total_acceleration(ax, ay, az)
    total_gyro  = compute_total_gyro(gx, gy, gz)

    # Free-fall detection (sudden drop in acceleration)
    if total_accel < FALL_ACCEL_LOW and total_gyro > GYRO_THRESHOLD:
        return {
            "detected":   True,
            "type":       "Fall Detected",
            "confidence": 92,
            "reason":     f"Near-zero acceleration ({total_accel:.2f}g) + high rotation ({total_gyro:.1f}°/s)",
            "total_accel": round(total_accel, 3),
            "total_gyro":  round(total_gyro, 2),
        }

    # High-impact detection
    if total_accel > IMPACT_THRESHOLD:
        confidence = min(99, int(60 + (total_accel - IMPACT_THRESHOLD) * 15))
        return {
            "detected":   True,
            "type":       "High Impact Detected",
            "confidence": confidence,
            "reason":     f"Impact force {total_accel:.2f}g exceeds threshold {IMPACT_THRESHOLD}g",
            "total_accel": round(total_accel, 3),
            "total_gyro":  round(total_gyro, 2),
        }

    # Rapid rotation alone
    if total_gyro > GYRO_THRESHOLD:
        return {
            "detected":   True,
            "type":       "Rapid Rotation / Skid",
            "confidence": 75,
            "reason":     f"Gyroscope reading {total_gyro:.1f}°/s exceeds threshold {GYRO_THRESHOLD}°/s",
            "total_accel": round(total_accel, 3),
            "total_gyro":  round(total_gyro, 2),
        }

    return {
        "detected":   False,
        "type":       "Normal",
        "confidence": 0,
        "reason":     "All readings within safe range.",
        "total_accel": round(total_accel, 3),
        "total_gyro":  round(total_gyro, 2),
    }

# ──────────────────────────── GPS SIMULATION ─────────────────────────────

# Hyderabad city center as default starting location
BASE_LAT = 17.3850
BASE_LON = 78.4867

def simulate_gps_location(prev_lat=None, prev_lon=None):
    """
    Simulate a GPS location. Drifts slightly from previous position
    to mimic real movement.
    """
    if prev_lat is None or prev_lon is None:
        lat = BASE_LAT + random.uniform(-0.01, 0.01)
        lon = BASE_LON + random.uniform(-0.01, 0.01)
    else:
        lat = prev_lat + random.uniform(-0.001, 0.001)
        lon = prev_lon + random.uniform(-0.001, 0.001)

    return {
        "latitude":  round(lat, 6),
        "longitude": round(lon, 6),
        "accuracy":  round(random.uniform(3, 15), 1),  # metres
        "speed_kmh": round(random.uniform(0, 60), 1),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

def generate_route_history(n=10):
    """Generate a list of n GPS points simulating a route."""
    route = []
    lat, lon = BASE_LAT, BASE_LON
    for _ in range(n):
        lat += random.uniform(-0.002, 0.002)
        lon += random.uniform(-0.002, 0.002)
        route.append({"lat": round(lat, 6), "lon": round(lon, 6)})
    return route

# ──────────────────────────── ALERT SYSTEM ───────────────────────────────

def build_alert_message(user_name, location, accident_type):
    """Create the SMS alert message text."""
    maps_url = f"https://maps.google.com/?q={location['latitude']},{location['longitude']}"
    return (
        f"🚨 ACCIDENT ALERT 🚨\n"
        f"User: {user_name} may have been in an accident!\n"
        f"Type: {accident_type}\n"
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Location: {location['latitude']}, {location['longitude']}\n"
        f"Google Maps: {maps_url}\n"
        f"Please check on them immediately!"
    )

def simulate_send_sms(user_id, user_name, contacts, location, accident_type):
    """
    Simulate sending SMS to all emergency contacts.
    Logs each alert to the database.
    Returns list of results.
    """
    results = []
    message = build_alert_message(user_name, location, accident_type)

    for contact in contacts:
        # Simulate network delay
        time.sleep(0.1)
        # 95% success rate simulation
        success = random.random() < 0.95
        status = "Sent ✅" if success else "Failed ❌"

        db.log_sms(
            user_id       = user_id,
            contact_name  = contact["name"],
            contact_phone = contact["phone"],
            message       = message,
        )
        results.append({
            "name":    contact["name"],
            "phone":   contact["phone"],
            "status":  status,
            "message": message,
        })

    return results

# ──────────────────────────── STATS / CHARTS ─────────────────────────────

def generate_sensor_history(n=50, inject_accident_at=None):
    """
    Generate n historical sensor readings for chart display.
    Optionally inject an accident at a specific index.
    """
    history = []
    for i in range(n):
        if inject_accident_at and i == inject_accident_at:
            data = simulate_accident_sensor_data("impact")
        else:
            data = simulate_normal_sensor_data()
        history.append({
            "index":       i,
            "total_accel": compute_total_acceleration(data["accel_x"], data["accel_y"], data["accel_z"]),
            "total_gyro":  compute_total_gyro(data["gyro_x"], data["gyro_y"], data["gyro_z"]),
        })
    return history

def get_dashboard_stats(user_id):
    """Aggregate stats for the dashboard."""
    logs     = db.get_accident_logs(user_id)
    contacts = db.get_emergency_contacts(user_id)
    sms_logs = db.get_sms_logs(user_id)

    return {
        "total_accidents":  len(logs),
        "total_contacts":   len(contacts),
        "total_alerts_sent": len(sms_logs),
        "last_accident":    logs[0]["timestamp"] if logs else "None",
    }

# ──────────────────────────── UTILITIES ──────────────────────────────────

def format_stars(rating):
    """Convert integer rating to star emoji string."""
    return "⭐" * int(rating) + "☆" * (5 - int(rating))

def time_ago(timestamp_str):
    """Return human-readable time difference like '2 hours ago'."""
    try:
        ts  = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        diff = datetime.now() - ts
        secs = int(diff.total_seconds())
        if secs < 60:
            return f"{secs} seconds ago"
        elif secs < 3600:
            return f"{secs // 60} minutes ago"
        elif secs < 86400:
            return f"{secs // 3600} hours ago"
        else:
            return f"{secs // 86400} days ago"
    except Exception:
        return timestamp_str
