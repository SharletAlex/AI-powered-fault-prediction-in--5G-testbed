import joblib
from pathlib import Path
root = Path(__file__).resolve().parent
model_path = root / 'ML_MODEL' / 'fault_prediction_model.pkl'
scaler_path = root / 'ML_MODEL' / 'scaler.pkl'
print('Model path exists:', model_path.exists(), model_path)
print('Scaler path exists:', scaler_path.exists(), scaler_path)
try:
    m = joblib.load(model_path)
    print('MODEL_OK:', type(m).__name__)
except Exception as e:
    print('MODEL_ERR:', repr(e))
try:
    s = joblib.load(scaler_path)
    print('SCALER_OK:', type(s).__name__)
except Exception as e:
    print('SCALER_ERR:', repr(e))
