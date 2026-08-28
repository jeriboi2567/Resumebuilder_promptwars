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
        res_text = profile.raw_resume_text.lower()

        quotes = []
        for q in profile.quote_bank:
            q_lower = q.quote.lower()
            if any(w in q_lower for w in ["built", "design", "deliver", "architect", "lead", "project", "board", "service", "system"]):
                quotes.append(SupportingQuote(quote=q.quote, source=q.location))
                if len(quotes) >= 2:
                    break

        if not quotes and profile.quote_bank:
            quotes.append(SupportingQuote(quote=profile.quote_bank[0].quote, source=profile.quote_bank[0].location))

        # Check candidate experience items and skill matches
        has_delivery_history = len(profile.experiences) > 0 or len(profile.skills) >= 2
        quote_text = f" (e.g. \"{quotes[0].quote}\")" if quotes else ""

        if has_delivery_history:
            overall_score = 8.4
            verdict = "Hire"
            reasoning = f"{cand_name} presents a strong execution and delivery profile for {jd.title}{quote_text}."
        else:
            overall_score = 7.0
            verdict = "Lean Hire"
            reasoning = f"{cand_name} demonstrates relevant technical foundation for {jd.title}, though onboarding supervision is recommended."

        raw_dimensions = [
            DimensionEvaluation(
                dimension_name=f"Role Execution & Technical Deliverable Fit for {jd.title}",
                score=overall_score,
                insufficient_evidence=False,
                supporting_quote=quotes[0] if quotes else SupportingQuote(quote=f"{cand_name} profile", source="resume")
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
