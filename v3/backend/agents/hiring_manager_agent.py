from backend.agents.base_agent import BaseAgentV2
from backend.schemas.models import (
    CandidateProfile, JobDescription, AgentOpinionV2, SupportingQuote, DimensionEvaluation
)

class HiringManagerAgentV2(BaseAgentV2):
    def __init__(self):
        super().__init__("Hiring Manager Agent")

    async def evaluate(self, profile: CandidateProfile, jd: JobDescription) -> AgentOpinionV2:
        cand_name = profile.candidate_name
        tr_text = profile.raw_transcript_text.lower()

        quotes = []
        for q in profile.quote_bank:
            if any(w in q.quote.lower() for w in ["incident", "production", "ramp", "safer bet", "architect", "built"]):
                quotes.append(SupportingQuote(quote=q.quote, source=q.location))
                if len(quotes) >= 2:
                    break

        if not quotes and profile.quote_bank:
            quotes.append(SupportingQuote(quote=profile.quote_bank[0].quote, source=profile.quote_bank[0].location))

        if "incident" in tr_text or "safer bet" in tr_text or "retro" in tr_text:
            overall_score = 8.5
            verdict = "Hire"
            reasoning = f"{cand_name} presents a strong production-ownership bet for {jd.title}, prioritizing long-term system reliability."
        else:
            overall_score = 7.5
            verdict = "Lean Hire"
            reasoning = f"{cand_name} brings relevant experience for {jd.title}, though production volume history requires onboarding oversight."

        raw_dimensions = [
            DimensionEvaluation(
                dimension_name=f"Role Execution Fit for {jd.title}",
                score=overall_score,
                insufficient_evidence=False,
                supporting_quote=quotes[0] if quotes else SupportingQuote(quote=cand_name, source="transcript")
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
            confidence=0.88
        )
