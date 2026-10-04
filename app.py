"""
app.py — Smart Helmet Safety System (Main Streamlit App)
Run with:  streamlit run app.py
"""

import streamlit as st
import time
import random
from datetime import datetime

import database as db
import utils
from location import simulate_gps_location, generate_route_history
from buzzer import trigger_buzzer_html
from sms import send_sms_alert, build_alert_message

# ──────────────────────────── PAGE CONFIG ────────────────────────────────

st.set_page_config(
    page_title="Smart Helmet Safety System",
    page_icon="🪖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────── GLOBAL STYLES ──────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Exo+2:wght@300;400;500;600&display=swap');

:root {
    --red:    #FF2D2D;
    --red2:   #C0392B;
    --green:  #00E676;
    --green2: #1B5E20;
    --amber:  #FFB300;
    --bg:     #080C14;
    --bg2:    #0D1117;
    --card:   rgba(255,255,255,0.04);
    --border: rgba(255,255,255,0.08);
    --text:   #E8EDF5;
    --muted:  #6B7A94;
}

.stApp {
    background: var(--bg);
    background-image:
        radial-gradient(ellipse at 20% 50%, rgba(255,45,45,0.06) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, rgba(0,230,118,0.04) 0%, transparent 50%);
}

html, body, [class*="css"] {
    font-family: 'Exo 2', sans-serif;
    color: var(--text);
}

h1, h2, h3, h4 {
    font-family: 'Orbitron', monospace;
    letter-spacing: 1px;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid rgba(255,45,45,0.2) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── Cards ── */
.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.4rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(8px);
}

/* ── Status Badges ── */
.status-safe {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(0,230,118,0.12);
    border: 1px solid rgba(0,230,118,0.4);
    border-radius: 24px;
    padding: 6px 18px;
    font-family: 'Orbitron', monospace;
    font-size: 0.85rem;
    color: var(--green);
}
.status-danger {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(255,45,45,0.15);
    border: 1px solid rgba(255,45,45,0.5);
    border-radius: 24px;
    padding: 6px 18px;
    font-family: 'Orbitron', monospace;
    font-size: 0.85rem;
    color: var(--red);
    animation: blink 1s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.5} }

/* ── Alert boxes ── */
.alert-danger {
    background: linear-gradient(90deg, rgba(255,45,45,0.25), rgba(192,57,43,0.15));
    border-left: 4px solid var(--red);
    border-radius: 8px;
    padding: 1rem 1.5rem;
    font-size: 1rem;
    animation: pulse 1.5s infinite;
}
.alert-success {
    background: rgba(0,230,118,0.1);
    border-left: 4px solid var(--green);
    border-radius: 8px;
    padding: 1rem 1.5rem;
}
.alert-info {
    background: rgba(33,150,243,0.1);
    border-left: 4px solid #2196F3;
    border-radius: 8px;
    padding: 1rem 1.5rem;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.65} }

/* ── Metric card ── */
.metric-card {
    background: linear-gradient(135deg, rgba(255,45,45,0.12), rgba(13,17,23,0.8));
    border: 1px solid rgba(255,45,45,0.25);
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
}
.metric-card .val { font-family:'Orbitron',monospace; font-size:2.2rem; color:var(--red); }
.metric-card .lbl { color:var(--muted); font-size:0.8rem; margin-top:2px; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #FF2D2D, #C0392B) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    padding: 0.55rem 1.5rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 24px rgba(255,45,45,0.5) !important;
}

/* Green button override */
.btn-green .stButton > button {
    background: linear-gradient(135deg, #00C853, #1B5E20) !important;
    box-shadow: 0 0 12px rgba(0,200,83,0.3) !important;
}

/* ── Inputs ── */
.stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox select {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: white !important;
    border-radius: 8px !important;
}

/* ── Review card ── */
.review-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.7rem;
}

/* ── Progress ── */
.stProgress > div > div > div { background: var(--red) !important; }

/* ── Hide branding ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── GPS coord box ── */
.gps-box {
    background: rgba(0,0,0,0.4);
    border: 1px solid rgba(0,230,118,0.3);
    border-radius: 10px;
    padding: 1rem 1.4rem;
    font-family: 'Orbitron', monospace;
    font-size: 0.85rem;
    color: var(--green);
    letter-spacing: 1px;
}

