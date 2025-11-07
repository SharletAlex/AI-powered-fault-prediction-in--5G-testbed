import json
import time
from datetime import datetime
from typing import Any, Dict, Tuple

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
from streamlit import rerun as experimental_rerun

# -----------------------------
# Config & Styling
# -----------------------------
st.set_page_config(
    page_title="AI Fault Predictor — Network Pulse",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Professional Modern UI CSS with Perfect Color Harmony
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
  /* Professional Color Palette - Corporate Blue/Slate */
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-tertiary: #334155;
  --bg-card: #1e293b;
  
  /* Glass Effects */
  --glass: rgba(30, 41, 59, 0.7);
  --glass-strong: rgba(30, 41, 59, 0.85);
  --glass-light: rgba(255, 255, 255, 0.03);
  
  /* Borders */
  --border: rgba(59, 130, 246, 0.1);
  --border-strong: rgba(59, 130, 246, 0.25);
  --border-hover: rgba(59, 130, 246, 0.4);
  
  /* Text Colors */
  --text-primary: #f1f5f9;
  --text-secondary: #cbd5e1;
  --text-muted: #94a3b8;
  --text-dim: #64748b;
  
  /* Brand Colors - Professional Blue Scheme */
  --primary: #3b82f6;
  --primary-light: #60a5fa;
  --primary-dark: #2563eb;
  --accent: #0ea5e9;
  --accent-light: #38bdf8;
  
  /* Status Colors - Carefully Selected */
  --success: #10b981;
  --success-light: #34d399;
  --success-bg: rgba(16, 185, 129, 0.1);
  
  --warning: #f59e0b;
  --warning-light: #fbbf24;
  --warning-bg: rgba(245, 158, 11, 0.1);
  
  --danger: #ef4444;
  --danger-light: #f87171;
  --danger-bg: rgba(239, 68, 68, 0.1);
  
  --info: #3b82f6;
  --info-light: #60a5fa;
  --info-bg: rgba(59, 130, 246, 0.1);
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.4);
  --shadow-glow: 0 0 30px rgba(59, 130, 246, 0.15);
  --shadow-glow-strong: 0 0 50px rgba(59, 130, 246, 0.25);
}

/* Professional Background with Subtle Gradient */
.main {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
  background-size: 200% 200%;
  animation: gradientFlow 20s ease infinite;
  position: relative;
  overflow-x: hidden;
  overflow-y: auto;
  min-height: 100vh;
}

@keyframes gradientFlow {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

/* Ensure app container allows scrolling */
html, body { height: auto !important; overflow-y: auto !important; }
[data-testid="stAppViewContainer"] { overflow-y: auto !important; }
section.main { overflow-y: auto !important; }

/* Subtle Grid Pattern Overlay */
.main::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 20% 30%, rgba(59, 130, 246, 0.08) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(14, 165, 233, 0.06) 0%, transparent 50%),
    linear-gradient(rgba(59, 130, 246, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59, 130, 246, 0.02) 1px, transparent 1px);
  background-size: 100% 100%, 100% 100%, 50px 50px, 50px 50px;
  pointer-events: none;
  z-index: 0;
  opacity: 0.4;
}

/* Content Layer Above Background */
.main > div {
  position: relative;
  z-index: 1;
}

/* Professional Typography */
* {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

h1, h2, h3, h4, h5, h6 {
  font-family: 'Space Grotesk', 'Inter', sans-serif;
  color: var(--text-primary);
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.2;
}

h1 { font-size: 2.5rem; }
h2 { font-size: 2rem; }
h3 { font-size: 1.5rem; }

p, label, span {
  color: var(--text-secondary);
  line-height: 1.6;
}

/* Professional Glass Cards with Perfect Depth */
.glass-card {
  background: linear-gradient(135deg, var(--glass) 0%, var(--glass-strong) 100%);
  border: 1px solid var(--border);
  border-radius: 16px;
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  box-shadow: 
    var(--shadow-lg),
    inset 0 1px 0 0 rgba(255, 255, 255, 0.05),
    0 0 0 1px rgba(0, 0, 0, 0.1);
  padding: 28px 32px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Subtle Top Border Highlight */
.glass-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    var(--primary) 50%,
    transparent
  );
  opacity: 0.5;
}

.glass-card:hover {
  transform: translateY(-2px);
  border-color: var(--border-hover);
  box-shadow: 
    var(--shadow-xl),
    var(--shadow-glow),
    inset 0 1px 0 0 rgba(255, 255, 255, 0.08);
}

/* Professional Hero Section */
.hero {
  text-align: center;
  padding: 80px 40px 60px;
  background: linear-gradient(
    135deg,
    rgba(59, 130, 246, 0.05) 0%,
    rgba(14, 165, 233, 0.05) 100%
  );
  border-radius: 20px;
  margin-bottom: 48px;
  position: relative;
  overflow: hidden;
  border: 1px solid var(--border);
}

