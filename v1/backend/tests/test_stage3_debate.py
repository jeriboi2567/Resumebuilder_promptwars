import pytest
from backend.profile_builder.builder import CandidateProfileBuilder
from backend.agents.runner import run_stage2_independent_opinions
from backend.debate.orchestrator import Stage3DebateOrchestrator

@pytest.mark.asyncio
async def test_stage3_debate_orchestration():
    resume = "JORDAN LEE\nPrincipal AI Architect\n- Architected and trained a custom 70B parameter Large Language Model from scratch on 200 NVIDIA A100 GPUs"
    transcript = (
        "[00:01:25] Jordan Lee: We took a base LLaMA-2 70B model checkpoint from HuggingFace and performed supervised fine-tuning (SFT) and LoRA adapter training across a cluster of 8 A100 nodes\n"
        "[00:02:28] Jordan Lee: 200 GPU-hours was total compute across our experimentation phases over 3 months, not 200 GPUs simultaneously.\n"
        "[00:03:32] Jordan Lee: DevOps team handled the low-level Triton and Kubernetes setup. I mostly called the API endpoints from our backend FastAPI microservice\n"
        "[00:04:35] Jordan Lee: Usually timelines slip because non-technical project managers set unrealistic deadlines without understanding ML complexity."
    )

    profile = CandidateProfileBuilder.build_profile("cand_2", resume, transcript)
    opinions = await run_stage2_independent_opinions(profile)
    debate = Stage3DebateOrchestrator.run_debate(profile, opinions)

    assert debate.rounds >= 2
    assert len(debate.turns) >= 4
    
    # Check that turns address named agents and contain valid stances
    for turn in debate.turns:
        assert turn.responding_to != ""
        assert turn.stance in ['Agree', 'Disagree', 'Revise', 'Reinforce']

    # Verify stance deltas are tracked
    assert len(debate.stance_deltas) == 4
    tech_delta = debate.stance_deltas.get("Technical Agent")
    assert tech_delta is not None
    assert tech_delta.changed is True
    assert tech_delta.score_after < tech_delta.score_before
