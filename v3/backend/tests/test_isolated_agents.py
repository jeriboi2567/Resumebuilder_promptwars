import pytest
import inspect
from backend.schemas.models import CandidateProfile, JobDescription
from backend.profile_builder.builder import CandidateProfileBuilderV2
from backend.pdf_parser.parser import PDFDocumentParser
from backend.agents.technical_agent import TechnicalAgentV2
from backend.agents.hr_culture_agent import HRCultureAgentV2
from backend.agents.hiring_manager_agent import HiringManagerAgentV2
from backend.agents.skeptic_agent import SkepticAgentV2

def test_agent_signature_isolation():
    """
    Asserts strict agent isolation: Stage 2 agent evaluate() functions
    must accept ONLY CandidateProfile and JobDescription parameters.
    """
    agents = [TechnicalAgentV2(), HRCultureAgentV2(), HiringManagerAgentV2(), SkepticAgentV2()]
    for agent in agents:
        sig = inspect.signature(agent.evaluate)
        params = list(sig.parameters.keys())
        assert "profile" in params
        assert "jd" in params
        assert len(params) == 2, f"{agent.name} evaluate() takes extra parameters, breaking Stage 2 isolation!"

@pytest.mark.asyncio
async def test_insufficient_evidence_path_enforcement():
    """
    Asserts that any dimension lacking source evidence returns insufficient_evidence: True
    and score: None, preventing fabricated scores.
    """
    resume = "TAYLOR SMITH\nPython Engineer\n- Developed FastAPI REST APIs."
    transcript = "Interview Transcript - Candidate: Taylor Smith\nQ: Tell us about FastAPI.\nA: I built REST APIs."
    jd_text = "JOB DESCRIPTION: AI System Engineer\nRequired Skills: Python, FastAPI, PyTorch, Triton, CUDA"

    profile = CandidateProfileBuilderV2.build_profile("cand_taylor", resume, transcript)
    jd = PDFDocumentParser.parse_job_description(jd_text)

    agent = TechnicalAgentV2()
    opinion = await agent.evaluate(profile, jd)

    assert len(opinion.insufficient_dimensions) >= 1
    unmentioned_dim = next((d for d in opinion.dimension_evaluations if d.insufficient_evidence), None)
    assert unmentioned_dim is not None
    assert unmentioned_dim.score is None
    assert unmentioned_dim.reason is not None

@pytest.mark.asyncio
async def test_all_four_agents_independent_execution():
    resume = "MORGAN LEE\nBackend Engineer\n- Built Go services with PostgreSQL."
    transcript = "Interview Transcript - Candidate: Morgan Lee\nQ: How do you handle team disagreements?\nA: We hold retros and review metrics."
    jd_text = "JOB DESCRIPTION: Backend Engineer\nRequired Skills: Go, PostgreSQL"

    profile = CandidateProfileBuilderV2.build_profile("cand_morgan", resume, transcript)
    jd = PDFDocumentParser.parse_job_description(jd_text)

    tech = await TechnicalAgentV2().evaluate(profile, jd)
    hr = await HRCultureAgentV2().evaluate(profile, jd)
    hm = await HiringManagerAgentV2().evaluate(profile, jd)
    sk = await SkepticAgentV2().evaluate(profile, jd)

    assert tech.agent_name == "Technical Agent"
    assert hr.agent_name == "HR / Culture Agent"
    assert hm.agent_name == "Hiring Manager Agent"
    assert sk.agent_name == "Skeptic Agent"

    assert tech.overall_score is not None
    assert hr.overall_score is not None
    assert hm.overall_score is not None
    assert sk.overall_score is not None
