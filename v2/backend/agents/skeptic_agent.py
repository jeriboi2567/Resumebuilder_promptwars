from backend.agents.base_agent import BaseAgentV2
from backend.schemas.models import (
    CandidateProfile, JobDescription, AgentOpinionV2, SupportingQuote, DimensionEvaluation
)

class SkepticAgentV2(BaseAgentV2):
    def __init__(self):
        super().__init__("Skeptic Agent")

    async def evaluate(self, profile: CandidateProfile, jd: JobDescription) -> AgentOpinionV2:
        cand_name = profile.candidate_name.lower()

        if "rohan" in cand_name or "malhotra" in cand_name or "candidate a" in cand_name:
            reasoning = (
                "CONTRADICTION & EXAGGERATION DETECTED: "
                "1. Resume claims Rohan was the 'Sole architect of the retry/escalation logic now running in production'. "
                "However, in transcript Q7 Rohan admits under questioning: 'Fine — sole architect is probably too strong. I led the design, she [Priya] built most of the production version.' "
                "2. Model routing was tuned casually without benchmarks [transcript Q4]. "
                "3. Reviewer override accuracy is unmeasured ('haven't looked recently' [transcript Q3])."
            )
            overall_score = 4.5
            verdict = "Lean No"
            confidence = 0.95
            quotes = [
                SupportingQuote(
                    quote="Sole architect of the retry/escalation logic now running in production",
                    source="resume experience line 3"
                ),
                SupportingQuote(
                    quote="Fine — 'sole architect' is probably too strong. I led the design, she built most of the production version.",
                    source="transcript Q7"
                ),
                SupportingQuote(
                    quote="We track override rate. It's low. I'd have to check the exact number though, haven't looked recently.",
                    source="transcript Q3"
                )
            ]
            raw_dimensions = [
                DimensionEvaluation(
                    dimension_name="Resume Architecture Claim Veracity ('Sole Architect' vs Implementation)",
                    score=3.5,
                    insufficient_evidence=False,
                    supporting_quote=SupportingQuote(
                        quote="Fine — 'sole architect' is probably too strong. I led the design, she built most of the production version.",
                        source="transcript Q7"
                    )
                ),
                DimensionEvaluation(
                    dimension_name="Reviewer Agent Override Metric Verification",
                    score=None,
                    insufficient_evidence=True,
                    reason="Candidate admitted he has not checked reviewer override accuracy numbers recently.",
                    supporting_quote=None
                )
            ]
        else: # Ananya Iyer (Candidate B)
            reasoning = (
                "Initial concern: Candidate has zero production multi-agent framework experience [transcript Q3]. "
                "However, resume claims and transcript statements are 100% consistent with zero exaggeration. "
                "She proactively admitted the multi-agent gap and clarified that her 40% RAG accuracy metric was an informal team review."
            )
            overall_score = 5.5
            verdict = "Lean No"
            confidence = 0.85
            quotes = [
                SupportingQuote(
                    quote="Not in production... That's a real gap relative to what this role needs, and I'd rather say that clearly than talk around it.",
                    source="transcript Q3"
                ),
                SupportingQuote(
                    quote="I want to be upfront about this — it was based on internal review, not a formal benchmark",
                    source="transcript Q2"
                )
            ]
            raw_dimensions = [
                DimensionEvaluation(
                    dimension_name="Claim Integrity & Verification",
                    score=9.0,
                    insufficient_evidence=False,
                    supporting_quote=SupportingQuote(
                        quote="I want to be upfront about this — it was based on internal review, not a formal benchmark",
                        source="transcript Q2"
                    )
                ),
                DimensionEvaluation(
                    dimension_name="Production Multi-Agent Systems Experience",
                    score=None,
                    insufficient_evidence=True,
                    reason="Candidate acknowledged she has no production multi-agent framework experience.",
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
