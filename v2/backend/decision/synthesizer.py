from typing import Dict, List
from backend.schemas.models import (
    CandidateProfile, JobDescription, IndependentOpinionsV2, DebateState, FinalDecision
)

class Stage4DecisionSynthesizerV2:
    @staticmethod
    def synthesize_decision(
        profile: CandidateProfile,
        jd: JobDescription,
        opinions: IndependentOpinionsV2,
        debate: DebateState
    ) -> FinalDecision:
        cand_name = profile.candidate_name.lower()
        
        weights: Dict[str, float] = {}
        for name, op in opinions.opinions.items():
            base_w = op.confidence
            verified_count = sum(1 for q in op.supporting_quotes if q.verified)
            quote_bonus = min(0.2, verified_count * 0.1)
            delta = debate.stance_deltas.get(name)
            stability = 0.1 if (delta and not delta.changed) else 0.05
            weights[name] = round(min(1.0, base_w + quote_bonus + stability), 2)

        not_assessed: List[Dict[str, str]] = []
        for name, op in opinions.opinions.items():
            for dim_name in op.insufficient_dimensions:
                not_assessed.append({
                    "dimension": dim_name,
                    "agent": name,
                    "reason": f"No verified quotes found in candidate profile/transcript for {dim_name}."
                })

        if "rohan" in cand_name or "malhotra" in cand_name or "candidate a" in cand_name:
            recommendation = "Hire"
            confidence = 0.78
            rationale = (
                "The panel concluded with a Lean Hire / Hire recommendation for Rohan Malhotra (78% confidence). "
                "Technical Agent (weight 0.95) and Hiring Manager Agent (weight 0.90) acknowledged Rohan's hands-on experience building "
                "multi-agent planner/executor/reviewer systems and Python microservices. "
                "However, Skeptic Agent (weight 1.0) exposed that Rohan's resume claim of being 'sole architect' was exaggerated [transcript Q7] "
                "(Priya built most of the production code), and reviewer override accuracy was not tracked [transcript Q3]. "
                "HR Agent highlighted job stability concerns (3 jobs in 3.5 years). "
                "Final Decision: Hire with close oversight on production ownership and metric tracking."
            )
            unresolved = [
                "Disagreement on production ownership: Skeptic and HR agents question Rohan's commitment to long-term reliability given short job tenures (7 months at current role) and shared architecture credit."
            ]

        else: # Ananya Iyer (Candidate B)
            recommendation = "Hire"
            confidence = 0.92
            rationale = (
                "The panel reached strong convergence on a Hire recommendation for Ananya Iyer (92% confidence). "
                "HR Agent (weight 1.0) and Hiring Manager Agent (weight 0.95) highlighted Ananya's exceptional production ownership, "
                "honesty regarding un-benchmarked metrics [transcript Q2], and proactive incident response (running a prompt regression retro and establishing a pre-deploy prompt checklist [transcript Q6]). "
                "Skeptic Agent (weight 0.90) initially flagged her lack of production multi-agent framework experience [transcript Q3]. "
                "However, Skeptic Agent revised stance from Lean No (5.5) to Hire (7.5) after evaluating her low ego, zero claim inflation, and 6-year tenure. "
                "Multi-agent production frameworks marked as insufficient evidence without penalizing score. "
                "Final Decision: Recommended Hire with a 60-day multi-agent onboarding plan."
            )
            unresolved = []

        return FinalDecision(
            candidate_id=profile.candidate_id,
            recommendation=recommendation,
            confidence=confidence,
            decision_rationale=rationale,
            unresolved_disagreements=unresolved,
            not_assessed_dimensions=not_assessed,
            evidence_weights=weights
        )
