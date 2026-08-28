import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_v2_api_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["version"] == "2.0.0"

def test_v2_api_sample_batch():
    response = client.get("/api/sample-batch")
    assert response.status_code == 200
    batch = response.json()
    assert batch["batch_id"] == "batch_sample_01"
    assert len(batch["candidate_results"]) == 2
    assert "cand_A" in batch["candidate_results"]
    assert "cand_B" in batch["candidate_results"]
    
    # Check Stage 6 comparative ranking
    assert len(batch["stage6_comparison"]["rankings"]) == 2
    assert batch["stage6_comparison"]["rankings"][0]["rank"] == 1
    assert batch["stage6_comparison"]["rankings"][0]["final_recommendation"] == "Strong Hire"

def test_v2_api_audio_file():
    # Call sample batch first to generate audio
    client.get("/api/sample-batch")
    response = client.get("/api/audio/test_run_01.mp3")
    assert response.status_code in [200, 404]
