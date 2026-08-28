import pytest
from backend.pipeline import MultiAgentPipelineOrchestratorV3
from backend.schemas.models import JobDescription

@pytest.mark.asyncio
async def test_fresh_non_hackathon_generic_candidate():
    jd_text = """
    JOB DESCRIPTION: Principal Cloud Infrastructure Architect
    Company: Skyline Cloud Systems
    Role: Build scalable Kubernetes clusters, Terraform infrastructure, and high-throughput Go gRPC services.
    Required Skills: Go, Kubernetes, Terraform, gRPC, AWS
    Responsibilities:
    - Architect multi-region EKS Kubernetes clusters.
    - Automate infrastructure provisioning using Terraform.
    Qualifications:
    - 7+ years of cloud platform engineering experience.
    """

    resume_text = """
    JORDAN HAYES
    Principal Cloud Engineer
    Experience:
    - Lead Cloud Architect — Nexa Systems (2022-Present): Built multi-region EKS clusters serving 50M requests/day using Terraform and Go gRPC.
    Skills: Go, Kubernetes, Terraform, gRPC, AWS, Docker
    """

    transcript_text = """
    Interview Transcript - Candidate: Jordan Hayes
    Q1: Walk us through your multi-region Kubernetes deployment with Terraform.
    A1: We deployed Terraform modules across 3 AWS regions with EKS.
    Q2: Tell us about a production incident you owned.
    A2: A terraform drift caused a DNS outage. I ran an incident retro, updated our CI/CD pre-commit hooks, and took 100% ownership.
    """

    role_id = "role_skyline_cloud"
    role = await MultiAgentPipelineOrchestratorV3.process_role_candidates(
        role_id=role_id,
        jd_text=jd_text,
        candidate_pairs=[("cand_jordan", resume_text, transcript_text)]
    )

    assert role.job_description.title == "Principal Cloud Infrastructure Architect"
    assert "cand_jordan" in role.candidate_results
    res = role.candidate_results["cand_jordan"]
    
    assert res.profile.candidate_name == "Jordan Hayes"
    assert res.final_decision.recommendation in ["Hire", "Strong Hire"]
    assert len(res.debate_state.turns) >= 2
    assert role.stage6_comparison is not None
    assert len(role.stage6_comparison.rankings) == 1
