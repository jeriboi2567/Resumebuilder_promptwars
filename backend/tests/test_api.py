import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_api_list_candidates():
    response = client.get("/api/candidates")
    assert response.status_code == 200
    candidates = response.json()
    assert len(candidates) == 3
    assert candidates[0]["name"] == "Alex Rivera"
    assert candidates[1]["name"] == "Jordan Lee"
    assert candidates[2]["name"] == "Taylor Morgan"

def test_api_get_candidate_detail():
    response = client.get("/api/candidates/cand_1")
    assert response.status_code == 200
    data = response.json()
    assert data["candidate_id"] == "cand_1"
    assert "ALEX RIVERA" in data["resume_text"].upper()
    assert "Nexus Cloud" in data["resume_text"]

def test_api_evaluate_candidates_end_to_end():
    # Evaluate Candidate 1 (Alex Rivera)
    r1 = client.post("/api/evaluate", json={"candidate_id": "cand_1"})
    assert r1.status_code == 200
    res1 = r1.json()
    assert res1["profile"]["candidate_name"] == "Alex Rivera"
    assert res1["final_decision"]["recommendation"] == "Strong Hire"
    assert res1["final_decision"]["confidence"] >= 0.9

    # Evaluate Candidate 2 (Jordan Lee)
    r2 = client.post("/api/evaluate", json={"candidate_id": "cand_2"})
    assert r2.status_code == 200
    res2 = r2.json()
    assert res2["profile"]["candidate_name"] == "Jordan Lee"
    assert res2["final_decision"]["recommendation"] == "No Hire"
    assert len(res2["independent_opinions"]["opinions"]["Skeptic Agent"]["supporting_quotes"]) >= 1

    # Evaluate Candidate 3 (Taylor Morgan)
    r3 = client.post("/api/evaluate", json={"candidate_id": "cand_3"})
    assert r3.status_code == 200
    res3 = r3.json()
    assert res3["profile"]["candidate_name"] == "Taylor Morgan"
    assert res3["final_decision"]["recommendation"] == "Hire"
    assert len(res3["final_decision"]["unresolved_disagreements"]) >= 1

def test_api_list_runs():
    response = client.get("/api/runs")
    assert response.status_code == 200
    runs = response.json()
    assert len(runs) >= 3
