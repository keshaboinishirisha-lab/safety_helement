"""
sms.py — SMS Alert Logic using Twilio
Smart Helmet Safety System

To enable REAL SMS:
  1. Sign up at https://www.twilio.com
  2. Get your Account SID, Auth Token, and a Twilio phone number
  3. Fill in the credentials below
  4. Install:  pip install twilio

Without credentials, all alerts are SIMULATED (logged to DB only).
"""

import random
import time
from datetime import datetime

import database as db

# ──────────────────────────── TWILIO CREDENTIALS ─────────────────────────
# Replace these with your actual Twilio credentials to send real SMS.
# Leave blank ("") to run in simulation mode.

TWILIO_ACCOUNT_SID  = ""          # e.g. "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN   = ""          # e.g. "your_auth_token_here"
TWILIO_FROM_NUMBER  = ""          # e.g. "+12345678900" (your Twilio number)

# ──────────────────────────── MESSAGE BUILDER ────────────────────────────

def build_alert_message(user_name: str, location: dict, accident_type: str) -> str:
    """
    Build the SMS alert message string.

    Args:
        user_name:     Full name of the rider.
        location:      Dict with 'latitude' and 'longitude' keys.
        accident_type: String describing the accident type.

    Returns:
        Formatted SMS string.
    """
    maps_url = f"https://maps.google.com/?q={location['latitude']},{location['longitude']}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return (
        f"🚨 ACCIDENT ALERT 🚨\n"
        f"Rider: {user_name}\n"
        f"Type: {accident_type}\n"
        f"Time: {timestamp}\n"
        f"\n"
        f"The rider may be in danger.\n"
        f"Live Location:\n"
        f"{maps_url}\n"
        f"\n"
        f"Please check on them immediately!\n"
        f"If no response, call 112."
    )


# ──────────────────────────── TWILIO SENDER ──────────────────────────────

def _send_via_twilio(to_number: str, message: str) -> tuple[bool, str]:
    """
    Attempt to send a real SMS via Twilio.

    Returns:
        (success: bool, status_message: str)
    """
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER]):
        return False, "Twilio not configured — using simulation mode"

    try:
        from twilio.rest import Client
        client  = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message_obj = client.messages.create(
            body=message,
            from_=TWILIO_FROM_NUMBER,
            to=to_number,
        )
        return True, f"Sent (SID: {message_obj.sid})"
    except ImportError:
        return False, "twilio package not installed — pip install twilio"
    except Exception as e:
        return False, f"Twilio error: {str(e)}"


# ──────────────────────────── SIMULATION FALLBACK ────────────────────────

def _simulate_send(contact_name: str) -> tuple[bool, str]:
    """
    Simulate SMS delivery with a realistic delay and 95% success rate.
    """
    time.sleep(0.15)                     # Simulate network latency
    success = random.random() < 0.95     # 95% success
    if success:
        return True,  "Sent ✅ (simulated)"
    else:
        return False, "Failed ❌ (simulated network error)"


# ──────────────────────────── MAIN ALERT DISPATCHER ─────────────────────

def send_sms_alert(
    user_id:      int,
    user_name:    str,
    contacts:     list[dict],
    location:     dict,
    accident_type: str,
) -> list[dict]:
    """
    Send SMS alerts to all supplied emergency contacts.
    Uses Twilio if configured, otherwise simulates delivery.
    Logs every attempt to the database.

    Args:
        user_id:       ID of the logged-in user.
        user_name:     Rider's display name.
        contacts:      List of dicts with keys: name, phone.
        location:      Dict with latitude, longitude.
        accident_type: Description of the event.

    Returns:
        List of result dicts: { name, phone, status, message, real_sms }
    """
    message = build_alert_message(user_name, location, accident_type)
    results = []
    twilio_active = bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_FROM_NUMBER)

    for contact in contacts:
        if twilio_active:
            success, status_text = _send_via_twilio(contact["phone"], message)
        else:
            success, status_text = _simulate_send(contact["name"])

        # Always log to DB
        db.log_sms(
            user_id       = user_id,
            contact_name  = contact["name"],
            contact_phone = contact["phone"],
            message       = message,
        )

        results.append({
            "name":     contact["name"],
            "phone":    contact["phone"],
            "status":   status_text,
            "message":  message,
            "real_sms": twilio_active and success,
        })

    return results


# ──────────────────────────── QUICK TEST ────────────────────────────────

if __name__ == "__main__":
    test_contacts = [{"name": "Test Contact", "phone": "+91XXXXXXXXXX"}]
    test_location = {"latitude": 17.3850, "longitude": 78.4867}
    results = send_sms_alert(1, "Test Rider", test_contacts, test_location, "Test Alert")
    for r in results:
        print(f"{r['name']} ({r['phone']}): {r['status']}")
        print(f"Message:\n{r['message']}")
