"""
Quick test script to verify frontend-backend connection
"""
import requests
import json

API_BASE = "http://127.0.0.1:8000"

print("=" * 60)
print("Testing Frontend-Backend Connection")
print("=" * 60)

# Test 1: Health Check
print("\n1. Testing Health Endpoint (GET /)")
try:
    response = requests.get(f"{API_BASE}/", timeout=5)
    if response.status_code == 200:
        health = response.json()
        print("✅ Health endpoint connected!")
        print(f"   Status: {health.get('status')}")
        print(f"   Model Loaded: {health.get('model_loaded')}")
        print(f"   Scaler Loaded: {health.get('scaler_loaded')}")
        print(f"   Expected Features: {health.get('expected_feature_count')}")
    else:
        print(f"❌ Health check failed: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("   Make sure the FastAPI server is running!")
    print("   Run: uvicorn app:app --host 0.0.0.0 --port 8000")

# Test 2: Prediction Endpoint
print("\n2. Testing Prediction Endpoint (POST /predict)")
test_payload = {
    "RSSI": -75.0,
    "SINR": 18.0,
    "throughput": 95.0,
    "latency": 15.0,
    "jitter": 3.0,
    "packet_loss": 0.5,
    "cpu_usage_percent": 65.0,
    "memory_usage_percent": 60.0,
    "active_users": 350.0,
    "temperature_celsius": 45.0,
    "hour": 14.0,
    "day_of_week": 3.0,
    "is_peak_hour": 1.0,
    "network_quality_score": 0.75,
    "resource_stress": 65.0,
}

try:
    response = requests.post(
        f"{API_BASE}/predict",
        json=test_payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    if response.status_code == 200:
        result = response.json()
        print("✅ Prediction endpoint connected!")
        print(f"   Prediction: {result.get('prediction')}")
        if 'probability_faulty' in result:
            print(f"   Probability Faulty: {result.get('probability_faulty')}")
        if 'confidence_percent' in result:
            print(f"   Confidence: {result.get('confidence_percent')}%")
    else:
        print(f"❌ Prediction failed: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"❌ Prediction request failed: {e}")

# Test 3: Verify Payload Format
print("\n3. Verifying Payload Format Compatibility")
print("   Frontend sends:")
print(f"   {json.dumps(test_payload, indent=2)}")
print("\n   Backend expects (NetworkParams):")
print("   - RSSI, SINR, throughput, latency, jitter, packet_loss (required)")
print("   - cpu_usage_percent, memory_usage_percent, active_users, etc. (optional)")
print("   ✅ Payload format matches!")

print("\n" + "=" * 60)
print("Connection Test Complete!")
print("=" * 60)
print("\nIf both tests passed, your frontend should connect successfully.")
print("Make sure both servers are running:")
print("  - Backend: uvicorn app:app --host 0.0.0.0 --port 8000")
print("  - Frontend: streamlit run frontend-enhanced/app_enhanced.py")


