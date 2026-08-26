from fastapi.testclient import TestClient
import json
import sys
import os

# Add the project root to sys.path so it can find src.api.main
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from src.api.main import app
except ImportError as e:
    print(f"Failed to import app: {e}")
    sys.exit(1)

client = TestClient(app)

def test_payload(filepath):
    print(f"\nTesting payload: {filepath}")
    with open(filepath, 'r') as f:
        payload = json.load(f)
    
    response = client.post("/verify", json=payload)
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
    
if __name__ == "__main__":
    clean_path = os.path.join("fixtures", "clean", "full_request.json")
    suspicious_path = os.path.join("fixtures", "suspicious", "full_request.json")
    
    test_payload(clean_path)
    test_payload(suspicious_path)
