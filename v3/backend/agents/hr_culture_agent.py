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

        # Find relevant culture/communication quotes from candidate's quote bank
        quotes = []
        for q in profile.quote_bank:
            q_lower = q.quote.lower()
            if any(w in q_lower for w in ["team", "lead", "collaborat", "retro", "ownership", "learn", "project", "design", "deliver"]):
                quotes.append(SupportingQuote(quote=q.quote, source=q.location))
                if len(quotes) >= 2:
                    break

        if not quotes and profile.quote_bank:
            quotes.append(SupportingQuote(quote=profile.quote_bank[0].quote, source=profile.quote_bank[0].location))

        # Check for transparency, teamwork, or retention indicators in source text
        has_transparency = any(w in tr_text for w in ["retro", "ownership", "honest", "mistake", "learned", "review", "test"])
        has_retention_risk = "pay and title" in tr_text or "better pay" in tr_text or "hopping" in tr_text

        if has_transparency and not has_retention_risk:
            overall_score = 9.0
            verdict = "Strong Hire"
            quote_text = f" (e.g. \"{quotes[0].quote}\")" if quotes else ""
            reasoning = f"{cand_name} demonstrates high professional accountability, team collaboration, and learning mindset{quote_text}."
        elif has_retention_risk:
            overall_score = 6.0
            verdict = "Lean No"
            reasoning = f"{cand_name} exhibits potential job retention or alignment risks based on interview responses."
        else:
            overall_score = 7.8
            verdict = "Hire"
            quote_text = f" (e.g. \"{quotes[0].quote}\")" if quotes else ""
            reasoning = f"{cand_name} demonstrates standard team collaboration, technical communication, and workplace alignment{quote_text}."

        raw_dimensions = [
            DimensionEvaluation(
                dimension_name="Team Collaboration & Technical Communication",
                score=overall_score,
                insufficient_evidence=False,
                supporting_quote=quotes[0] if quotes else SupportingQuote(quote=f"{cand_name} interview transcript", source="transcript")
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
