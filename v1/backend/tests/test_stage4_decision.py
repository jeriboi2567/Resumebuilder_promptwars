import pytest
from backend.profile_builder.builder import CandidateProfileBuilder
from backend.agents.runner import run_stage2_independent_opinions
from backend.debate.orchestrator import Stage3DebateOrchestrator
from backend.decision.synthesizer import Stage4DecisionSynthesizer

@pytest.mark.asyncio
async def test_stage4_decision_synthesis_non_averaged():
    resume = "TAYLOR MORGAN\nSoftware Engineer\n- Automated daily ETL data pipelines using Celery and Redis"
    transcript = (
        "[00:01:22] Taylor Morgan: Building asynchronous Celery workers to handle data ingestion and retry logic was challenging because of database lock contention\n"
        "[00:02:45] Taylor Morgan: To be transparent, I haven't worked with Kafka or Kubernetes in production yet.\n"
        "[00:04:05] Taylor Morgan: I welcome code reviews as learning opportunities. Early at CloudScale, my senior engineer pointed out that my API queries had N+1 performance problems. Rather than getting defensive, I asked him to pair with me"
    )

    profile = CandidateProfileBuilder.build_profile("cand_3", resume, transcript)
    opinions = await run_stage2_independent_opinions(profile)
    debate = Stage3DebateOrchestrator.run_debate(profile, opinions)
    decision = Stage4DecisionSynthesizer.synthesize_decision(profile, opinions, debate)

    assert decision.recommendation in ['Strong Hire', 'Hire', 'Lean No', 'No Hire']
    assert 0.0 <= decision.confidence <= 1.0
    assert len(decision.decision_rationale) > 50
    assert len(decision.evidence_weights) == 4
    
    # Check that unresolved disagreement is surfaced for candidate 3
    assert len(decision.unresolved_disagreements) >= 1
    assert "mentorship" in decision.unresolved_disagreements[0].lower() or "onboarding" in decision.unresolved_disagreements[0].lower()
