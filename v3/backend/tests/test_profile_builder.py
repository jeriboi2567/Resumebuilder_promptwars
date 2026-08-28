import pytest
from backend.profile_builder.builder import CandidateProfileBuilderV2, verify_quote_in_source

def test_profile_builder_full_extraction():
    resume = """
    ALEX RIVERA
    Senior Backend Architect
    Experience:
    - Principal Engineer — Datastream Systems (2020-Present): Built distributed Kafka pipelines handling 100K msg/sec using Go and PostgreSQL.
    Skills: Go, Kafka, PostgreSQL, Docker, Kubernetes, Microservices
    """
    transcript = """
    Interview Transcript - Candidate: Alex Rivera
    Q1: Tell us about your Kafka pipeline architecture.
    A1: We used Go goroutines to process Kafka event streams into PostgreSQL.
    Q2: Did you use LangChain in production?
    A2: No, I haven't used LangChain in production.
    """

    profile = CandidateProfileBuilderV2.build_profile("cand_alex", resume, transcript)

    assert profile.candidate_id == "cand_alex"
    assert profile.candidate_name == "Alex Rivera"
    assert profile.seniority_level == "Senior"
    assert len(profile.skills) >= 2
    assert any(s.skill_name == "Kafka" for s in profile.skills)
    assert len(profile.quote_bank) >= 2

def test_verify_quote_in_source_accuracy():
    resume = "Alex Rivera built Kafka pipelines using Go."
    transcript = "Interview Transcript - Candidate: Alex Rivera. We used Go goroutines."

    is_valid, note = verify_quote_in_source("built Kafka pipelines using Go", resume, transcript)
    assert is_valid is True
    assert "Verified" in note

    is_invalid, invalid_note = verify_quote_in_source("fabricated quote never spoken", resume, transcript)
    assert is_invalid is False
    assert "not found" in invalid_note.lower()
