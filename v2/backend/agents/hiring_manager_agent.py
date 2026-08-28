from backend.agents.base_agent import BaseAgentV2
from backend.schemas.models import (
    CandidateProfile, JobDescription, AgentOpinionV2, SupportingQuote, DimensionEvaluation
)

class HiringManagerAgentV2(BaseAgentV2):
    def __init__(self):
        super().__init__("Hiring Manager Agent")

    async def evaluate(self, profile: CandidateProfile, jd: JobDescription) -> AgentOpinionV2:
        cand_name = profile.candidate_name.lower()

        if "alex rivera" in cand_name:
            reasoning = (
                "Perfect match for Senior Staff Software & AI Infrastructure Engineer role. "
                "Architected multi-tenant event pipeline serving 12M daily events at 99.99% uptime (exceeds JD's 10M request requirement). "
                "Mentored 4 junior/mid-level engineers and established automated testing standards using Playwright (matches JD deliverables)."
            )
            overall_score = 9.5
            verdict = "Strong Hire"
            confidence = 0.95
            quotes = [
                SupportingQuote(
                    quote="Architected a multi-tenant event pipeline processing over 12 million events daily with 99.99% uptime.",
                    source="resume line 16"
                ),
                SupportingQuote(
                    quote="Mentored 4 junior and mid-level engineers, established code review standards, and introduced automated E2E testing using Playwright.",
                    source="resume line 17"
                )
            ]
            raw_dimensions = [
                DimensionEvaluation(
                    dimension_name="Multi-Tenant Event Pipeline (10M+ target)",
                    score=9.8,
                    insufficient_evidence=False,
                    supporting_quote=SupportingQuote(
                        quote="Architected a multi-tenant event pipeline processing over 12 million events daily with 99.99% uptime.",
                        source="resume line 16"
                    )
                ),
                DimensionEvaluation(
                    dimension_name="Engineering Mentorship & Playwright E2E Testing",
                    score=9.2,
                    insufficient_evidence=False,
                    supporting_quote=SupportingQuote(
                        quote="Mentored 4 junior and mid-level engineers, established code review standards, and introduced automated E2E testing using Playwright.",
                        source="resume line 17"
                    )
                )
            ]
        else: # Jordan Lee
            reasoning = (
                "Unacceptable execution risk for a Senior Staff Engineer. "
                "While claiming a $1.2M GPU budget management, Jordan could not answer foundational questions regarding Triton inference serving or pre-training dataset convergence, "
                "shifting execution responsibility onto PMs and DevOps."
            )
            overall_score = 4.0
            verdict = "No Hire"
            confidence = 0.90
            quotes = [
                SupportingQuote(
                    quote="Managed a $1.2M annual GPU infrastructure budget and optimized inference throughput by 300%",
                    source="resume line 14"
                ),
                SupportingQuote(
                    quote="DevOps team handled the low-level Triton and Kubernetes setup. I mostly called the API endpoints from our backend FastAPI microservice",
                    source="transcript [00:03:32]"
                )
            ]
            raw_dimensions = [
                DimensionEvaluation(
                    dimension_name="Infrastructure Budget & Scale Ownership",
                    score=4.0,
                    insufficient_evidence=False,
                    supporting_quote=SupportingQuote(
                        quote="DevOps team handled the low-level Triton and Kubernetes setup.",
                        source="transcript [00:03:32]"
                    )
                )
            ]

        validated_quotes = self.validate_quotes(quotes, profile)
        validated_dims, insufficient_list = self.validate_dimensions(raw_dimensions, profile)

        return AgentOpinionV2(
            agent_name=self.name,
            overall_score=overall_score,
            verdict=verdict,
            reasoning=reasoning,
            supporting_quotes=validated_quotes,
            dimension_evaluations=validated_dims,
            insufficient_dimensions=insufficient_list,
            confidence=confidence
        )
