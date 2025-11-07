#!/usr/bin/env python3
"""Debug script to test model loading."""

import joblib
import pickle
from pathlib import Path

root = Path(__file__).resolve().parent
model_path = root / "ML_MODEL" / "fault_prediction_model.pkl"
scaler_path = root / "ML_MODEL" / "scaler.pkl"
feature_path = root / "feature_list.pkl"

print("Testing model loading...")
print(f"Model path: {model_path}")
print(f"Exists: {model_path.exists()}")

try:
    model = joblib.load(model_path)
    print("✅ Model loaded successfully!")
    print(f"Model type: {type(model)}")
    if hasattr(model, 'feature_names_in_'):
        print(f"Feature names: {model.feature_names_in_}")
except Exception as e:
    print(f"❌ Model loading failed: {e}")

print("\nTesting scaler loading...")
print(f"Scaler path: {scaler_path}")
print(f"Exists: {scaler_path.exists()}")

try:
    scaler = joblib.load(scaler_path)
    print("✅ Scaler loaded successfully!")
    print(f"Scaler type: {type(scaler)}")
    if hasattr(scaler, 'n_features_in_'):
        print(f"Number of features: {scaler.n_features_in_}")
except Exception as e:
    print(f"❌ Scaler loading failed: {e}")

print("\nTesting feature list loading...")
print(f"Feature list path: {feature_path}")
print(f"Exists: {feature_path.exists()}")

try:
    features = joblib.load(feature_path)
    print("✅ Feature list loaded successfully!")
    print(f"Number of features: {len(features)}")
    print(f"Features: {features}")
except Exception as e:
    print(f"❌ Feature list loading failed: {e}")