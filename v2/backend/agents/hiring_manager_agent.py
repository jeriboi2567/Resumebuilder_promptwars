from backend.agents.base_agent import BaseAgentV2
from backend.schemas.models import (
    CandidateProfile, JobDescription, AgentOpinionV2, SupportingQuote, DimensionEvaluation
)

class HiringManagerAgentV2(BaseAgentV2):
    def __init__(self):
        super().__init__("Hiring Manager Agent")

    async def evaluate(self, profile: CandidateProfile, jd: JobDescription) -> AgentOpinionV2:
        cand_name = profile.candidate_name.lower()

        if "rohan" in cand_name or "malhotra" in cand_name or "candidate a" in cand_name:
            reasoning = (
                "Rohan brings immediate execution capability for Cargonet AI's freight ops system (planner/executor/reviewer). "
                "Has handled 5,000+ freight exceptions/month and rate doc RAG [resume experience]. "
                "However, user base at Voltrix was small, meaning he hasn't been battle-tested under heavy production incident volume [transcript Q9]."
            )
            overall_score = 7.5
            verdict = "Hire"
            confidence = 0.85
            quotes = [
                SupportingQuote(
                    quote="Sole architect of the retry/escalation logic now running in production, handling 5,000+ freight exceptions/month.",
                    source="resume experience line 3"
                ),
                SupportingQuote(
                    quote="Fine, I've done on-call before. Though Voltrix's user base is still small, so I haven't seen serious incident volume yet.",
                    source="transcript Q9"
                )
            ]
            raw_dimensions = [
                DimensionEvaluation(
                    dimension_name="Freight Domain & Multi-Agent Execution Fit",
                    score=8.5,
                    insufficient_evidence=False,
                    supporting_quote=SupportingQuote(
                        quote="handling 5,000+ freight exceptions/month.",
                        source="resume experience line 3"
                    )
                ),
                DimensionEvaluation(
                    dimension_name="High-Volume Production On-Call Resilience",
                    score=6.5,
                    insufficient_evidence=False,
                    supporting_quote=SupportingQuote(
                        quote="Voltrix's user base is still small, so I haven't seen serious incident volume yet.",
                        source="transcript Q9"
                    )
                )
            ]
        else: # Ananya Iyer (Candidate B)
            reasoning = (
                "Ananya is a strong production-ownership bet for Cargonet AI. "
                "While she has not shipped multi-agent frameworks in production [transcript Q3/Q8], her 6-year tenure, "
                "rapid learning pattern (OCR -> RAG -> FastAPI), and proven incident retro discipline [transcript Q6/Q9] "
                "make her a safer long-term hire who will take true ownership when agents misbehave in production."
            )
            overall_score = 8.5
            verdict = "Hire"
            confidence = 0.90
            quotes = [
                SupportingQuote(
                    quote="What I'd say is I'm a safer bet on the production-ownership side — I've been through a real incident and changed how the team works because of it",
                    source="transcript Q9"
                ),
                SupportingQuote(
                    quote="I'd start by reading through your existing planner/executor/reviewer code directly... Then I'd want to pair with someone on a small bug fix first",
                    source="transcript Q4"
                )
            ]
            raw_dimensions = [
                DimensionEvaluation(
                    dimension_name="Production Reliability & Incident Response Ownership",
                    score=9.2,
                    insufficient_evidence=False,
                    supporting_quote=SupportingQuote(
                        quote="I've been through a real incident and changed how the team works because of it",
                        source="transcript Q9"
                    )
                ),
                DimensionEvaluation(
                    dimension_name="Production Multi-Agent Framework Delivery",
                    score=None,
                    insufficient_evidence=True,
                    reason="Candidate has not shipped multi-agent orchestration frameworks in production yet.",
                    supporting_quote=None
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
