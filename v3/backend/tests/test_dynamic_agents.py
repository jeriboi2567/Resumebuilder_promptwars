import pytest
from backend.profile_builder.builder import CandidateProfileBuilderV2
from backend.pdf_parser.parser import PDFDocumentParser
from backend.agents.technical_agent import TechnicalAgentV2

@pytest.mark.asyncio
async def test_dynamic_insufficient_evidence_rule():
    resume = "TAYLOR MORGAN\nPython Developer\n- Built REST APIs using FastAPI."
    transcript = "Q1: Tell me about your FastAPI experience.\nA1: I built REST APIs."
    jd_text = "JOB DESCRIPTION: AI Engineer\nRequired Skills: Python, PyTorch, Triton, CUDA"

    profile = CandidateProfileBuilderV2.build_profile("cand_test_02", resume, transcript)
    jd = PDFDocumentParser.parse_job_description(jd_text)

    agent = TechnicalAgentV2()
    opinion = await agent.evaluate(profile, jd)

    assert len(opinion.insufficient_dimensions) >= 1
    for dim in opinion.dimension_evaluations:
        if dim.insufficient_evidence:
            assert dim.score is None
            assert dim.reason is not None
