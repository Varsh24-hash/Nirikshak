import json
import pytest
from fastapi.testclient import TestClient
import os
import sys

# Add project root to sys.path so we can import src
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.api.main import app, orchestrate_verification
from src.schemas.input_schemas import FullVerificationRequest

client = TestClient(app)

def load_fixture(name: str):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, "fixtures", name)
    with open(path, "r") as f:
        return json.load(f)

def test_integration_clean_case():
    payload = load_fixture("clean/full_request.json")
    response = client.post("/verify", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["verification_status"] == "VERIFIED"
    assert data["risk_level"] == "LOW"
    assert data["inspection_priority_rank"] == 100
    assert len(data["contributing_factors"]) == 0

def test_integration_suspicious_case():
    payload = load_fixture("suspicious/full_request.json")
    response = client.post("/verify", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["verification_status"] == "DISPUTED"
    assert data["risk_level"] == "CRITICAL"
    assert data["inspection_priority_rank"] == 1
    assert len(data["contributing_factors"]) > 0

def test_orchestrate_verification_direct_call():
    payload = load_fixture("clean/full_request.json")
    request_obj = FullVerificationRequest(**payload)
    output = orchestrate_verification(request_obj)
    
    assert output.verification_status == "VERIFIED"
    assert output.risk_level == "LOW"
