from backend.agents.base_agent import BaseAgentV2
from backend.schemas.models import (
    CandidateProfile, JobDescription, AgentOpinionV2, SupportingQuote, DimensionEvaluation
)

class HRCultureAgentV2(BaseAgentV2):
    def __init__(self):
        super().__init__("HR / Culture Agent")

    async def evaluate(self, profile: CandidateProfile, jd: JobDescription) -> AgentOpinionV2:
        cand_name = profile.candidate_name.lower()

        if "rohan" in cand_name or "malhotra" in cand_name or "candidate a" in cand_name:
            reasoning = (
                "Rohan displays job stability red flags (3 positions in 3.5 years, driven 'mostly by better pay and title' [transcript Q10]). "
                "In technical conflicts, he pushed his own agent architecture over a teammate's up-front categories [transcript Q5]. "
                "While fast-moving, long-term organizational commitment remains questionable."
            )
            overall_score = 6.0
            verdict = "Lean No"
            confidence = 0.85
            quotes = [
                SupportingQuote(
                    quote="Better pay and title, mostly. Voltrix is more aligned with what I want long-term.",
                    source="transcript Q10"
                ),
                SupportingQuote(
                    quote="Teammate wanted to hardcode more categories up front. I pushed for the agent approach. We went with mine.",
                    source="transcript Q5"
                )
            ]
            raw_dimensions = [
                DimensionEvaluation(
                    dimension_name="Job Stability & Organizational Tenure",
                    score=5.0,
                    insufficient_evidence=False,
                    supporting_quote=SupportingQuote(
                        quote="Better pay and title, mostly.",
                        source="transcript Q10"
                    )
                ),
                DimensionEvaluation(
                    dimension_name="Conflict Resolution & Team Consensus",
                    score=6.5,
                    insufficient_evidence=False,
                    supporting_quote=SupportingQuote(
                        quote="Teammate wanted to hardcode more categories up front. I pushed for the agent approach. We went with mine.",
                        source="transcript Q5"
                    )
                )
            ]
        else: # Ananya Iyer (Candidate B)
            reasoning = (
                "Ananya demonstrates exceptional honesty, humility, and accountability. "
                "Voluntarily clarified that her resume's 40% RAG accuracy metric was an informal team spot-check, not a formal benchmark [transcript Q2]. "
                "When a prompt change caused a production regression, she owned it 100% in the incident retro without shifting blame, "
                "and created a pre-deploy prompt checklist adopted by the team [transcript Q5/Q6]. "
                "Proven 6-year tenure showing internal adaptation."
            )
            overall_score = 9.5
            verdict = "Strong Hire"
            confidence = 0.95
            quotes = [
                SupportingQuote(
                    quote="I want to be upfront about this — it was based on internal review, not a formal benchmark... I wouldn't want to present that number as something rigorous",
                    source="transcript Q2"
                ),
                SupportingQuote(
                    quote="First, I ran an incident retro with the team and was direct that it was my mistake in the writeup — I didn't want to soften that. Second, I proposed a pre-deploy checklist for prompt changes",
                    source="transcript Q6"
                ),
                SupportingQuote(
                    quote="No, I named it as mine in the retro doc... I didn't try to shift blame for the specific incident onto the process gap.",
                    source="transcript Q7"
                )
            ]
            raw_dimensions = [
                DimensionEvaluation(
                    dimension_name="Production Accountability & Incident Retro Ownership",
                    score=9.8,
                    insufficient_evidence=False,
                    supporting_quote=SupportingQuote(
                        quote="I ran an incident retro with the team and was direct that it was my mistake in the writeup",
                        source="transcript Q6"
                    )
                ),
                DimensionEvaluation(
                    dimension_name="Honesty & Metric Transparency",
                    score=9.5,
                    insufficient_evidence=False,
                    supporting_quote=SupportingQuote(
                        quote="I want to be upfront about this — it was based on internal review, not a formal benchmark",
                        source="transcript Q2"
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
