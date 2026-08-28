import re
from backend.agents.base_agent import BaseAgentV2
from backend.schemas.models import (
    CandidateProfile, JobDescription, AgentOpinionV2, SupportingQuote, DimensionEvaluation
)

class HRCultureAgentV2(BaseAgentV2):
    def __init__(self):
        super().__init__("HR / Culture Agent")

    async def evaluate(self, profile: CandidateProfile, jd: JobDescription) -> AgentOpinionV2:
        cand_name = profile.candidate_name
        tr_text = profile.raw_transcript_text.lower()
        res_text = profile.raw_resume_text.lower()

        quotes = []
        # Look for accountability, retro, or mistake disclosures
        for q in profile.quote_bank:
            q_lower = q.quote.lower()
            if any(w in q_lower for w in ["retro", "upfront", "mistake", "checklist", "disagreed", "pay", "tenure"]):
                quotes.append(SupportingQuote(quote=q.quote, source=q.location))
                if len(quotes) >= 2:
                    break

        if not quotes and profile.quote_bank:
            quotes.append(SupportingQuote(quote=profile.quote_bank[0].quote, source=profile.quote_bank[0].location))

        # Detect honesty / accountability signals vs job hopping signals
        has_retro = "retro" in tr_text or "upfront" in tr_text or "mistake" in tr_text or "checklist" in tr_text
        has_tenure_risk = "pay and title" in tr_text or "better pay" in tr_text

        if has_retro and not has_tenure_risk:
            overall_score = 9.2
            verdict = "Strong Hire"
            reasoning = f"{cand_name} demonstrates exceptional accountability, transparency, and production incident ownership."
        elif has_tenure_risk:
            overall_score = 6.0
            verdict = "Lean No"
            reasoning = f"{cand_name} exhibits potential job stability or retention risks based on interview responses."
        else:
            overall_score = 7.5
            verdict = "Hire"
            reasoning = f"{cand_name} demonstrates standard team collaboration and communication."

        raw_dimensions = [
            DimensionEvaluation(
                dimension_name="Production Accountability & Incident Retro Ownership",
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
            confidence=0.90
        )
