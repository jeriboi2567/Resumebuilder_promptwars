import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_v3_api_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["version"] == "3.0.0"

def test_v3_api_sample_batch():
    response = client.get("/api/sample-batch")
    assert response.status_code == 200
    batch = response.json()
    assert "candidate_results" in batch
    assert len(batch["candidate_results"]) == 2
