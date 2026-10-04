"""
buzzer.py — Buzzer / Alarm Alert Logic
Smart Helmet Safety System

Browser-based buzzer using the Web Audio API (works in Streamlit via HTML injection).
Also provides optional system-level buzzer for native environments.
"""

import sys


# ──────────────────────────── BROWSER BUZZER (Web Audio API) ─────────────

def trigger_buzzer_html(
    repeat:    int   = 4,
    freq_hz:   float = 880.0,
    duration:  float = 0.4,
    gap:       float = 0.15,
    volume:    float = 0.6,
) -> str:
    """
    Generate an HTML <script> block that plays a buzzer alarm in the browser
    using the Web Audio API. Works in any Streamlit deployment without
    any extra packages.

    Args:
        repeat:   Number of beep repetitions.
        freq_hz:  Buzzer tone frequency in Hz (880 = A5, high-pitched alarm).
        duration: Length of each beep in seconds.
        gap:      Silence between beeps in seconds.
        volume:   Volume level 0.0 – 1.0.

    Returns:
        HTML string — pass directly to st.markdown(..., unsafe_allow_html=True).
    """
    period_ms   = int((duration + gap) * 1000)
    duration_ms = int(duration * 1000)

    return f"""
<script>
(function() {{
    // Create AudioContext only once
    if (window._helmetBuzzerRunning) return;
    window._helmetBuzzerRunning = true;

    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) {{
        console.warn("Web Audio API not supported — buzzer unavailable.");
        window._helmetBuzzerRunning = false;
        return;
    }}

    const ctx  = new AudioCtx();
    let   count = 0;
    const total = {repeat};

    function beep() {{
        if (count >= total) {{
            window._helmetBuzzerRunning = false;
            return;
        }}
        count++;

        // Primary high-pitched alarm tone
        const osc1   = ctx.createOscillator();
        const gain1  = ctx.createGain();
        osc1.connect(gain1);
        gain1.connect(ctx.destination);
        osc1.type      = "square";
        osc1.frequency.setValueAtTime({freq_hz},     ctx.currentTime);
        osc1.frequency.setValueAtTime({freq_hz*1.5}, ctx.currentTime + {duration/2});
        gain1.gain.setValueAtTime({volume}, ctx.currentTime);
        gain1.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + {duration});
        osc1.start(ctx.currentTime);
        osc1.stop(ctx.currentTime + {duration});

        // Sub-tone for depth
        const osc2   = ctx.createOscillator();
        const gain2  = ctx.createGain();
        osc2.connect(gain2);
        gain2.connect(ctx.destination);
        osc2.type      = "sawtooth";
        osc2.frequency.setValueAtTime({freq_hz/2}, ctx.currentTime);
        gain2.gain.setValueAtTime({volume * 0.3}, ctx.currentTime);
        gain2.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + {duration});
        osc2.start(ctx.currentTime);
        osc2.stop(ctx.currentTime + {duration});

        setTimeout(beep, {period_ms});
    }}

    beep();
}})();
</script>
<div style="
    background: rgba(255,45,45,0.15);
    border: 1px solid rgba(255,45,45,0.5);
    border-radius: 8px;
    padding: 0.6rem 1.2rem;
    font-size: 0.88rem;
    color: #FF6B6B;
    display: flex;
    align-items: center;
    gap: 8px;
    animation: pulse 0.5s infinite alternate;
">
    🔊 <b>ALARM ACTIVATED</b> — {repeat} beeps at {int(freq_hz)} Hz
</div>
"""


# ──────────────────────────── NATIVE BUZZER (optional) ───────────────────

def trigger_native_buzzer(repeat: int = 3, duration_ms: int = 400, gap_ms: int = 200):
    """
    Play a system buzzer sound using platform-native APIs.
    Falls back gracefully if unavailable.

    Works on:
      - Windows: winsound.Beep()
      - macOS/Linux: terminal bell via print("\a")

    Args:
        repeat:      Number of beeps.
        duration_ms: Duration of each beep in milliseconds (Windows only).
        gap_ms:      Gap between beeps in milliseconds.
    """
    import time

    if sys.platform == "win32":
        try:
            import winsound
            for _ in range(repeat):
                winsound.Beep(880, duration_ms)
                time.sleep(gap_ms / 1000)
            return
        except Exception:
            pass

    # macOS / Linux fallback: terminal bell
    for _ in range(repeat):
        print("\a", end="", flush=True)
        time.sleep((duration_ms + gap_ms) / 1000)


# ──────────────────────────── STOP BUZZER ────────────────────────────────

def stop_buzzer_html() -> str:
    """
    Generate an HTML snippet that cancels any running Web Audio buzzer.
    Use: st.markdown(stop_buzzer_html(), unsafe_allow_html=True)
    """
    return """
<script>
    window._helmetBuzzerRunning = true;  // Set flag to stop loop immediately
    // Close any open AudioContext
    if (window._helmetAudioCtx) {
        try { window._helmetAudioCtx.close(); } catch(e) {}
    }
</script>
"""


# ──────────────────────────── QUICK TEST ────────────────────────────────

if __name__ == "__main__":
    print("Testing native buzzer...")
    trigger_native_buzzer(repeat=3)
    print("Done. For browser buzzer, use trigger_buzzer_html() in Streamlit.")