/* Animated Border Glow */
.hero::before {
  content: '';
  position: absolute;
  inset: -2px;
  background: linear-gradient(
    45deg,
    var(--primary),
    var(--accent),
    var(--primary)
  );
  background-size: 200% 200%;
  border-radius: 20px;
  z-index: -1;
  opacity: 0.3;
  animation: borderRotate 4s linear infinite;
  filter: blur(8px);
}

@keyframes borderRotate {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.hero-title {
  font-size: 56px;
  font-weight: 800;
  background: linear-gradient(
    135deg,
    #ffffff 0%,
    var(--primary-light) 50%,
    var(--accent-light) 100%
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 20px;
  line-height: 1.1;
  letter-spacing: -0.03em;
}

.hero-subtitle {
  font-size: 18px;
  color: var(--text-secondary);
  margin-bottom: 36px;
  max-width: 640px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.7;
  font-weight: 400;
}

/* Professional CTA Button */
.cta-button {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 16px 32px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
  border: none;
  border-radius: 12px;
  color: #ffffff !important;
  font-weight: 700;
  font-size: 16px;
  text-decoration: none;
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 4px 16px rgba(99, 102, 241, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  cursor: pointer;
}

.cta-button:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 
    0 8px 24px rgba(99, 102, 241, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
  color: #ffffff !important;
  text-decoration: none;
}

.cta-button:active {
  transform: translateY(0) scale(0.98);
}

/* Ensure text inside button is always white */
.cta-button span {
  color: #ffffff !important;
}

/* Shimmer Effect on Hover */
.cta-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.3),
    transparent
  );
  transition: left 0.5s;
}

.cta-button:hover::before {
  left: 100%;
}

/* Professional Status Badges */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  border: 1px solid;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(8px);
}

.badge-success {
  background: var(--success-bg);
  border-color: var(--success);
  color: var(--success-light);
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.1);
}

.badge-error {
  background: var(--danger-bg);
  border-color: var(--danger);
  color: var(--danger-light);
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.1);
}

.badge-warning {
  background: var(--warning-bg);
  border-color: var(--warning);
  color: var(--warning-light);
  box-shadow: 0 0 20px rgba(245, 158, 11, 0.1);
}

.status-badge:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Pulse Animation for Live Status */
.pulse {
  position: relative;
}

.pulse::after {
  content: '';
  position: absolute;
  top: -4px;
  left: -4px;
  right: -4px;
  bottom: -4px;
  border-radius: 50px;
  background: radial-gradient(circle, rgba(88, 166, 255, 0.15) 0%, transparent 70%);
  animation: pulse 2s ease-in-out infinite;
  z-index: -1;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.7; }
  50% { transform: scale(1.1); opacity: 0.3; }
}

/* Professional Input Fields */
.input-container {
  margin-bottom: 24px;
  position: relative;
}

.input-field {
  background: linear-gradient(135deg, rgba(30, 36, 51, 0.4), rgba(30, 36, 51, 0.6));
  border: 1.5px solid var(--border);
  border-radius: 12px;
  padding: 18px 20px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.input-field:hover {
  border-color: var(--border-strong);
  background: linear-gradient(135deg, rgba(30, 36, 51, 0.5), rgba(30, 36, 51, 0.7));
}

.input-field:focus-within {
  border-color: var(--primary);
  box-shadow: 
    0 0 0 3px rgba(59, 130, 246, 0.1),
    0 4px 12px rgba(59, 130, 246, 0.15);
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.6), rgba(30, 41, 59, 0.8));
}

/* Status-Based Input Styling */
.input-field.status-normal {
  border-color: rgba(16, 185, 129, 0.4);
  background: linear-gradient(
    135deg,
    rgba(16, 185, 129, 0.03),
    rgba(30, 36, 51, 0.6)
  );
}

.input-field.status-normal:hover {
  border-color: var(--success);
  box-shadow: 0 0 0 1px rgba(16, 185, 129, 0.2);
}

.input-field.status-warning {
  border-color: rgba(245, 158, 11, 0.4);
  background: linear-gradient(
    135deg,
    rgba(245, 158, 11, 0.03),
    rgba(30, 36, 51, 0.6)
  );
}

.input-field.status-warning:hover {
  border-color: var(--warning);
  box-shadow: 0 0 0 1px rgba(245, 158, 11, 0.2);
}

.input-field.status-danger {
  border-color: rgba(239, 68, 68, 0.4);
  background: linear-gradient(
    135deg,
    rgba(239, 68, 68, 0.03),
    rgba(30, 36, 51, 0.6)
  );
}

.input-field.status-danger:hover {
  border-color: var(--danger);
  box-shadow: 0 0 0 1px rgba(239, 68, 68, 0.2);
}

/* Professional Prediction Result Card */
.result-card {
  background: linear-gradient(
    135deg,
    rgba(30, 36, 51, 0.6),
    rgba(30, 36, 51, 0.8)
  );
  border: 1.5px solid var(--border-strong);
  border-radius: 20px;
  padding: 40px;
  text-align: center;
  position: relative;
  overflow: hidden;
  animation: slideInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow-xl);
}

