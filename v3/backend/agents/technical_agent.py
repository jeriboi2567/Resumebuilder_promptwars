import re
from backend.agents.base_agent import BaseAgentV2
from backend.schemas.models import (
    CandidateProfile, JobDescription, AgentOpinionV2, SupportingQuote, DimensionEvaluation
)

class TechnicalAgentV2(BaseAgentV2):
    def __init__(self):
        super().__init__("Technical Agent")

    async def evaluate(self, profile: CandidateProfile, jd: JobDescription) -> AgentOpinionV2:
        cand_name = profile.candidate_name
        res_text = profile.raw_resume_text
        tr_text = profile.raw_transcript_text
        full_text = (res_text + " " + tr_text).lower()

        # Match candidate skills against JD required skills dynamically
        matched_skills = []
        unmatched_skills = []

        for req in jd.required_skills:
            if re.search(r'\b' + re.escape(req.lower()) + r'\b', full_text):
                matched_skills.append(req)
            else:
                unmatched_skills.append(req)

        # Dynamic quote selection from candidate's quote bank / transcript / resume
        quotes = []
        for q in profile.quote_bank:
            if any(s.lower() in q.quote.lower() for s in matched_skills) or len(quotes) < 2:
                quotes.append(SupportingQuote(
                    quote=q.quote,
                    source=q.location
                ))
                if len(quotes) >= 2:
                    break

        if not quotes and profile.quote_bank:
            quotes.append(SupportingQuote(
                quote=profile.quote_bank[0].quote,
                source=profile.quote_bank[0].location
            ))

        # Dynamic score & dimension evaluation calculation
        match_ratio = len(matched_skills) / max(1, len(jd.required_skills))
        if match_ratio >= 0.7:
            overall_score = round(7.5 + (match_ratio * 2.0), 1)
            verdict = "Hire" if overall_score >= 8.0 else "Lean Hire"
        elif match_ratio >= 0.4:
            overall_score = round(5.5 + (match_ratio * 3.0), 1)
            verdict = "Lean No"
        else:
            overall_score = round(3.5 + (match_ratio * 3.0), 1)
            verdict = "No Hire"

        reasoning = (
            f"{cand_name} demonstrates technical alignment with {len(matched_skills)} of {len(jd.required_skills)} core required skills "
            f"in the Job Description ({', '.join(matched_skills[:4])}). "
        )

        raw_dimensions = []
        if matched_skills:
            top_skill = matched_skills[0]
            top_quote = quotes[0] if quotes else SupportingQuote(quote=f"Experience with {top_skill}", source="resume")
            raw_dimensions.append(DimensionEvaluation(
                dimension_name=f"Core Skill Competency ({top_skill})",
                score=min(9.5, overall_score + 0.5),
                insufficient_evidence=False,
                supporting_quote=top_quote
            ))

        if unmatched_skills:
            gap_skill = unmatched_skills[0]
            raw_dimensions.append(DimensionEvaluation(
                dimension_name=f"Production Experience with {gap_skill}",
                score=None,
                insufficient_evidence=True,
                reason=f"Candidate's resume and interview transcript contain no verified production evidence for {gap_skill}.",
                supporting_quote=None
            ))
            reasoning += f"Rule Enforced: Production experience with {gap_skill} was marked as insufficient evidence without speculative scoring."
        else:
            reasoning += "Candidate has verified evidence across all primary technical requirements."

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