/* ── Twilio config notice ── */
.twilio-notice {
    background: rgba(255,179,0,0.1);
    border: 1px solid rgba(255,179,0,0.3);
    border-radius: 8px;
    padding: 0.8rem 1.2rem;
    font-size: 0.82rem;
    color: var(--amber);
}

/* ── Tab ── */
.stTabs [data-baseweb="tab-list"] { background: rgba(255,255,255,0.04); border-radius: 10px; }
.stTabs [data-baseweb="tab"]      { color: var(--muted) !important; font-family:'Exo 2',sans-serif; }
.stTabs [aria-selected="true"]    { color: var(--red) !important; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────── INIT ────────────────────────────────────────

db.init_database()

for key, val in {
    "logged_in":       False,
    "user":            None,
    "page":            "🏠 Home",
    "last_location":   None,
    "accident_active": False,
    "last_alert_time": None,
    "buzzer_active":   False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ──────────────────────────── SIDEBAR ────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center; padding:1.2rem 0 0.5rem;'>
            <div style='font-size:2.8rem;'>🪖</div>
            <div style='font-family:Orbitron; font-size:1.1rem; font-weight:700; color:#FF2D2D; line-height:1.3;'>
                Smart Helmet<br>Safety System
            </div>
        </div>
        <hr style='border-color:rgba(255,45,45,0.2); margin:0.8rem 0;'/>
        """, unsafe_allow_html=True)

        # Live status pill
        if st.session_state.accident_active:
            st.markdown("<div class='status-danger'>⚠ ACCIDENT DETECTED</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='status-safe'>● SYSTEM SAFE</div>", unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)

        pages = ["🏠 Home", "🔐 Login / Register", "📊 Dashboard",
                 "💥 Accident Detection", "👥 Emergency Contacts",
                 "📍 Live Location", "📱 SMS Alerts", "⭐ Reviews",
                 "📜 Terms & Conditions"]

        for p in pages:
            active = st.session_state.page == p
            style  = "color:#FF2D2D; font-weight:700;" if active else "color:#94A3B8;"
            if st.sidebar.button(p, use_container_width=True, key=f"nav_{p}"):
                st.session_state.page = p
                st.rerun()

        st.markdown("<hr style='border-color:rgba(255,255,255,0.08);'/>", unsafe_allow_html=True)

        if st.session_state.logged_in:
            user = st.session_state.user
            st.markdown(f"""
            <div style='text-align:center; font-size:0.82rem; color:#6B7A94;'>
                Logged in as<br>
                <span style='color:#FF2D2D; font-family:Orbitron; font-size:0.9rem;'>{user['username']}</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user      = None
                st.session_state.page      = "🏠 Home"
                st.rerun()
        else:
            st.markdown("<div style='text-align:center; color:#6B7A94; font-size:0.82rem;'>Not logged in</div>", unsafe_allow_html=True)

# ──────────────────────────── PAGES ──────────────────────────────────────

def page_home():
    st.markdown("""
    <div style='text-align:center; padding:2rem 0 1rem;'>
        <div style='font-size:5rem; margin-bottom:0.5rem;'>🪖</div>
        <h1 style='font-size:2.2rem; color:#FF2D2D; margin:0;'>SMART HELMET SAFETY SYSTEM</h1>
        <p style='color:#6B7A94; font-size:1rem; margin-top:0.5rem;'>
            Real-time accident detection · Emergency alerts · GPS tracking
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    features = [
        ("💥", "Accident Detection", "Detects high-impact crashes, free-falls, and rapid rotation using simulated accelerometer and gyroscope data."),
        ("📱", "SMS Alerts", "Instantly alerts all emergency contacts with your GPS location via Twilio SMS when an accident is detected."),
        ("📍", "GPS Tracking", "Simulates real-time GPS coordinates and generates live Google Maps links for precise location sharing."),
        ("🔊", "Buzzer Alarm", "Triggers an audible alarm sequence when an accident is detected to alert nearby bystanders."),
        ("👥", "Emergency Contacts", "Store and manage multiple emergency contacts in a local SQLite database with name, phone, and relation."),
        ("📊", "Dashboard", "Live stats showing accident history, alert logs, sensor readings, and system health overview."),
    ]
    for i, (icon, title, desc) in enumerate(features):
        col = [col1, col2, col3][i % 3]
        with col:
            st.markdown(f"""
            <div class='card' style='height:160px;'>
                <div style='font-size:2rem;'>{icon}</div>
                <div style='font-family:Orbitron; font-size:0.95rem; color:#FF2D2D; margin:0.4rem 0 0.3rem;'>{title}</div>
                <div style='color:#6B7A94; font-size:0.82rem; line-height:1.5;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div class='card' style='margin-top:1rem;'>
        <h3 style='color:#FF2D2D; margin:0 0 0.8rem;'>⚠️ DISCLAIMER</h3>
        <p style='color:#6B7A94; font-size:0.88rem; margin:0; line-height:1.7;'>
            This is a <b style='color:#FFB300;'>software simulation</b> for educational/demonstration purposes only.
            It does not connect to real physical sensors. SMS alerts are simulated by default but can be
            configured with real Twilio credentials. Always call <b style='color:#FF2D2D;'>112</b> in an actual emergency.
        </p>
    </div>
    """, unsafe_allow_html=True)


def page_login():
    st.markdown("<h1 style='color:#FF2D2D; font-family:Orbitron;'>🔐 LOGIN / REGISTER</h1>", unsafe_allow_html=True)
    tab_login, tab_register, tab_profile = st.tabs(["Login", "Register", "Profile"])

    with tab_login:
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter username")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                submit   = st.form_submit_button("🔓 LOGIN", use_container_width=True)
                if submit:
                    user = db.login_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user      = user
                        st.success(f"✅ Welcome back, {user['full_name'] or username}!")
                        time.sleep(0.5)
                        st.session_state.page = "📊 Dashboard"
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials.")

    with tab_register:
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            with st.form("register_form"):
                r_user   = st.text_input("Username *",    placeholder="Choose a username")
                r_pass   = st.text_input("Password *",    type="password", placeholder="Choose a password")
                r_name   = st.text_input("Full Name",     placeholder="Your full name")
                r_phone  = st.text_input("Phone Number",  placeholder="+91 XXXXXXXXXX")
                r_email  = st.text_input("Email",         placeholder="you@example.com")
                r_age    = st.number_input("Age", 10, 100, 25)
                r_blood  = st.selectbox("Blood Group", ["A+","A-","B+","B-","AB+","AB-","O+","O-","Unknown"])
                r_submit = st.form_submit_button("📝 REGISTER", use_container_width=True)
                if r_submit:
                    if not r_user or not r_pass:
                        st.error("Username and password are required.")
                    else:
                        ok, msg = db.register_user(r_user, r_pass, r_name, r_phone, r_email, r_age, r_blood)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)

    with tab_profile:
        if not st.session_state.logged_in:
            st.warning("🔒 Please log in first.")
            return
        user = st.session_state.user
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            with st.form("profile_form"):
                p_name  = st.text_input("Full Name",   value=user.get("full_name","") or "")
                p_phone = st.text_input("Phone",       value=user.get("phone","")     or "")
                p_email = st.text_input("Email",       value=user.get("email","")     or "")
                p_age   = st.number_input("Age", 10, 100, int(user.get("age",25) or 25))
                p_blood = st.selectbox("Blood Group",
                    ["A+","A-","B+","B-","AB+","AB-","O+","O-","Unknown"],
                    index=["A+","A-","B+","B-","AB+","AB-","O+","O-","Unknown"].index(user.get("blood_group","Unknown") or "Unknown"))
                p_submit = st.form_submit_button("💾 SAVE CHANGES", use_container_width=True)
                if p_submit:
                    db.update_user_profile(user["id"], p_name, p_phone, p_email, p_age, p_blood)
                    st.session_state.user = db.get_user_by_id(user["id"])
                    st.success("✅ Profile updated!")
                    st.rerun()


def page_dashboard():
    if not st.session_state.logged_in:
        st.warning("🔒 Please log in to view the dashboard."); return

    user  = st.session_state.user
    stats = utils.get_dashboard_stats(user["id"])

    st.markdown("<h1 style='color:#FF2D2D; font-family:Orbitron;'>📊 HELMET DASHBOARD</h1>", unsafe_allow_html=True)

    # Status bar
    if st.session_state.accident_active:
        st.markdown("<div class='alert-danger'>🚨 EMERGENCY ACTIVE — Accident was detected! Check rider status immediately.</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='alert-success'>✅ System Normal — All sensors within safe range.</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    metrics = [
        (stats["total_accidents"],  "Total Accidents"),
        (stats["total_contacts"],   "Emergency Contacts"),
        (stats["total_alerts_sent"],"Alerts Sent"),
        (stats["last_accident"],    "Last Accident"),
    ]
    for col, (val, lbl) in zip([c1,c2,c3,c4], metrics):
        with col:
            st.markdown(f"<div class='metric-card'><div class='val'>{val}</div><div class='lbl'>{lbl}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_chart, col_log = st.columns([3,2])

    with col_chart:
        st.markdown("<h3 style='color:#FF2D2D; font-size:1rem;'>SENSOR HISTORY</h3>", unsafe_allow_html=True)
        history = utils.generate_sensor_history(50, inject_accident_at=random.randint(20,40))
        import pandas as pd
        df = pd.DataFrame(history)
        df = df.rename(columns={"index":"Reading","total_accel":"Acceleration (g)","total_gyro":"Gyroscope (°/s)"})
        st.line_chart(df.set_index("Reading")[["Acceleration (g)","Gyroscope (°/s)"]], height=250)

    with col_log:
        st.markdown("<h3 style='color:#FF2D2D; font-size:1rem;'>ACCIDENT LOG</h3>", unsafe_allow_html=True)
        logs = db.get_accident_logs(user["id"])
        if not logs:
            st.markdown("<div class='alert-info' style='font-size:0.85rem;'>No accidents recorded yet.</div>", unsafe_allow_html=True)
        else:
            for log in logs[:5]:
                st.markdown(f"""
                <div class='card' style='padding:0.8rem;'>
                    <div style='font-size:0.8rem; color:#FF2D2D; font-family:Orbitron;'>⚡ {log['timestamp']}</div>
                    <div style='font-size:0.78rem; color:#6B7A94; margin-top:4px;'>
                        Impact: <b style='color:#E8EDF5;'>{log['impact_force']:.2f}g</b> &nbsp;|&nbsp;
                        Gyro: <b style='color:#E8EDF5;'>{log['gyro_reading']:.1f}°/s</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)


def page_accident_detection():
    if not st.session_state.logged_in:
        st.warning("🔒 Please log in."); return

    user = st.session_state.user
    st.markdown("<h1 style='color:#FF2D2D; font-family:Orbitron;'>💥 ACCIDENT DETECTION</h1>", unsafe_allow_html=True)

    col_ctrl, col_status = st.columns([1,2])

    with col_ctrl:
        st.markdown("<h3 style='color:#FF2D2D; font-size:0.95rem;'>SIMULATION CONTROLS</h3>", unsafe_allow_html=True)

        sim_type = st.selectbox("Simulation Type", ["Normal Ride", "High Impact Crash", "Free Fall"])
        st.markdown("<br>", unsafe_allow_html=True)

        btn_simulate = st.button("💥 SIMULATE ACCIDENT", use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
        btn_normal   = st.button("✅ SIMULATE NORMAL", use_container_width=True)

        if st.session_state.accident_active:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔕 CLEAR ALERT", use_container_width=True):
                st.session_state.accident_active = False
                st.rerun()

        st.markdown("""
        <div class='card' style='margin-top:1rem; padding:1rem;'>
            <div style='font-size:0.78rem; color:#6B7A94; line-height:1.8;'>
                <b style='color:#FFB300;'>Thresholds:</b><br>
                🔴 Impact  ≥ 2.5 g<br>
                🔴 Gyro    ≥ 250 °/s<br>
                🔴 Fall    ≤ 0.3 g
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_status:
        # Run simulation
        if btn_simulate or btn_normal:
            if btn_simulate:
                kind = "fall" if sim_type == "Free Fall" else "impact"
                sensor = utils.simulate_accident_sensor_data(kind)
            else:
                sensor = utils.simulate_normal_sensor_data()

            result = utils.detect_accident(sensor)
            loc    = simulate_gps_location()
            st.session_state.last_location = loc

            # Show sensor readings
            st.markdown("<h3 style='color:#FF2D2D; font-size:0.95rem;'>SENSOR READINGS</h3>", unsafe_allow_html=True)
            s1,s2,s3 = st.columns(3)
            with s1:
                st.metric("Accel X", f"{sensor['accel_x']} g")
                st.metric("Gyro X",  f"{sensor['gyro_x']} °/s")
            with s2:
                st.metric("Accel Y", f"{sensor['accel_y']} g")
                st.metric("Gyro Y",  f"{sensor['gyro_y']} °/s")
            with s3:
                st.metric("Accel Z", f"{sensor['accel_z']} g")
                st.metric("Gyro Z",  f"{sensor['gyro_z']} °/s")

            st.markdown("<br>", unsafe_allow_html=True)

            if result["detected"]:
                st.session_state.accident_active = True
                st.session_state.last_alert_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                st.markdown(f"""
                <div class='alert-danger'>
                    🚨 <b>{result['type']}</b> — Confidence: {result['confidence']}%<br>
                    <span style='font-size:0.88rem;'>{result['reason']}</span>
                </div>
                """, unsafe_allow_html=True)

                # Buzzer HTML
                st.markdown(trigger_buzzer_html(), unsafe_allow_html=True)

                # GPS
                maps_url = f"https://maps.google.com/?q={loc['latitude']},{loc['longitude']}"
                st.markdown(f"""
                <div class='gps-box' style='margin:0.8rem 0;'>
                    📍 LAT: {loc['latitude']}  |  LON: {loc['longitude']}<br>
                    <a href='{maps_url}' target='_blank' style='color:#00E676; font-size:0.78rem;'>
                        🗺 Open in Google Maps
                    </a>
                </div>
                """, unsafe_allow_html=True)

                # Log accident
                db.log_accident(user["id"], loc["latitude"], loc["longitude"],
                                result["total_accel"], result["total_gyro"], 1)

                # Send SMS alerts
                contacts = db.get_emergency_contacts(user["id"])
                if contacts:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("<h3 style='color:#FF2D2D; font-size:0.9rem;'>📱 SMS ALERTS DISPATCHED</h3>", unsafe_allow_html=True)
                    sms_results = send_sms_alert(user["id"], user.get("full_name") or user["username"],
                                                 contacts, loc, result["type"])
                    for r in sms_results:
                        st.markdown(f"<div class='alert-success' style='padding:0.5rem 1rem; margin-bottom:0.4rem; font-size:0.85rem;'>📨 {r['name']} ({r['phone']}) — {r['status']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='alert-info'>⚠️ No emergency contacts found. Add contacts to receive SMS alerts.</div>", unsafe_allow_html=True)

            else:
                st.session_state.accident_active = False
                st.markdown(f"""
                <div class='alert-success'>
                    ✅ <b>Normal — No Accident Detected</b><br>
                    <span style='font-size:0.88rem;'>{result['reason']}</span>
                </div>
                """, unsafe_allow_html=True)

        else:
            # Idle state
            if st.session_state.accident_active:
                st.markdown("<div class='alert-danger'>🚨 LAST SIMULATION DETECTED AN ACCIDENT — Press 'CLEAR ALERT' to reset.</div>", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='card' style='text-align:center; padding:3rem;'>
                    <div style='font-size:3rem; margin-bottom:1rem;'>🪖</div>
                    <div style='font-family:Orbitron; color:#6B7A94; font-size:0.9rem;'>
                        SELECT A SIMULATION TYPE AND CLICK<br>"SIMULATE ACCIDENT" TO TEST THE SYSTEM
                    </div>
                </div>
                """, unsafe_allow_html=True)


def page_emergency_contacts():
    if not st.session_state.logged_in:
        st.warning("🔒 Please log in."); return

    user = st.session_state.user
    st.markdown("<h1 style='color:#FF2D2D; font-family:Orbitron;'>👥 EMERGENCY CONTACTS</h1>", unsafe_allow_html=True)

    col_add, col_list = st.columns([1,2])

    with col_add:
        st.markdown("<h3 style='color:#FF2D2D; font-size:0.95rem;'>ADD CONTACT</h3>", unsafe_allow_html=True)
        with st.form("add_contact_form"):
            c_name     = st.text_input("Name *",         placeholder="Contact's full name")
            c_phone    = st.text_input("Phone Number *",  placeholder="+91 XXXXXXXXXX")
            c_relation = st.selectbox("Relation", ["Parent","Spouse","Sibling","Friend","Doctor","Other"])
            c_submit   = st.form_submit_button("➕ ADD CONTACT", use_container_width=True)
            if c_submit:
                if not c_name or not c_phone:
                    st.error("Name and phone are required.")
                else:
                    db.add_emergency_contact(user["id"], c_name, c_phone, c_relation)
                    st.success(f"✅ {c_name} added!")
                    st.rerun()

    with col_list:
        st.markdown("<h3 style='color:#FF2D2D; font-size:0.95rem;'>YOUR CONTACTS</h3>", unsafe_allow_html=True)
        contacts = db.get_emergency_contacts(user["id"])
        if not contacts:
            st.markdown("<div class='alert-info'>No contacts yet. Add your first emergency contact.</div>", unsafe_allow_html=True)
        else:
            for c in contacts:
                col_info, col_del = st.columns([4,1])
                with col_info:
                    st.markdown(f"""
                    <div class='card' style='padding:0.9rem;'>
                        <div style='font-family:Orbitron; font-size:0.85rem; color:#FF2D2D;'>👤 {c['name']}</div>
                        <div style='color:#E8EDF5; font-size:0.85rem; margin-top:4px;'>📞 {c['phone']}</div>
                        <div style='color:#6B7A94; font-size:0.75rem;'>🔗 {c['relation']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_del:
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    if st.button("🗑", key=f"del_{c['id']}"):
                        db.delete_emergency_contact(c["id"])
                        st.rerun()


def page_live_location():
    if not st.session_state.logged_in:
        st.warning("🔒 Please log in."); return

    st.markdown("<h1 style='color:#FF2D2D; font-family:Orbitron;'>📍 LIVE GPS LOCATION</h1>", unsafe_allow_html=True)

    col_map, col_info = st.columns([3,2])

    with col_info:
        st.markdown("<h3 style='color:#FF2D2D; font-size:0.95rem;'>LOCATION DATA</h3>", unsafe_allow_html=True)

        loc = simulate_gps_location(
            st.session_state.last_location["latitude"]  if st.session_state.last_location else None,
            st.session_state.last_location["longitude"] if st.session_state.last_location else None,
        )
        st.session_state.last_location = loc
        maps_url = f"https://maps.google.com/?q={loc['latitude']},{loc['longitude']}"

        st.markdown(f"""
        <div class='gps-box'>
            📡 GPS LOCK ACQUIRED<br><br>
            LAT: {loc['latitude']}<br>
            LON: {loc['longitude']}<br>
            ACC: ±{loc['accuracy']} m<br>
            SPD: {loc['speed_kmh']} km/h<br>
            <br>
            <a href='{maps_url}' target='_blank' style='color:#00E676;'>
                🗺 Open in Google Maps ↗
            </a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🔄 REFRESH LOCATION", use_container_width=True):
            st.rerun()

        if st.button("▶ START LIVE TRACKING (5s)", use_container_width=True):
            placeholder = st.empty()
            for i in range(5):
                l = simulate_gps_location(loc["latitude"], loc["longitude"])
                st.session_state.last_location = l
                placeholder.markdown(f"""
                <div class='card' style='padding:0.8rem; font-size:0.82rem;'>
                    Update {i+1}/5 · {l['latitude']}, {l['longitude']} · {l['speed_kmh']} km/h
                </div>
                """, unsafe_allow_html=True)
                time.sleep(1)
            st.success("✅ Tracking complete.")

    with col_map:
        import pandas as pd
        route = generate_route_history(15)
        df = pd.DataFrame(route).rename(columns={"lat":"lat","lon":"lon"})
        # Add current loc
        df2 = pd.DataFrame([{"lat": loc["latitude"], "lon": loc["longitude"]}])
        st.markdown("<h3 style='color:#FF2D2D; font-size:0.95rem;'>ROUTE MAP</h3>", unsafe_allow_html=True)
        st.map(pd.concat([df, df2]).rename(columns={"lat":"latitude","lon":"longitude"}), zoom=13)


def page_sms_alerts():
    if not st.session_state.logged_in:
        st.warning("🔒 Please log in."); return

    user = st.session_state.user
    st.markdown("<h1 style='color:#FF2D2D; font-family:Orbitron;'>📱 SMS ALERT SYSTEM</h1>", unsafe_allow_html=True)

    st.markdown("""
    <div class='twilio-notice'>
        ⚠️ <b>Twilio Integration:</b> Real SMS requires valid Twilio credentials in <code>sms.py</code>.
        Configure <code>TWILIO_SID</code>, <code>TWILIO_AUTH_TOKEN</code>, and <code>TWILIO_FROM</code>.
        Without credentials, alerts are <b>simulated</b> locally.
    </div><br>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1,1])

    with col1:
        st.markdown("<h3 style='color:#FF2D2D; font-size:0.95rem;'>📤 SEND TEST ALERT</h3>", unsafe_allow_html=True)
        contacts = db.get_emergency_contacts(user["id"])
        loc      = st.session_state.last_location or simulate_gps_location()

        if not contacts:
            st.markdown("<div class='alert-info'>⚠️ Add emergency contacts first.</div>", unsafe_allow_html=True)
        else:
            selected = st.multiselect("Select contacts", [c["name"] for c in contacts],
                                      default=[contacts[0]["name"]])
            alert_type = st.selectbox("Alert Type", ["Test Alert","High Impact Crash","Free Fall","Rapid Rotation"])

            msg_preview = build_alert_message(user.get("full_name") or user["username"], loc, alert_type)
            st.markdown("<div style='color:#6B7A94; font-size:0.8rem; margin-bottom:4px;'>MESSAGE PREVIEW:</div>", unsafe_allow_html=True)
            st.code(msg_preview, language="")

            if st.button("📱 SEND ALERT NOW", use_container_width=True):
                chosen = [c for c in contacts if c["name"] in selected]
                if not chosen:
                    st.error("Select at least one contact.")
                else:
                    results = send_sms_alert(user["id"], user.get("full_name") or user["username"],
                                             chosen, loc, alert_type)
                    for r in results:
                        st.markdown(f"<div class='alert-success' style='margin-bottom:4px; font-size:0.85rem;'>📨 {r['name']} ({r['phone']}): {r['status']}</div>", unsafe_allow_html=True)
                    st.rerun()

    with col2:
        st.markdown("<h3 style='color:#FF2D2D; font-size:0.95rem;'>📋 ALERT HISTORY</h3>", unsafe_allow_html=True)
        logs = db.get_sms_logs(user["id"])
        if not logs:
            st.markdown("<div class='alert-info'>No alerts sent yet.</div>", unsafe_allow_html=True)
        else:
            for log in logs[:10]:
                st.markdown(f"""
                <div class='card' style='padding:0.8rem;'>
                    <div style='display:flex; justify-content:space-between;'>
                        <b style='font-size:0.85rem;'>📞 {log['contact_name']} ({log['contact_phone']})</b>
                        <span style='color:#00E676; font-size:0.78rem;'>{log['status']}</span>
                    </div>
                    <div style='color:#6B7A94; font-size:0.75rem; margin-top:4px;'>
                        🕐 {utils.time_ago(log['timestamp'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)


def page_reviews():
    if not st.session_state.logged_in:
        st.warning("🔒 Please log in."); return

    user = st.session_state.user
    st.markdown("<h1 style='color:#FF2D2D; font-family:Orbitron;'>⭐ REVIEWS & FEEDBACK</h1>", unsafe_allow_html=True)

    col_form, col_reviews = st.columns([1,1])

    with col_form:
        st.markdown("<h3 style='color:#FF2D2D; font-size:0.95rem;'>✍️ SUBMIT REVIEW</h3>", unsafe_allow_html=True)
        with st.form("review_form"):
            rating  = st.slider("Rating", 1, 5, 5)
            st.markdown(f"<div style='font-size:1.5rem;'>{'⭐'*rating}{'☆'*(5-rating)}</div>", unsafe_allow_html=True)
            comment = st.text_area("Feedback", placeholder="Share your experience...", height=130)
            r_sub   = st.form_submit_button("⭐ SUBMIT", use_container_width=True)
            if r_sub:
                if not comment.strip():
                    st.error("Please write a comment.")
                else:
                    db.submit_review(user["id"], user["username"], rating, comment.strip())
                    st.success("✅ Thank you!")
                    st.rerun()

        all_r = db.get_all_reviews()
        if all_r:
            avg = sum(r["rating"] for r in all_r) / len(all_r)
            st.markdown(f"""
            <div class='card' style='text-align:center; margin-top:1rem;'>
                <div style='font-size:2rem;'>{'⭐'*round(avg)}{'☆'*(5-round(avg))}</div>
                <div style='font-family:Orbitron; font-size:1.8rem; color:#FF2D2D;'>{avg:.1f}/5</div>
                <div style='color:#6B7A94; font-size:0.8rem;'>{len(all_r)} review(s)</div>
            </div>
            """, unsafe_allow_html=True)

    with col_reviews:
        st.markdown("<h3 style='color:#FF2D2D; font-size:0.95rem;'>💬 ALL REVIEWS</h3>", unsafe_allow_html=True)
        reviews = db.get_all_reviews()
        if not reviews:
            st.markdown("<div class='alert-info'>No reviews yet.</div>", unsafe_allow_html=True)
        else:
            for r in reviews:
                st.markdown(f"""
                <div class='review-card'>
                    <div style='display:flex; justify-content:space-between;'>
                        <b style='font-size:0.88rem;'>👤 {r['username']}</b>
                        <span style='font-size:1rem;'>{'⭐'*r['rating']}{'☆'*(5-r['rating'])}</span>
                    </div>
                    <p style='color:#E8EDF5; font-size:0.85rem; margin:0.4rem 0;'>{r['comment']}</p>
                    <div style='color:#6B7A94; font-size:0.72rem;'>🕐 {utils.time_ago(r['timestamp'])}</div>
                </div>
                """, unsafe_allow_html=True)


def page_terms():
    st.markdown("<h1 style='color:#FF2D2D; font-family:Orbitron;'>📜 TERMS & CONDITIONS</h1>", unsafe_allow_html=True)
    sections = [
        ("1. Acceptance", "By using this system, you agree to these terms."),
        ("2. Simulation Only", "This app is a SOFTWARE SIMULATION. It does not connect to real hardware. All sensor data and GPS are simulated."),
        ("3. Not Emergency Services", "Do NOT rely on this app in a real emergency. Always call 112 (India) or your local emergency number."),
        ("4. Data Storage", "Data is stored locally in SQLite. Nothing is transmitted to external servers unless Twilio is configured."),
        ("5. Twilio / SMS", "Real SMS alerts require valid Twilio credentials. You are responsible for Twilio account usage and costs."),
        ("6. Limitation of Liability", "Developers are not liable for damages arising from use or misuse of this software."),
    ]
    for title, content in sections:
        st.markdown(f"""
        <div class='card'>
            <h3 style='color:#FF2D2D; margin:0 0 0.4rem; font-size:0.95rem;'>{title}</h3>
            <p style='color:#E8EDF5; margin:0; font-size:0.88rem; line-height:1.7;'>{content}</p>
        </div>
        """, unsafe_allow_html=True)

# ──────────────────────────── ROUTER ──────────────────────────────────────

def main():
    render_sidebar()
    page = st.session_state.page
    dispatch = {
        "🏠 Home":               page_home,
        "🔐 Login / Register":   page_login,
        "📊 Dashboard":          page_dashboard,
        "💥 Accident Detection": page_accident_detection,
        "👥 Emergency Contacts": page_emergency_contacts,
        "📍 Live Location":      page_live_location,
        "📱 SMS Alerts":         page_sms_alerts,
        "⭐ Reviews":            page_reviews,
        "📜 Terms & Conditions": page_terms,
    }
    dispatch.get(page, page_home)()

if __name__ == "__main__":
    main()
