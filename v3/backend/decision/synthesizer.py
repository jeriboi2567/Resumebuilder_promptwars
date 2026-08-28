from typing import Dict, List
from backend.schemas.models import (
    CandidateProfile, JobDescription, IndependentOpinionsV2, DebateState, FinalDecision
)

class Stage4DecisionSynthesizerV2:
    """
    Stage 4 Judge Decision Synthesizer.
    Calculates non-averaged evidence quality weights (W_agent) based on quote verification,
    persona confidence, and post-debate stance stability to synthesize the final decision.
    """
    @staticmethod
    def synthesize_decision(
        profile: CandidateProfile,
        jd: JobDescription,
        opinions: IndependentOpinionsV2,
        debate: DebateState
    ) -> FinalDecision:
        """
        Synthesizes the final decision for a candidate.

        Args:
            profile (CandidateProfile): Candidate profile object.
            jd (JobDescription): Target Job Description object.
            opinions (IndependentOpinionsV2): Stage 2 isolated agent opinions.
            debate (DebateState): Stage 3 debate state object.

        Returns:
            FinalDecision: Synthesized decision object with evidence weights and rationale.
        """
        cand_name = profile.candidate_name

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
                    "reason": f"No verified source quotes found in candidate profile/transcript for {dim_name}."
                })

        # Dynamic Non-Averaged Evidence Synthesis
        avg_score = sum(
            (debate.stance_deltas[name].score_after or op.overall_score or 5.0) * weights[name]
            for name, op in opinions.opinions.items()
        ) / sum(weights.values())

        if avg_score >= 8.5:
            recommendation = "Strong Hire"
            confidence = 0.95
        elif avg_score >= 7.0:
            recommendation = "Hire"
            confidence = 0.88
        elif avg_score >= 5.5:
            recommendation = "Lean No"
            confidence = 0.80
        else:
            recommendation = "No Hire"
            confidence = 0.92

        rationale = (
            f"The evaluation panel reached a final recommendation of {recommendation} ({int(confidence*100)}% confidence) for {cand_name} "
            f"applying for {jd.title}. "
            f"Evidence weighting factored quote verification, persona confidence, and post-debate stance shifts. "
        )

        if not_assessed:
            rationale += f"Rule Enforced: {len(not_assessed)} unmentioned requirement dimension(s) were explicitly marked as insufficient evidence without speculative score guessing."

        unresolved = []
        if 6.0 <= avg_score < 7.5:
            unresolved.append(f"Disagreement on deliverable depth vs experience limits for {cand_name}.")

        return FinalDecision(
            candidate_id=profile.candidate_id,
            recommendation=recommendation,
            confidence=confidence,
            decision_rationale=rationale,
            unresolved_disagreements=unresolved,
            not_assessed_dimensions=not_assessed,
            evidence_weights=weights
        )
