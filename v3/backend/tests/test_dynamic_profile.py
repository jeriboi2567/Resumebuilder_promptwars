import pytest
from backend.profile_builder.builder import CandidateProfileBuilderV2

def test_dynamic_profile_extraction():
    resume = "CAMERON MORGAN\nSenior Backend Engineer\n- Developed Go microservices and Kafka event stream pipelines."
    transcript = "Interview Transcript - Candidate: Cameron Morgan\nQ1: Walk me through your Go backend microservice architecture.\nA1: We used Go goroutines and Kafka."

    profile = CandidateProfileBuilderV2.build_profile("cand_test_01", resume, transcript)

    assert profile.candidate_name == "Cameron Morgan"
    assert profile.seniority_level == "Senior"
    assert any(s.skill_name == "Go" or s.skill_name == "Kafka" for s in profile.skills)
    assert len(profile.quote_bank) >= 1
