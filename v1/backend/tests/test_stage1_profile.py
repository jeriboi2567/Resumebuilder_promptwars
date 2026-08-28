import pytest
from backend.profile_builder.builder import CandidateProfileBuilder, verify_quote_in_source

def test_verify_quote_in_source():
    resume = "ALEX RIVERA\nLed a cross-functional team of 8 developers."
    transcript = "[00:01:30] Alex Rivera: The main bottleneck was unindexed JSONB queries."

    # Test verbatim resume quote
    valid, note = verify_quote_in_source("Led a cross-functional team", resume, transcript)
    assert valid is True
    assert "resume" in note.lower()

    # Test verbatim transcript quote
    valid, note = verify_quote_in_source("unindexed JSONB queries", resume, transcript)
    assert valid is True
    assert "transcript" in note.lower()

    # Test non-existent quote
    valid, note = verify_quote_in_source("invented fake statement that does not exist", resume, transcript)
    assert valid is False

def test_candidate_profile_builder():
    resume = (
        "ALEX RIVERA\n"
        "Lead Full-Stack Engineer\n"
        "TECHNICAL SKILLS\n"
        "- Languages: TypeScript, Python, Go\n"
        "PROFESSIONAL EXPERIENCE\n"
        "Lead Engineer | Nexus Cloud | Jan 2022 – Present\n"
        "- Improved P99 endpoint latency by 40%\n"
    )
    transcript = "[00:02:15] Interviewer: How did you lower latency?\n[00:02:30] Alex Rivera: We introduced a Redis write-through cache."

    profile = CandidateProfileBuilder.build_profile("cand_test", resume, transcript)

    assert profile.candidate_name == "Alex Rivera"
    assert profile.seniority_level == "Lead / Principal"
    assert len(profile.skills) >= 3
    assert len(profile.claims) >= 1
    assert len(profile.quote_bank) >= 1
    assert profile.quote_bank[0].location == "[00:02:30]"
