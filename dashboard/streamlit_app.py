import json
import time
from typing import Dict, Any, Tuple

import requests
import streamlit as st
import streamlit.components.v1 as components


# -----------------------------
# Config & Styling
# -----------------------------
st.set_page_config(
    page_title="AI Fault Predictor — Network Pulse",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Google Font + Futuristic UI CSS (Isora-inspired)
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
:root{
  --bg-1:#0b1224; --bg-2:#0a0f1c; --bg-3:#0b0f1a;
  --glass: rgba(255,255,255,0.07);
  --border: rgba(255,255,255,0.12);
  --text:#eef4ff; --muted:#a8b3d6;
  --cyan:#00e5ff; --purple:#9b5de5; --green:#2ecc71; --red:#ff5c5c; --orange:#ff9f43;
}

/* Animated gradient background */
body {
  background: linear-gradient(120deg, var(--bg-1), var(--bg-2), var(--bg-3));
  background-size: 200% 200%;
  animation: gradientShift 18s ease infinite;
  font-family: 'Poppins', sans-serif !important;
}
@keyframes gradientShift { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }

/* Glass card */
.glass-card {
  background: var(--glass);
  border: 1px solid var(--border);
  border-radius: 18px;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 12px 40px rgba(0,0,0,0.35);
  padding: 18px 22px;
}

/* Header */
.title { color: var(--text); font-weight:700; font-size:34px; letter-spacing:.2px; }
.subtitle { color: var(--muted); font-size:15px; }

/* CTA Button */
.cta {
  display:inline-block; margin-top:10px; padding:10px 16px; border-radius:12px; color:#031018; font-weight:700;
  background: linear-gradient(90deg, var(--cyan), var(--purple)); border:none; box-shadow:0 8px 24px rgba(0,229,255,0.25);
  transition: transform .15s ease, box-shadow .15s ease; text-decoration:none;
}
.cta:hover { transform: translateY(-2px); box-shadow:0 14px 36px rgba(155,93,229,0.35); }

/* Badges */
.badge{ display:inline-flex; align-items:center; gap:6px; padding:6px 12px; border-radius:999px; font-weight:700; border:1px solid var(--border); }
.ok{ background: rgba(0,229,255,0.10); color:#8af6ff; border-color: rgba(0,229,255,0.35); }
.err{ background: rgba(255,92,92,0.10); color:#ffb1b1; border-color: rgba(255,92,92,0.35); }

/* Sections */
.section-title{ color: var(--text); font-weight:700; margin: 6px 0 10px; }
.hr{ height:1px; background:linear-gradient(90deg,transparent, rgba(255,255,255,0.25), transparent); margin:10px 0 16px; }
.help{ color: var(--muted); font-size:12px; }

/* Inputs container with severity outline */
.field-wrap{ border:1px solid var(--border); border-radius:12px; padding:10px 12px; transition:border-color .2s ease, box-shadow .2s ease; }
.sev-ok{ box-shadow: 0 0 0 0 rgba(0,0,0,0); }
.sev-warn{ border-color: rgba(255,159,67,.55); box-shadow: 0 0 0 2px rgba(255,159,67,.15) inset; }
.sev-bad{ border-color: rgba(255,92,92,.6); box-shadow: 0 0 0 2px rgba(255,92,92,.18) inset; }

/* Progress bar */
.progress-wrap { width:100%; height:14px; border-radius:10px; overflow:hidden; border:1px solid var(--border); background:rgba(255,255,255,0.06); }
.progress-bar { height:100%; background: linear-gradient(90deg, var(--purple), var(--cyan)); transition: width .6s ease; }

/* Confidence arc container */
.arc-wrap{ display:flex; align-items:center; gap:12px; }

.foot{ color:#a7b7e6; font-size:12px; opacity:.85; }

/* Subtle pulse for live status */
.pulse { position:relative; }
.pulse:after{
  content:""; position:absolute; left:-6px; top:-6px; right:-6px; bottom:-6px; border-radius:999px;
  background: radial-gradient(closest-side, rgba(0,229,255,.20), transparent);
  animation:pulse 1.8s ease infinite; opacity:.6;
}
@keyframes pulse { 0%{transform:scale(.95)} 50%{transform:scale(1.05)} 100%{transform:scale(.95)} }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------
# Helpers
# -----------------------------
def get_api_base() -> str:
    return st.session_state.get("api_base", "http://127.0.0.1:8000")


def set_api_base(url: str) -> None:
    st.session_state["api_base"] = url.rstrip("/")


def fetch_health(base_url: str) -> Tuple[bool, Dict[str, Any]]:
    try:
        r = requests.get(f"{base_url}/", timeout=5)
        return True, r.json()
    except Exception as e:
        return False, {"error": str(e)}


def post_predict(base_url: str, payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    try:
        r = requests.post(f"{base_url}/predict", json=payload, timeout=10)
        if r.status_code == 200:
            return True, r.json()
        else:
            return False, {"status_code": r.status_code, "detail": safe_json(r)}
    except Exception as e:
        return False, {"error": str(e)}


def safe_json(resp) -> Any:
    try:
        return resp.json()
    except Exception:
        return resp.text


def threshold_hint(name: str, value: float) -> str:
    # Standardized hints (normalized thinking not enforced on backend):
    # RSSI/SINR/throughput better high; latency/jitter/loss better low
    if name == "RSSI":
        if value < -85: return "🔴 Weak signal (< -85 dBm)"
        if value < -70: return "🟠 Degraded signal"
        return "🟢 Normal"
    if name == "SINR":
        if value < 10: return "🔴 Low SINR (< 10 dB)"
        if value < 15: return "🟠 Borderline"
        return "🟢 Normal"
    if name == "throughput":
        if value < 50: return "🔴 Low throughput (< 50 Mbps)"
        if value < 80: return "🟠 Below normal"
        return "🟢 Normal"
    if name == "latency":
        if value > 50: return "🔴 High latency (> 50 ms)"
        if value > 20: return "🟠 Elevated"
        return "🟢 Normal"
    if name == "jitter":
        if value > 15: return "🔴 High jitter (> 15 ms)"
        if value > 5: return "🟠 Elevated"
        return "🟢 Normal"
    if name == "packet_loss":
        if value > 3: return "🔴 High loss (> 3%)"
        if value > 1: return "🟠 Elevated"
        return "🟢 Normal"
    return ""


def severity_class(name: str, value: float) -> str:
    # Map to CSS class for input container outline
    hint = threshold_hint(name, value)
    if hint.startswith("🔴"): return "sev-bad"
    if hint.startswith("🟠"): return "sev-warn"
    return "sev-ok"


# -----------------------------
# Header / Intro
# -----------------------------
st.markdown(
    """
    <div class="glass-card">
      <div class="title">AI‑Powered Fault Predictor</div>
      <div class="subtitle">Analyze real‑time 5G network signals and detect potential faults instantly.</div>
      <a class="cta" href="#predict-form">Start Prediction ⚡</a>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Sidebar: API settings + Health
# -----------------------------
with st.sidebar:
    st.markdown("### API Settings")
    api_base = st.text_input("FastAPI Base URL", value=get_api_base(), help="Example: http://127.0.0.1:8000")
    if st.button("Save API URL"):
        set_api_base(api_base)
        st.success("Saved.")

    st.markdown("\n### Service Health")
    ok, health = fetch_health(get_api_base())
    if ok and isinstance(health, dict):
        st.markdown(
            f"<span class='badge {'ok pulse' if health.get('status')=='ok' else 'err'}'>🩺 status: {health.get('status')}</span>",
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                f"<span class='badge {'ok' if health.get('model_loaded') else 'err'}'>🧠 Model</span>",
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"<span class='badge {'ok' if health.get('scaler_loaded') else 'err'}'>📏 Scaler</span>",
                unsafe_allow_html=True,
            )
        st.caption(
            f"Expected features: {health.get('expected_feature_count')} • Scaler features: {health.get('scaler_feature_count')} • "
            f"Scaler compatible: {health.get('scaler_compatible')}"
        )
    else:
        st.markdown("<span class='badge err'>Service Unreachable</span>", unsafe_allow_html=True)
        if isinstance(health, dict) and health.get("error"):
            st.caption(health.get("error"))


# -----------------------------
# Input Form
# -----------------------------
st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-title' id='predict-form'>Input Parameters</div>", unsafe_allow_html=True)

with st.form("predict_form"):
    col1, col2 = st.columns(2)
    with col1:
        rssi_default = -80.0
        rssi_curr = st.session_state.get("RSSI", rssi_default)
        st.markdown(f"<div class='field-wrap {severity_class('RSSI', rssi_curr)}'>", unsafe_allow_html=True)
        RSSI = st.number_input("RSSI (dBm)", value=rssi_default, step=1.0, help="Normal: -70 to -50; Faulty: -110 to -90", key="RSSI")
        st.markdown("</div>", unsafe_allow_html=True)

        sinr_default = 12.0
        sinr_curr = st.session_state.get("SINR", sinr_default)
        st.markdown(f"<div class='field-wrap {severity_class('SINR', sinr_curr)}'>", unsafe_allow_html=True)
        SINR = st.number_input("SINR (dB)", value=sinr_default, step=0.5, help="Normal: 15 to 30; Faulty: -5 to 5", key="SINR")
        st.markdown("</div>", unsafe_allow_html=True)

        thr_default = 60.0
        thr_curr = st.session_state.get("throughput", thr_default)
        st.markdown(f"<div class='field-wrap {severity_class('throughput', thr_curr)}'>", unsafe_allow_html=True)
        throughput = st.number_input("Throughput (Mbps)", value=thr_default, step=1.0, help="Normal: 80 to 150; Faulty: 10 to 40", key="throughput")
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        lat_default = 30.0
        lat_curr = st.session_state.get("latency", lat_default)
        st.markdown(f"<div class='field-wrap {severity_class('latency', lat_curr)}'>", unsafe_allow_html=True)
        latency = st.number_input("Latency (ms)", value=lat_default, step=1.0, help="Normal: 5 to 20; Faulty: 80 to 200", key="latency")
        st.markdown("</div>", unsafe_allow_html=True)

        jit_default = 8.0
        jit_curr = st.session_state.get("jitter", jit_default)
        st.markdown(f"<div class='field-wrap {severity_class('jitter', jit_curr)}'>", unsafe_allow_html=True)
        jitter = st.number_input("Jitter (ms)", value=jit_default, step=0.5, help="Normal: 1 to 5; Faulty: 20 to 50", key="jitter")
        st.markdown("</div>", unsafe_allow_html=True)

        loss_default = 1.5
        loss_curr = st.session_state.get("packet_loss", loss_default)
        st.markdown(f"<div class='field-wrap {severity_class('packet_loss', loss_curr)}'>", unsafe_allow_html=True)
        packet_loss = st.number_input("Packet Loss (%)", value=loss_default, step=0.1, help="Normal: 0 to 1; Faulty: 5 to 20", key="packet_loss")
        st.markdown("</div>", unsafe_allow_html=True)

    st.caption(
        f"Hints: RSSI → {threshold_hint('RSSI', RSSI)} • SINR → {threshold_hint('SINR', SINR)} • Throughput → {threshold_hint('throughput', throughput)}"
    )
    st.caption(
        f"Latency → {threshold_hint('latency', latency)} • Jitter → {threshold_hint('jitter', jitter)} • Loss → {threshold_hint('packet_loss', packet_loss)}"
    )

    with st.expander("Advanced Settings (optional)"):
        c1, c2, c3 = st.columns(3)
        with c1:
            cpu_default = 70.0
            cpu_curr = st.session_state.get("cpu_usage_percent", cpu_default)
            st.markdown(f"<div class='field-wrap {severity_class('cpu_usage_percent', cpu_curr)}'>", unsafe_allow_html=True)
            cpu = st.number_input("CPU Usage (%)", value=cpu_default, step=1.0, min_value=0.0, max_value=100.0, key="cpu_usage_percent")
            st.markdown("</div>", unsafe_allow_html=True)

            mem_default = 65.0
            mem_curr = st.session_state.get("memory_usage_percent", mem_default)
            st.markdown(f"<div class='field-wrap {severity_class('memory_usage_percent', mem_curr)}'>", unsafe_allow_html=True)
            mem = st.number_input("Memory Usage (%)", value=mem_default, step=1.0, min_value=0.0, max_value=100.0, key="memory_usage_percent")
            st.markdown("</div>", unsafe_allow_html=True)

            temp = st.number_input("Temperature (°C)", value=45.0, step=0.5, key="temperature_celsius")
        with c2:
            users = st.number_input("Active Users", value=350.0, step=1.0, min_value=0.0, key="active_users")
            hour = st.number_input("Hour (0-23)", value=15.0, step=1.0, min_value=0.0, max_value=23.0, key="hour")
            dow = st.number_input("Day of Week (0-6)", value=3.0, step=1.0, min_value=0.0, max_value=6.0, key="day_of_week")
        with c3:
            is_peak = st.selectbox("Is Peak Hour", options=[0, 1], index=1, key="is_peak_hour")
            nqs = st.number_input("Network Quality Score (0-1)", value=0.6, step=0.01, min_value=0.0, max_value=1.0, key="network_quality_score")
            stress = st.number_input("Resource Stress (0-100)", value=70.0, step=1.0, min_value=0.0, max_value=100.0, key="resource_stress")

    submitted = st.form_submit_button("Predict ⚡")

payload = {
    "RSSI": RSSI,
    "SINR": SINR,
    "throughput": throughput,
    "latency": latency,
    "jitter": jitter,
    "packet_loss": packet_loss,
}

# Only include optional params if expander was opened and values adjusted; here we include by default for alignment
payload.update({
    "cpu_usage_percent": cpu,
    "memory_usage_percent": mem,
    "active_users": users,
    "temperature_celsius": temp,
    "hour": hour,
    "day_of_week": dow,
    "is_peak_hour": float(is_peak),
    "network_quality_score": nqs,
    "resource_stress": stress,
})


# -----------------------------
# Submit & Result
# -----------------------------
if submitted:
    with st.spinner("Analyzing network signals…"):
        ok, result = post_predict(get_api_base(), payload)
        time.sleep(0.3)

    if ok:
        pred = result.get("prediction", "?")
        prob = result.get("probability_faulty")
        conf = result.get("confidence_percent")

        # Save to history in session
        hist = st.session_state.get("history", [])
        hist.insert(0, {"payload": payload, "result": result})
        st.session_state["history"] = hist[:5]

        # Result card (animated gradient accent)
        st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Result</div>", unsafe_allow_html=True)
        with st.container():
            badge_cls = "ok" if pred == "Normal" else "err"
            st.markdown(f"<div class='glass-card'><span class='badge {badge_cls}'>Prediction: {pred}</span>", unsafe_allow_html=True)

            # Confidence arc (SVG)
            if conf is not None:
                pct = max(0, min(100, float(conf)))
                # SVG circular progress approximation
                radius = 40
                circ = 2 * 3.1416 * radius
                dash = circ * pct / 100.0
                st.markdown("""
                <div class='arc-wrap'>
                  <svg width="110" height="110" viewBox="0 0 120 120">
                    <circle cx="60" cy="60" r="40" stroke="rgba(255,255,255,0.15)" stroke-width="10" fill="none" />
                    <circle cx="60" cy="60" r="40" stroke="url(#grad1)" stroke-width="10" fill="none" stroke-linecap="round"
                            stroke-dasharray="{dash} {rest}" transform="rotate(-90 60 60)" />
                    <defs>
                      <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" style="stop-color:#9b5de5;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#00f5d4;stop-opacity:1" />
                      </linearGradient>
                    </defs>
                    <text x="60" y="65" text-anchor="middle" fill="#e6f1ff" font-size="16" font-weight="700">{pct}%</text>
                  </svg>
                  <div>
                    <div class='help'>Model Confidence</div>
                    <div style='color:#e6f1ff;font-weight:700'>{pct}%</div>
                  </div>
                </div>
                """.replace("{dash}", f"{dash:.2f}").replace("{rest}", f"{circ - dash:.2f}").replace("{pct}", f"{pct:.2f}"), unsafe_allow_html=True)

            if prob is not None:
                p100 = max(0, min(100, int(round(prob * 100))))
                st.markdown("<div class='help'>Fault likelihood</div>", unsafe_allow_html=True)
                st.markdown(
                    f"<div class='progress-wrap'><div class='progress-bar' style='width:{p100}%;'></div></div>",
                    unsafe_allow_html=True,
                )

            # Guidance text
            if conf is not None and conf < 60:
                st.caption("Low confidence — additional metrics recommended.")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("Prediction failed")
        st.code(json.dumps(result, indent=2))


# -----------------------------
# History (optional)
# -----------------------------
if st.session_state.get("history"):
    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Recent Predictions</div>", unsafe_allow_html=True)
    for i, item in enumerate(st.session_state["history"], start=1):
        res = item.get("result", {})
        st.markdown(f"**#{i}** — {res.get('prediction', '?')} • confidence: {res.get('confidence_percent', '—')}%")


# -----------------------------
# Footer
# -----------------------------
st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
st.markdown("<div class='foot'>Tip: Ensure the FastAPI server is running and health shows Model/Scaler loaded.</div>", unsafe_allow_html=True)


