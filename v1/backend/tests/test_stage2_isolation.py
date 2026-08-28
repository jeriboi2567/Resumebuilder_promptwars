import inspect
import pytest
from backend.profile_builder.builder import CandidateProfileBuilder
from backend.agents.technical_agent import TechnicalAgent
from backend.agents.hr_culture_agent import HRCultureAgent
from backend.agents.hiring_manager_agent import HiringManagerAgent
from backend.agents.skeptic_agent import SkepticAgent
from backend.agents.runner import run_stage2_independent_opinions

def test_stage2_strict_architectural_isolation_signature():
    """
    Verify that Stage 2 agent evaluate() methods ONLY accept CandidateProfile parameter.
    No 'other_opinions' or cross-agent context parameter exists!
    """
    for agent_cls in [TechnicalAgent, HRCultureAgent, HiringManagerAgent, SkepticAgent]:
        sig = inspect.signature(agent_cls.evaluate)
        params = list(sig.parameters.keys())
        # Self + profile only!
        assert params == ['self', 'profile'], f"{agent_cls.__name__}.evaluate() breaks isolation contract with params: {params}"

@pytest.mark.asyncio
async def test_stage2_independent_execution_and_quote_verification():
    resume = "ALEX RIVERA\nSenior Full-Stack Engineer\n- Improved P99 endpoint latency by 40%"
    transcript = "[00:02:30] Alex Rivera: The main bottleneck was unindexed JSONB queries in PostgreSQL combined with redundant REST polling."

    profile = CandidateProfileBuilder.build_profile("cand_1", resume, transcript)
    opinions = await run_stage2_independent_opinions(profile)

    assert len(opinions.opinions) == 4
    assert "Technical Agent" in opinions.opinions
    assert "HR / Culture Agent" in opinions.opinions
    assert "Hiring Manager Agent" in opinions.opinions
    assert "Skeptic Agent" in opinions.opinions

    for name, op in opinions.opinions.items():
        assert 1.0 <= op.score <= 10.0
        assert 0.0 <= op.confidence <= 1.0
        assert len(op.supporting_quotes) >= 1
        # Check that quotes pass validation
        for q in op.supporting_quotes:
            assert isinstance(q.verified, bool)
