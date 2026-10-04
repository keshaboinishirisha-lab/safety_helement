"""
database.py - Handles all data storage and retrieval using SQLite
Smart Safety Helmet with Accident Detection
"""

import sqlite3
import json
import os
from datetime import datetime

DB_FILE = "helmet_data.db"

def get_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def init_database():
    """Initialize the database and create all tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            phone TEXT,
            email TEXT,
            age INTEGER,
            blood_group TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # Emergency contacts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emergency_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            relation TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Accident logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accident_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp TEXT,
            latitude REAL,
            longitude REAL,
            impact_force REAL,
            gyro_reading REAL,
            alert_sent INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Reviews table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            rating INTEGER,
            comment TEXT,
            timestamp TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # SMS alerts log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sms_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            contact_name TEXT,
            contact_phone TEXT,
            message TEXT,
            timestamp TEXT DEFAULT (datetime('now')),
            status TEXT DEFAULT 'Sent',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

# ──────────────────────────── USER FUNCTIONS ────────────────────────────

def register_user(username, password, full_name, phone, email, age, blood_group):
    """Register a new user. Returns (True, msg) or (False, error)."""
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO users (username, password, full_name, phone, email, age, blood_group)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (username, password, full_name, phone, email, age, blood_group))
        conn.commit()
        return True, "Registration successful!"
    except sqlite3.IntegrityError:
        return False, "Username already exists. Please choose another."
    finally:
        conn.close()

def login_user(username, password):
    """Verify login. Returns user dict or None."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?", (username, password)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_id(user_id):
    """Fetch user details by ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_user_profile(user_id, full_name, phone, email, age, blood_group):
    """Update user profile info."""
    conn = get_connection()
    conn.execute("""
        UPDATE users SET full_name=?, phone=?, email=?, age=?, blood_group=?
        WHERE id=?
    """, (full_name, phone, email, age, blood_group, user_id))
    conn.commit()
    conn.close()

# ──────────────────────────── CONTACT FUNCTIONS ─────────────────────────

def add_emergency_contact(user_id, name, phone, relation):
    """Add an emergency contact for a user."""
    conn = get_connection()
    conn.execute("""
        INSERT INTO emergency_contacts (user_id, name, phone, relation)
        VALUES (?, ?, ?, ?)
    """, (user_id, name, phone, relation))
    conn.commit()
    conn.close()

def get_emergency_contacts(user_id):
    """Get all emergency contacts for a user."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM emergency_contacts WHERE user_id=?", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_emergency_contact(contact_id):
    """Delete an emergency contact by ID."""
    conn = get_connection()
    conn.execute("DELETE FROM emergency_contacts WHERE id=?", (contact_id,))
    conn.commit()
    conn.close()

# ──────────────────────────── ACCIDENT FUNCTIONS ─────────────────────────

def log_accident(user_id, latitude, longitude, impact_force, gyro_reading, alert_sent=0):
    """Log a detected accident event."""
    conn = get_connection()
    conn.execute("""
        INSERT INTO accident_logs (user_id, timestamp, latitude, longitude, impact_force, gyro_reading, alert_sent)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), latitude, longitude,
          impact_force, gyro_reading, alert_sent))
    conn.commit()
    conn.close()

def get_accident_logs(user_id):
    """Get accident history for a user."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM accident_logs WHERE user_id=? ORDER BY timestamp DESC", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ──────────────────────────── REVIEW FUNCTIONS ───────────────────────────

def submit_review(user_id, username, rating, comment):
    """Submit a user review/feedback."""
    conn = get_connection()
    conn.execute("""
        INSERT INTO reviews (user_id, username, rating, comment)
        VALUES (?, ?, ?, ?)
    """, (user_id, username, rating, comment))
    conn.commit()
    conn.close()

def get_all_reviews():
    """Get all reviews sorted by newest first."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM reviews ORDER BY timestamp DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ──────────────────────────── SMS LOG FUNCTIONS ──────────────────────────

def log_sms(user_id, contact_name, contact_phone, message):
    """Log a simulated SMS alert."""
    conn = get_connection()
    conn.execute("""
        INSERT INTO sms_logs (user_id, contact_name, contact_phone, message)
        VALUES (?, ?, ?, ?)
    """, (user_id, contact_name, contact_phone, message))
    conn.commit()
    conn.close()

def get_sms_logs(user_id):
    """Get all SMS logs for a user."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM sms_logs WHERE user_id=? ORDER BY timestamp DESC", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
