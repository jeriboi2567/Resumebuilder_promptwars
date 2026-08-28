import pytest
from backend.pipeline import MultiAgentPipelineOrchestrator
from backend.storage.repository import RunStorageRepository

@pytest.mark.asyncio
async def test_full_pipeline_end_to_end():
    resume = (
        "ALEX RIVERA\n"
        "Lead Full-Stack Engineer\n"
        "TECHNICAL SKILLS\n"
        "- Languages: TypeScript, Python, Go\n"
        "PROFESSIONAL EXPERIENCE\n"
        "Lead Engineer | Nexus Cloud | Jan 2022 – Present\n"
        "- Improved P99 endpoint latency by 40%\n"
    )
    transcript = (
        "[00:01:30] Alex Rivera: led a team of engineers—well, technically 5 dedicated backend/frontend engineers plus 3 embedded QA and design folks\n"
        "[00:02:30] Alex Rivera: The main bottleneck was unindexed JSONB queries in PostgreSQL combined with redundant REST polling."
    )

    result = await MultiAgentPipelineOrchestrator.run("cand_e2e_test", resume, transcript)

    assert result.run_id.startswith("run_")
    assert result.profile.candidate_name == "Alex Rivera"
    assert len(result.independent_opinions.opinions) == 4
    assert len(result.debate_state.turns) >= 2
    assert result.final_decision.recommendation in ['Strong Hire', 'Hire', 'Lean No', 'No Hire']
    assert len(result.report.markdown_content) > 100

    # Verify persistence storage
    saved = RunStorageRepository.get_run(result.run_id)
    assert saved is not None
    assert saved.run_id == result.run_id
    assert saved.final_decision.recommendation == result.final_decision.recommendation
