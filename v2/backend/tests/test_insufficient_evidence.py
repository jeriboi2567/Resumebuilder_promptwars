import pytest
from backend.profile_builder.builder import CandidateProfileBuilderV2
from backend.agents.technical_agent import TechnicalAgentV2
from backend.pdf_parser.parser import PDFDocumentParser

@pytest.mark.asyncio
async def test_insufficient_evidence_rule_enforcement():
    resume = "ALEX RIVERA\nSenior Full-Stack Engineer\n- Improved P99 endpoint latency by 40%"
    transcript = "[00:02:30] Alex Rivera: The main bottleneck was unindexed JSONB queries in PostgreSQL."
    jd_text = "JOB DESCRIPTION: Senior Staff Engineer\nRequired: PyTorch, CUDA, Triton"

    profile = CandidateProfileBuilderV2.build_profile("cand_1", resume, transcript)
    jd = PDFDocumentParser.parse_job_description(jd_text)

    agent = TechnicalAgentV2()
    opinion = await agent.evaluate(profile, jd)

    assert len(opinion.insufficient_dimensions) >= 1
    assert any("Multi-Agent" in dim or "Frameworks" in dim or "LLM" in dim or "Triton" in dim for dim in opinion.insufficient_dimensions)
    
    # Verify that insufficient dimensions have insufficient_evidence=True and score=None
    for dim in opinion.dimension_evaluations:
        if dim.insufficient_evidence:
            assert dim.score is None
            assert dim.reason is not None
            assert len(dim.reason) > 5
