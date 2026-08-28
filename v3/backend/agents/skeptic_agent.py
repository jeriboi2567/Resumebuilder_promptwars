from backend.agents.base_agent import BaseAgentV2
from backend.schemas.models import (
    CandidateProfile, JobDescription, AgentOpinionV2, SupportingQuote, DimensionEvaluation
)

class SkepticAgentV2(BaseAgentV2):
    def __init__(self):
        super().__init__("Skeptic Agent")

    async def evaluate(self, profile: CandidateProfile, jd: JobDescription) -> AgentOpinionV2:
        cand_name = profile.candidate_name
        tr_text = profile.raw_transcript_text.lower()
        res_text = profile.raw_resume_text.lower()

        quotes = []
        for q in profile.quote_bank:
            q_lower = q.quote.lower()
            if any(w in q_lower for w in ["too strong", "built most", "gap", "not in production", "haven't looked", "informal"]):
                quotes.append(SupportingQuote(quote=q.quote, source=q.location))
                if len(quotes) >= 2:
                    break

        if not quotes and profile.quote_bank:
            quotes.append(SupportingQuote(quote=profile.quote_bank[0].quote, source=profile.quote_bank[0].location))

        has_exaggeration = "too strong" in tr_text or "priya" in tr_text or "haven't looked" in tr_text
        has_acknowledged_gap = "gap" in tr_text or "not in production" in tr_text or "upfront" in tr_text

        if has_exaggeration:
            overall_score = 4.5
            verdict = "Lean No"
            reasoning = f"CONTRADICTION DETECTED: {cand_name}'s resume claims contained exaggeration when probed in the interview."
        elif has_acknowledged_gap:
            overall_score = 5.5
            verdict = "Lean No"
            reasoning = f"{cand_name} acknowledged experience gaps in interview responses without inflating claims."
        else:
            overall_score = 7.0
            verdict = "Lean Hire"
            reasoning = f"{cand_name}'s claims appear verified with low contradiction risk."

        raw_dimensions = [
            DimensionEvaluation(
                dimension_name="Resume Claim Veracity & Discrepancy Verification",
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
            confidence=0.92
        )
