"""
AI-Powered Fault Prediction API

How to run (from the project root):
  uvicorn app:app --host 0.0.0.0 --port 8000 --reload

Then open the docs at:
  http://127.0.0.1:8000/docs
"""

from pathlib import Path
from typing import Literal, Optional

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd


app = FastAPI(title="AI-Powered Fault Prediction in 5G Testbed", version="1.0.0")

# Enable CORS for all origins (adjust as needed for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class NetworkParams(BaseModel):
    RSSI: float
    SINR: float
    throughput: float
    latency: float
    jitter: float
    packet_loss: float
    # Optional fields used by the trained model (if present)
    cpu_usage_percent: Optional[float] = None
    memory_usage_percent: Optional[float] = None
    active_users: Optional[float] = None
    temperature_celsius: Optional[float] = None
    hour: Optional[float] = None
    day_of_week: Optional[float] = None
    is_peak_hour: Optional[float] = None
    network_quality_score: Optional[float] = None
    resource_stress: Optional[float] = None


@app.on_event("startup")
def load_artifacts() -> None:
    """Load the trained model and scaler into app.state on startup."""
    root = Path(__file__).resolve().parent
    model_path = root / "ML_MODEL" / "fault_prediction_model.pkl"
    scaler_path = root / "ML_MODEL" / "scaler.pkl"

    try:
        app.state.model = joblib.load(model_path)
    except Exception as e:
        # Store error so we can surface a helpful message later
        app.state.model = None
        app.state.model_load_error = RuntimeError(f"Failed to load model from {model_path}: {e}")

    try:
        app.state.scaler = joblib.load(scaler_path)
    except Exception as e:
        app.state.scaler = None
        app.state.scaler_load_error = RuntimeError(f"Failed to load scaler from {scaler_path}: {e}")

    # Determine expected feature names
    expected = None
    model = getattr(app.state, "model", None)
    if model is not None and hasattr(model, "feature_names_in_"):
        try:
            expected = list(model.feature_names_in_)
        except Exception:
            expected = None
    if expected is None:
        # Try project root
        try:
            feat_path = root / "feature_list.pkl"
            expected = joblib.load(feat_path)
        except Exception:
            expected = None
        # Try ML_MODEL folder as fallback
        if expected is None:
            try:
                feat_path2 = root / "ML_MODEL" / "feature_list.pkl"
                expected = joblib.load(feat_path2)
            except Exception:
                expected = None
    app.state.expected_features = expected


@app.get("/")
def health() -> dict:
    """Basic health endpoint that also reports artifact load status."""
    status = {
        "model_loaded": getattr(app.state, "model", None) is not None,
        "scaler_loaded": getattr(app.state, "scaler", None) is not None,
        "expected_feature_count": len(getattr(app.state, "expected_features", []) or []),
        "scaler_feature_count": getattr(getattr(app.state, "scaler", None), "n_features_in_", None),
        "scaler_compatible": (
            (getattr(app.state, "expected_features", None) is not None)
            and (getattr(getattr(app.state, "scaler", None), "n_features_in_", None) 
                 == len(getattr(app.state, "expected_features", []) or []))
        ),
    }
    return {"status": "ok", **status}


@app.post("/predict")
def predict(params: NetworkParams) -> dict:
    """
    Accepts network parameters and returns the prediction label: "Normal" or "Faulty".
    """
    model = getattr(app.state, "model", None)
    scaler = getattr(app.state, "scaler", None)
    expected_features = getattr(app.state, "expected_features", None)

    if model is None:
        err = getattr(app.state, "model_load_error", None)
        detail = str(err) if err else "Model is not loaded."
        raise HTTPException(status_code=500, detail=detail)

    if scaler is None:
        err = getattr(app.state, "scaler_load_error", None)
        detail = str(err) if err else "Scaler is not loaded."
        raise HTTPException(status_code=500, detail=detail)

    # Map API fields to training feature names
    features = {
        "rssi_dbm": params.RSSI,
        "sinr_db": params.SINR,
        "throughput_mbps": params.throughput,
        "latency_ms": params.latency,
        "jitter_ms": params.jitter,
        "packet_loss_percent": params.packet_loss,
    }

    # Optional direct mappings if provided
    optional_map = {
        "cpu_usage_percent": params.cpu_usage_percent,
        "memory_usage_percent": params.memory_usage_percent,
        "active_users": params.active_users,
        "temperature_celsius": params.temperature_celsius,
        "hour": params.hour,
        "day_of_week": params.day_of_week,
        "is_peak_hour": params.is_peak_hour,
        "network_quality_score": params.network_quality_score,
        "resource_stress": params.resource_stress,
    }
    for k, v in optional_map.items():
        if v is not None:
            features[k] = v

    # Engineered features (compute when possible)
    try:
        if "efficiency_score" not in features:
            features["efficiency_score"] = features["throughput_mbps"] / (features["latency_ms"] + 1)
        if "signal_ratio" not in features:
            features["signal_ratio"] = features["sinr_db"] / (abs(features["rssi_dbm"]) + 1)
        if "network_load_factor" not in features:
            cpu = features.get("cpu_usage_percent")
            users = features.get("active_users")
            if cpu is not None and users is not None:
                features["network_load_factor"] = users / (cpu + 1)
    except Exception:
        # If engineered feature computation fails, we'll fill defaults below
        pass

    # Build DataFrame and align columns to expected features if available
    input_df = pd.DataFrame([features])
    if expected_features is not None and len(expected_features) > 0:
        for col in expected_features:
            if col not in input_df.columns:
                input_df[col] = 0.0
        input_df = input_df[expected_features]
    else:
        # Fallback: use whatever features we have in deterministic order
        input_df = input_df.reindex(sorted(input_df.columns), axis=1)

    # Decide whether to use scaler based on compatibility
    n_expected = len(expected_features or [])
    scaler_n = getattr(scaler, "n_features_in_", None)
    use_scaler = scaler is not None and scaler_n is not None and scaler_n == n_expected

    try:
        if use_scaler:
            X_in = scaler.transform(input_df.values)
        else:
            X_in = input_df.values
        y_pred = model.predict(X_in)

        prob_faulty = None
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X_in)
            if proba is not None and proba.shape[1] >= 2:
                prob_faulty = float(proba[0][1])
        elif hasattr(model, "decision_function"):
            df = model.decision_function(X_in)
            try:
                from math import exp
                s = 1.0 / (1.0 + exp(-float(df[0])))
                prob_faulty = s
            except Exception:
                prob_faulty = None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {e}")

    label: Literal["Normal", "Faulty"] = "Faulty" if int(y_pred[0]) == 1 else "Normal"
    if prob_faulty is not None:
        confidence = prob_faulty if label == "Faulty" else (1.0 - prob_faulty)
        return {
            "prediction": label,
            "probability_faulty": round(prob_faulty, 6),
            "confidence_percent": round(confidence * 100.0, 2)
        }
    else:
        return {
            "prediction": label
        }


if __name__ == "__main__":
    # Optional: run with `python app.py` (uses the same command as above programmatically)
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