.result-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(
    90deg,
    transparent,
    var(--primary),
    transparent
  );
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.result-normal {
  background: linear-gradient(
    135deg,
    rgba(16, 185, 129, 0.08),
    rgba(30, 36, 51, 0.8)
  );
  border-color: var(--success);
  box-shadow: 
    var(--shadow-xl),
    0 0 40px rgba(16, 185, 129, 0.15);
}

.result-faulty {
  background: linear-gradient(
    135deg,
    rgba(239, 68, 68, 0.08),
    rgba(30, 36, 51, 0.8)
  );
  border-color: var(--danger);
  box-shadow: 
    var(--shadow-xl),
    0 0 40px rgba(239, 68, 68, 0.15);
}

.result-prediction {
  font-size: 32px;
  font-weight: 800;
  margin-bottom: 20px;
  letter-spacing: -0.02em;
}

.prediction-normal {
  color: var(--success-light);
  text-shadow: 0 0 30px rgba(16, 185, 129, 0.4);
}

.prediction-faulty {
  color: var(--danger-light);
  text-shadow: 0 0 30px rgba(239, 68, 68, 0.4);
}

/* Confidence Visualization */
.confidence-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 32px;
  margin: 32px 0;
}

.confidence-circle {
  position: relative;
  width: 120px;
  height: 120px;
}

.confidence-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

/* Professional Progress Bars */
.progress-container {
  margin: 28px 0;
}

.progress-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-bar-container {
  width: 100%;
  height: 12px;
  background: rgba(30, 36, 51, 0.6);
  border-radius: 10px;
  overflow: hidden;
  position: relative;
  border: 1px solid var(--border);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
}

.progress-bar {
  height: 100%;
  background: linear-gradient(
    90deg,
    var(--primary),
    var(--accent)
  );
  border-radius: 10px;
  transition: width 1.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  box-shadow: 0 0 12px rgba(59, 130, 246, 0.5);
}

.progress-bar::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.4),
    transparent
  );
  animation: progressShine 2.5s ease-in-out infinite;
}

@keyframes progressShine {
  0% { left: -100%; }
  100% { left: 100%; }
}

/* Professional History Timeline */
.history-timeline {
  position: relative;
  padding-left: 40px;
}

.history-timeline::before {
  content: '';
  position: absolute;
  left: 18px;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(
    180deg,
    var(--primary),
    var(--accent)
  );
  border-radius: 10px;
}

.history-item {
  position: relative;
  margin-bottom: 28px;
  padding: 20px 24px;
  background: linear-gradient(
    135deg,
    var(--glass),
    var(--glass-strong)
  );
  border: 1px solid var(--border);
  border-radius: 14px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow-md);
}

.history-item::before {
  content: '';
  position: absolute;
  left: -31px;
  top: 24px;
  width: 10px;
  height: 10px;
  background: var(--primary);
  border-radius: 50%;
  border: 2px solid var(--bg-primary);
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.6);
  z-index: 1;
}

.history-item:hover {
  transform: translateX(8px);
  border-color: var(--border-hover);
  box-shadow: var(--shadow-lg);
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero-title {
    font-size: 36px;
  }

  .hero-subtitle {
    font-size: 16px;
  }

  .confidence-container {
    flex-direction: column;
    gap: 20px;
  }
}

/* Loading Animations */
.loading-dots {
  display: inline-block;
}

.loading-dots::after {
  content: '...';
  animation: loadingDots 1.5s infinite;
}

@keyframes loadingDots {
  0%, 20% { content: '.'; }
  40% { content: '..'; }
  60%, 100% { content: '...'; }
}

