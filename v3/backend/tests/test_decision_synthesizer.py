import pytest
from backend.profile_builder.builder import CandidateProfileBuilderV2
from backend.pdf_parser.parser import PDFDocumentParser
from backend.agents.runner import run_stage2_independent_opinions_v2
from backend.debate.orchestrator import Stage3DebateOrchestratorV2
from backend.decision.synthesizer import Stage4DecisionSynthesizerV2

@pytest.mark.asyncio
async def test_decision_synthesizer_evidence_weighting():
    resume = "JORDAN PATEL\nSenior Cloud Architect\n- Deployed AWS EKS clusters and Terraform modules."
    transcript = "Interview Transcript - Candidate: Jordan Patel\nQ: Describe your AWS EKS deployment.\nA: We managed 10 EKS clusters with Terraform."
    jd_text = "JOB DESCRIPTION: Cloud Architect\nRequired Skills: AWS, EKS, Terraform, Kubernetes"

    profile = CandidateProfileBuilderV2.build_profile("cand_jordan", resume, transcript)
    jd = PDFDocumentParser.parse_job_description(jd_text)

    opinions = await run_stage2_independent_opinions_v2(profile, jd)
    debate = Stage3DebateOrchestratorV2.run_debate(profile, jd, opinions)
    decision = Stage4DecisionSynthesizerV2.synthesize_decision(profile, jd, opinions, debate)

    assert decision.candidate_id == "cand_jordan"
    assert decision.recommendation in ["Hire", "Strong Hire"]
    assert decision.confidence >= 0.80
    assert len(decision.evidence_weights) == 4

    # Verify non-averaged evidence weights sum > 0 and factor quote verification
    for persona_name, weight in decision.evidence_weights.items():
        assert weight > 0.0
        assert weight <= 1.0

    assert decision.decision_rationale is not None
    assert "Jordan Patel" in decision.decision_rationale