/* Professional Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.metric-card {
  background: linear-gradient(
    135deg,
    var(--glass),
    var(--glass-strong)
  );
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

.metric-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(
    90deg,
    var(--primary),
    var(--accent)
  );
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.metric-card:hover::before {
  transform: scaleX(1);
}

.metric-card:hover {
  transform: translateY(-4px);
  border-color: var(--border-hover);
  box-shadow: var(--shadow-xl);
}

.metric-value {
  font-size: 28px;
  font-weight: 800;
  background: linear-gradient(
    135deg,
    var(--primary-light),
    var(--accent-light)
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 10px;
  letter-spacing: -0.02em;
}

.metric-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

/* Professional Utility Classes */
.text-gradient {
  background: linear-gradient(
    135deg,
    var(--primary-light),
    var(--accent-light)
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.glow {
  box-shadow: 0 0 30px rgba(59, 130, 246, 0.3);
}

.fade-in {
  animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes fadeIn {
  from { 
    opacity: 0;
    transform: translateY(10px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

/* Professional Scrollbar Styling */
::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-track {
  background: var(--bg-secondary);
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(
    180deg,
    var(--primary),
    var(--accent)
  );
  border-radius: 10px;
  border: 2px solid var(--bg-secondary);
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(
    180deg,
    var(--primary-light),
    var(--accent-light)
  );
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------
# Helper Functions
# -----------------------------
def get_api_base() -> str:
    return st.session_state.get("api_base", "http://127.0.0.1:8000")


def set_api_base(url: str) -> None:
    st.session_state["api_base"] = url.rstrip("/")


def fetch_health(base_url: str) -> Tuple[bool, Dict[str, Any]]:
    try:
        r = requests.get(f"{base_url}/", timeout=5)
        if r.status_code == 200:
            return True, r.json()
        else:
            return False, {"status_code": r.status_code, "detail": r.text}
    except requests.exceptions.ConnectionError:
        return False, {"error": "Connection failed - API server may be down"}
    except requests.exceptions.Timeout:
        return False, {"error": "Request timeout - API server is slow to respond"}
    except Exception as e:
        return False, {"error": f"Unexpected error: {str(e)}"}


def post_predict(base_url: str, payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    try:
        r = requests.post(f"{base_url}/predict", json=payload, timeout=15)
        if r.status_code == 200:
            return True, r.json()
        else:
            return False, {"status_code": r.status_code, "detail": r.text}
    except requests.exceptions.ConnectionError:
        return False, {"error": "Connection failed - API server may be down"}
    except requests.exceptions.Timeout:
        return False, {"error": "Request timeout (15s) - API server is slow to respond"}
    except Exception as e:
        return False, {"error": f"Unexpected error: {str(e)}"}


def get_threshold_status(metric: str, value: float) -> Tuple[str, str, str]:
    """Return status, color class, and hint text for a metric value"""
    thresholds = {
        "RSSI": {
            "normal": (-70, float("inf")),
            "warning": (-85, -70),
            "danger": (float("-inf"), -85),
        },
        "SINR": {
            "normal": (15, float("inf")),
            "warning": (10, 15),
            "danger": (float("-inf"), 10),
        },
        "throughput": {
            "normal": (80, float("inf")),
            "warning": (50, 80),
            "danger": (0, 50),
        },
        "latency": {
            "normal": (0, 20),
            "warning": (20, 50),
            "danger": (50, float("inf")),
        },
        "jitter": {"normal": (0, 5), "warning": (5, 15), "danger": (15, float("inf"))},
        "packet_loss": {
            "normal": (0, 1),
            "warning": (1, 3),
            "danger": (3, float("inf")),
        },
    }

    if metric not in thresholds:
        return "normal", "status-normal", "✅ Normal"

    ranges = thresholds[metric]

    for status, (min_val, max_val) in ranges.items():
        if min_val <= value < max_val:
            if status == "normal":
                return status, "status-normal", "✅ Normal"
            elif status == "warning":
                return status, "status-warning", "⚠️ Warning"
            else:
                return status, "status-danger", "🔴 Critical"

    return "normal", "status-normal", "✅ Normal"


def create_confidence_gauge(confidence: float) -> go.Figure:
    """Create a professional animated confidence gauge using Plotly"""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=confidence,
            domain={"x": [0, 1], "y": [0, 1]},
            title={
                "text": "Model Confidence",
                "font": {"color": "#f0f6fc", "size": 18, "family": "Space Grotesk, sans-serif"}
            },
            number={
                "font": {"color": "#ffffff", "size": 32, "family": "Space Grotesk, sans-serif"},
                "suffix": "%"
            },
            gauge={
                "axis": {
                    "range": [None, 100],
                    "tickcolor": "#768390",
                    "tickfont": {"color": "#768390", "size": 12}
                },
                "bar": {"color": "rgba(0,0,0,0)"},
                "bgcolor": "rgba(30, 36, 51, 0.4)",
                "borderwidth": 0,
                "bordercolor": "rgba(0,0,0,0)",
                "steps": [
                    {"range": [0, 50], "color": "rgba(239, 68, 68, 0.3)"},
                    {"range": [50, 75], "color": "rgba(245, 158, 11, 0.3)"},
                    {"range": [75, 100], "color": "rgba(16, 185, 129, 0.3)"},
                ],
                "threshold": {
                    "line": {
                        "color": "#6366f1" if confidence > 50 else "#ef4444",
                        "width": 6
                    },
                    "thickness": 0.85,
                    "value": confidence,
                },
            },
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#f0f6fc", "family": "Inter, sans-serif"},
        height=220,
        margin=dict(l=30, r=30, t=60, b=30),
    )

    return fig


# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []

if "is_predicting" not in st.session_state:
    st.session_state.is_predicting = False

# -----------------------------
# Professional Hero Section
# -----------------------------
st.markdown(
    """
<div class="hero">
    <div class="hero-title">AI Network Intelligence Platform</div>
    <div class="hero-subtitle">
        Predict and prevent 5G network faults with enterprise-grade machine learning. 
        Real-time analysis • Proactive detection • Minimal downtime
    </div>
    <a class="cta-button" href="#input-form">
        <span>⚡</span> Start Analysis
    </a>
</div>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# System Health Dashboard
# -----------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🛡️ System Status & Health Monitoring")

    ok, health = fetch_health(get_api_base())

    if ok and isinstance(health, dict):
        status = health.get("status", "unknown")
        model_loaded = health.get("model_loaded", False)
        scaler_loaded = health.get("scaler_loaded", False)

        # Health metrics grid
        metrics_html = f"""
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value {"text-gradient" if status == "ok" else ""}">{status.upper()}</div>
                <div class="metric-label">API Status</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: {"#3fb950" if model_loaded else "#f85149"}">
                    {"LOADED" if model_loaded else "ERROR"}
                </div>
                <div class="metric-label">ML Model</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: {"#3fb950" if scaler_loaded else "#f85149"}">
                    {"LOADED" if scaler_loaded else "ERROR"}
                </div>
                <div class="metric-label">Data Scaler</div>
            </div>
            <div class="metric-card">
                <div class="metric-value text-gradient">{health.get("expected_feature_count", 0)}</div>
                <div class="metric-label">Features</div>
            </div>
        </div>
        """
        st.markdown(metrics_html, unsafe_allow_html=True)

        # Status badges
        if status == "ok" and model_loaded and scaler_loaded:
            st.markdown(
                '<div class="status-badge badge-success pulse">🟢 System Ready</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="status-badge badge-error">🔴 System Error</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div class="status-badge badge-error">🔴 API Unreachable</div>',
            unsafe_allow_html=True,
        )
        if st.button("🔄 Retry Connection"):
            experimental_rerun()

with col2:
    st.markdown("### ⚙️ Settings")
    with st.form("api_settings"):
        api_base = st.text_input(
            "FastAPI Base URL",
            value=get_api_base(),
            help="Default: http://127.0.0.1:8000",
        )
        if st.form_submit_button("Update API URL"):
            set_api_base(api_base)
            st.success("✅ API URL updated!")
            experimental_rerun()

# -----------------------------
# Input Form Section
# -----------------------------
st.markdown("---")
st.markdown("<div id='input-form'></div>", unsafe_allow_html=True)

# Create tabs for different input methods
input_tab1, input_tab2 = st.tabs(["📊 Manual Input", "📋 JSON Input (Raw Data)"])

with input_tab1:
    st.markdown("### Network Parameters Input")
    
    # Initialize default values for form inputs
    if 'form_values' not in st.session_state:
        st.session_state.form_values = {
            'rssi': -75.0, 'sinr': 18.0, 'throughput': 95.0,
            'latency': 15.0, 'jitter': 3.0, 'packet_loss': 0.5,
            'cpu': 65.0, 'memory': 60.0, 'temperature': 45.0,
            'active_users': 350, 'hour': 14, 'day_of_week': 3,
            'is_peak_hour': 1, 'network_quality_score': 0.75, 'resource_stress': 65.0
        }

with st.form("network_analysis_form"):
    # Primary metrics in two columns
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Signal Quality Metrics")

        rssi = st.number_input(
            "📡 RSSI (dBm)",
            value=st.session_state.form_values['rssi'],
            step=1.0,
            help="Received Signal Strength Indicator\nNormal: -70 to -50 dBm\nWarning: -85 to -70 dBm\nCritical: < -85 dBm",
        )
        rssi_status, rssi_class, rssi_hint = get_threshold_status("RSSI", rssi)
        st.markdown(
            f'<small style="color: var(--text-muted)">{rssi_hint}</small>',
            unsafe_allow_html=True,
        )

        sinr = st.number_input(
            "📶 SINR (dB)",
            value=st.session_state.form_values['sinr'],
            step=0.5,
            help="Signal-to-Interference-plus-Noise Ratio\nNormal: > 15 dB\nWarning: 10-15 dB\nCritical: < 10 dB",
        )
        sinr_status, sinr_class, sinr_hint = get_threshold_status("SINR", sinr)
        st.markdown(
            f'<small style="color: var(--text-muted)">{sinr_hint}</small>',
            unsafe_allow_html=True,
        )

        throughput = st.number_input(
            "🚀 Throughput (Mbps)",
            value=st.session_state.form_values['throughput'],
            step=1.0,
            help="Network data throughput\nNormal: > 80 Mbps\nWarning: 50-80 Mbps\nCritical: < 50 Mbps",
        )
        throughput_status, throughput_class, throughput_hint = get_threshold_status(
            "throughput", throughput
        )
        st.markdown(
            f'<small style="color: var(--text-muted)">{throughput_hint}</small>',
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown("#### Performance Metrics")

        latency = st.number_input(
            "⏱️ Latency (ms)",
            value=st.session_state.form_values['latency'],
            step=1.0,
            help="Network response time\nNormal: < 20 ms\nWarning: 20-50 ms\nCritical: > 50 ms",
        )
        latency_status, latency_class, latency_hint = get_threshold_status(
            "latency", latency
        )
        st.markdown(
            f'<small style="color: var(--text-muted)">{latency_hint}</small>',
            unsafe_allow_html=True,
        )

        jitter = st.number_input(
            "📊 Jitter (ms)",
            value=st.session_state.form_values['jitter'],
            step=0.5,
            help="Packet delay variation\nNormal: < 5 ms\nWarning: 5-15 ms\nCritical: > 15 ms",
        )
        jitter_status, jitter_class, jitter_hint = get_threshold_status(
            "jitter", jitter
        )
        st.markdown(
            f'<small style="color: var(--text-muted)">{jitter_hint}</small>',
            unsafe_allow_html=True,
        )

        packet_loss = st.number_input(
            "📉 Packet Loss (%)",
            value=st.session_state.form_values['packet_loss'],
            step=0.1,
            help="Percentage of lost packets\nNormal: < 1%\nWarning: 1-3%\nCritical: > 3%",
        )
        loss_status, loss_class, loss_hint = get_threshold_status(
            "packet_loss", packet_loss
        )
        st.markdown(
            f'<small style="color: var(--text-muted)">{loss_hint}</small>',
            unsafe_allow_html=True,
        )

    # Advanced settings in expandable section
    with st.expander("🔧 Advanced Settings (Optional)", expanded=False):
        col3, col4, col5 = st.columns(3)

        with col3:
            st.markdown("**Infrastructure**")
            cpu = st.number_input(
                "💻 CPU Usage (%)", value=st.session_state.form_values['cpu'], min_value=0.0, max_value=100.0, step=1.0
            )
            memory = st.number_input(
                "🧠 Memory Usage (%)",
                value=st.session_state.form_values['memory'],
                min_value=0.0,
                max_value=100.0,
                step=1.0,
            )
            temperature = st.number_input("🌡️ Temperature (°C)", value=st.session_state.form_values['temperature'], step=0.5)

        with col4:
            st.markdown("**Network Load**")
            active_users = st.number_input(
                "👥 Active Users", value=st.session_state.form_values['active_users'], min_value=0, step=1
            )
            hour = st.number_input(
                "🕐 Hour (0-23)", value=st.session_state.form_values['hour'], min_value=0, max_value=23, step=1
            )
            day_of_week = st.number_input(
                "📅 Day of Week (0-6)", value=st.session_state.form_values['day_of_week'], min_value=0, max_value=6, step=1
            )

        with col5:
            st.markdown("**Quality Metrics**")
            is_peak_hour = st.selectbox("⏰ Peak Hour", options=[0, 1], index=st.session_state.form_values['is_peak_hour'])
            network_quality_score = st.number_input(
                "📈 Network Quality",
                value=st.session_state.form_values['network_quality_score'],
                min_value=0.0,
                max_value=1.0,
                step=0.01,
            )
            resource_stress = st.number_input(
                "⚡ Resource Stress",
                value=st.session_state.form_values['resource_stress'],
                min_value=0.0,
                max_value=100.0,
                step=1.0,
            )

    # Prediction button with enhanced styling
    st.markdown("<br>", unsafe_allow_html=True)
    predict_button = st.form_submit_button(
        "🚀 Analyze Network Health", 
        use_container_width=True,
        disabled=st.session_state.is_predicting
    )

    # Show loading state if predicting
    if st.session_state.is_predicting:
        st.info("🔄 Prediction in progress...")

# Update session state with current form values and process prediction
if predict_button:
    # Update session state with current form values
    st.session_state.form_values.update({
        'rssi': rssi, 'sinr': sinr, 'throughput': throughput,
        'latency': latency, 'jitter': jitter, 'packet_loss': packet_loss,
        'cpu': cpu, 'memory': memory, 'temperature': temperature,
        'active_users': active_users, 'hour': hour, 'day_of_week': day_of_week,
        'is_peak_hour': is_peak_hour, 'network_quality_score': network_quality_score, 'resource_stress': resource_stress
    })
    
    # Prepare payload for API call
    payload = {
        "RSSI": rssi,
        "SINR": sinr,
        "throughput": throughput,
        "latency": latency,
        "jitter": jitter,
        "packet_loss": packet_loss,
        "cpu_usage_percent": cpu,
        "memory_usage_percent": memory,
        "active_users": active_users,
        "temperature_celsius": temperature,
        "hour": hour,
        "day_of_week": day_of_week,
        "is_peak_hour": float(is_peak_hour),
        "network_quality_score": network_quality_score,
        "resource_stress": resource_stress,
    }
    
    # Set predicting state
    st.session_state.is_predicting = True

with input_tab2:
    st.markdown("### Raw JSON Input (Pre-scaled Data)")
    st.info("💡 **Note:** This accepts pre-scaled/normalized data from your training pipeline. Paste JSON directly from your dataset.")
    
    # JSON input text area
    json_input = st.text_area(
        "Paste JSON Data",
        value='',
        height=300,
        placeholder='''{
  "RSSI": 0.842511637,
  "SINR": 0.953234587,
  "throughput": 1.126543212,
  "latency": -0.748905324,
  "jitter": -0.684293455,
  "packet_loss": -0.833224211,
  "cpu_usage_percent": -0.342178954,
  "memory_usage_percent": -0.417293847,
  "active_users": -0.823489321,
  "temperature_celsius": -0.512839478,
  "hour": 0.218374662,
  "day_of_week": -0.478392184,
  "is_peak_hour": -0.864923712,
  "network_quality_score": 1.245892431,
  "resource_stress": -0.986573221,
  "base_station_id_encoded": 10,
  "cell_id_encoded": 214
}''',
        help="Paste JSON object with network parameters"
    )
    
    json_predict_button = st.button(
        "🚀 Predict from JSON",
        use_container_width=True,
        type="primary"
    )
    
    if json_predict_button:
        try:
            # Parse JSON input
            json_data = json.loads(json_input)
            
            # Prepare payload (use as-is since it's already formatted)
            payload = json_data
            
            # Set predicting state
            st.session_state.is_predicting = True
            
            # Store in form values for display (convert back to approximate raw values for display)
            st.session_state.form_values.update({
                'rssi': -75.0,  # Placeholder - actual scaled value used
                'sinr': 18.0,
                'throughput': 95.0,
                'latency': 15.0,
                'jitter': 3.0,
                'packet_loss': 0.5,
                'cpu': 65.0,
                'memory': 60.0,
                'temperature': 45.0,
                'active_users': 350,
                'hour': 14,
                'day_of_week': 3,
                'is_peak_hour': 1,
                'network_quality_score': 0.75,
                'resource_stress': 65.0
            })
            
        except json.JSONDecodeError as e:
            st.error(f"❌ Invalid JSON format: {str(e)}")
            st.info("💡 Make sure your JSON is properly formatted with double quotes and correct syntax.")
        except Exception as e:
            st.error(f"❌ Error processing JSON: {str(e)}")

# -----------------------------
# Prediction Results
# -----------------------------
if st.session_state.is_predicting and 'payload' in locals():
    # Loading animation
    with st.spinner("🔍 Analyzing network signals..."):
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)

        ok, result = post_predict(get_api_base(), payload)
        progress_bar.empty()
        time.sleep(0.2)
        
        # Reset predicting state
        st.session_state.is_predicting = False

    if ok and isinstance(result, dict):
        prediction = result.get("prediction", "Unknown")
        probability_faulty = result.get("probability_faulty", 0)
        confidence_percent = result.get("confidence_percent", 0)

        # Add to history
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_item = {
            "timestamp": timestamp,
            "prediction": prediction,
            "confidence": confidence_percent,
            "probability_faulty": probability_faulty,
            "payload": payload,
        }

        if len(st.session_state.history) >= 10:
            st.session_state.history.pop()
        st.session_state.history.insert(0, history_item)

        # Result visualization
        st.markdown("---")
        st.markdown("### 🎯 Analysis Results")

        # Main result card
        result_class = "result-normal" if prediction == "Normal" else "result-faulty"
        prediction_class = (
            "prediction-normal" if prediction == "Normal" else "prediction-faulty"
        )

        result_html = f"""
        <div class="result-card {result_class}">
            <div class="result-prediction {prediction_class}">
                {"✅ Network Normal" if prediction == "Normal" else "⚠️ Network Fault Detected"}
            </div>
            <div style="color: var(--text-secondary); font-size: 16px; margin-bottom: 24px;">
                Prediction: <strong>{prediction}</strong>
            </div>
        </div>
        """
        st.markdown(result_html, unsafe_allow_html=True)

        # Confidence and probability visualization
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🎯 Model Confidence")
            if confidence_percent:
                # Create Plotly gauge
                fig = create_confidence_gauge(confidence_percent)
                st.plotly_chart(
                    fig, use_container_width=True, config={"displayModeBar": False}
                )
            else:
                st.info("Confidence data not available")

        with col2:
            st.markdown("#### 📊 Fault Probability")
            if probability_faulty is not None:
                prob_percent = probability_faulty * 100

                # Progress bar with animation
                progress_html = f"""
                <div class="progress-container">
                    <div class="progress-label">Fault Likelihood: {prob_percent:.1f}%</div>
                    <div class="progress-bar-container">
                        <div class="progress-bar" style="width: {prob_percent}%;"></div>
                    </div>
                </div>
                """
                st.markdown(progress_html, unsafe_allow_html=True)

                # Risk assessment
                if prob_percent < 25:
                    st.success("🟢 Low Risk - Network operating normally")
                elif prob_percent < 75:
                    st.warning("🟡 Medium Risk - Monitor closely")
                else:
                    st.error("🔴 High Risk - Immediate attention required")
            else:
                st.info("Probability data not available")

        # Detailed metrics breakdown
        st.markdown("#### 📈 Input Metrics Analysis")

        # Get current values from session state
        current_values = st.session_state.form_values
        
        metrics_analysis = [
            ("RSSI", current_values['rssi'], "dBm", get_threshold_status("RSSI", current_values['rssi'])[2]),
            ("SINR", current_values['sinr'], "dB", get_threshold_status("SINR", current_values['sinr'])[2]),
            ("Throughput", current_values['throughput'], "Mbps", get_threshold_status("throughput", current_values['throughput'])[2]),
            ("Latency", current_values['latency'], "ms", get_threshold_status("latency", current_values['latency'])[2]),
            ("Jitter", current_values['jitter'], "ms", get_threshold_status("jitter", current_values['jitter'])[2]),
            ("Packet Loss", current_values['packet_loss'], "%", get_threshold_status("packet_loss", current_values['packet_loss'])[2]),
        ]

        cols = st.columns(3)
        for i, (metric, value, unit, hint) in enumerate(metrics_analysis):
            with cols[i % 3]:
                status_color = (
                    "#3fb950"
                    if hint.startswith("✅")
                    else "#d29922"
                    if hint.startswith("⚠️")
                    else "#f85149"
                )
                st.markdown(
                    f"""
                <div style="
                    background: var(--glass);
                    border: 1px solid var(--border);
                    border-radius: 12px;
                    padding: 16px;
                    margin-bottom: 16px;
                    text-align: center;
                ">
                    <div style="font-size: 20px; font-weight: 700; color: {status_color}; margin-bottom: 4px;">
                        {value} {unit}
                    </div>
                    <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 8px;">
                        {metric}
                    </div>
                    <div style="font-size: 11px; color: var(--text-secondary);">
                        {hint}
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

        # Recommendations
        st.markdown("#### 💡 Recommendations")
        recommendations = []
        
        # Get current values from session state
        current_values = st.session_state.form_values

        if current_values['rssi'] < -85:
            recommendations.append("🔧 Check antenna positioning and signal strength")
        if current_values['sinr'] < 10:
            recommendations.append("📡 Investigate interference sources")
        if current_values['throughput'] < 50:
            recommendations.append("🚀 Optimize network bandwidth allocation")
        if current_values['latency'] > 50:
            recommendations.append("⚡ Review network routing and congestion")
        if current_values['jitter'] > 15:
            recommendations.append("📊 Stabilize network traffic patterns")
        if current_values['packet_loss'] > 3:
            recommendations.append("🔄 Check for network hardware issues")

        if not recommendations:
            recommendations.append("✅ Network parameters are within normal ranges")

        for rec in recommendations:
            st.markdown(f"• {rec}")

    else:
        st.error("❌ Prediction failed")
        if isinstance(result, dict):
            error_msg = result.get("error", "Unknown error occurred")
            st.error(f"Error: {error_msg}")
            if "timeout" in error_msg.lower():
                st.info("💡 Tip: The API might be overloaded. Try again in a few moments.")
            elif "connection" in error_msg.lower():
                st.info("💡 Tip: Check if the backend server is running and accessible.")
        else:
            st.code(str(result))

# -----------------------------
# Prediction History
# -----------------------------
if st.session_state.history:
    st.markdown("---")
    st.markdown("### 📚 Prediction History")

    # History timeline container start
    st.markdown('<div class="history-timeline">', unsafe_allow_html=True)

    for i, item in enumerate(st.session_state.history[:5]):  # Show last 5
        pred = item.get("prediction", "Unknown")
        conf = item.get("confidence", 0)
        timestamp = item.get("timestamp", "Unknown")
        prob = item.get("probability_faulty", 0) * 100

        status_icon = "✅" if pred == "Normal" else "⚠️"
        status_color = "var(--success)" if pred == "Normal" else "var(--danger)"

        # Render each history item separately
        history_item_html = f"""
        <div class="history-item">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 600; color: {status_color};">
                    {status_icon} {pred}
                </span>
                <span style="font-size: 12px; color: var(--text-muted);">
                    {timestamp}
                </span>
            </div>
            <div style="display: flex; gap: 16px; font-size: 12px; color: var(--text-secondary);">
                <span>Confidence: {conf:.1f}%</span>
                <span>Risk: {prob:.1f}%</span>
            </div>
        </div>
        """
        st.markdown(history_item_html, unsafe_allow_html=True)

    # Close timeline container
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        experimental_rerun()

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown(
    """
<div style="text-align: center; color: var(--text-muted); font-size: 14px; padding: 20px;">
    <p>🚀 Powered by <strong>FastAPI</strong> + <strong>AI ML Models</strong> + <strong>Streamlit</strong></p>
    <p>Real-time 5G Network Fault Prediction System</p>
</div>
""",
    unsafe_allow_html=True,
)
