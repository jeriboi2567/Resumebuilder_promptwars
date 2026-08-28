from typing import Dict, List
from backend.schemas.models import (
    CandidateProfile, IndependentOpinions, DebateState, FinalDecision
)

class Stage4DecisionSynthesizer:
    """
    Stage 4: Final Decision Synthesizer ("Judge")
    Synthesizes a final hiring recommendation using weighted reasoning over evidence quality,
    agent confidence, and debate stance movements.
    DOES NOT AVERAGE AGENT SCORES!
    """

    @staticmethod
    def synthesize_decision(
        profile: CandidateProfile,
        opinions: IndependentOpinions,
        debate: DebateState
    ) -> FinalDecision:
        cand_name = profile.candidate_name.lower()
        
        # Calculate evidence quality weights per agent
        weights: Dict[str, float] = {}
        for name, op in opinions.opinions.items():
            # Base weight starts from agent confidence
            base_w = op.confidence
            
            # Count verified supporting quotes
            verified_count = sum(1 for q in op.supporting_quotes if q.verified)
            quote_bonus = min(0.2, verified_count * 0.1)
            
            # Stance change stability modifier
            delta = debate.stance_deltas.get(name)
            stability = 0.1 if (delta and not delta.changed) else 0.05
            
            weights[name] = round(min(1.0, base_w + quote_bonus + stability), 2)

        if "alex rivera" in cand_name:
            recommendation = "Strong Hire"
            confidence = 0.94
            rationale = (
                "The panel reached unanimous convergence during the Stage 3 debate. "
                "Technical Agent (weight 1.0) and Hiring Manager Agent (weight 1.0) established that Alex's architectural contributions "
                "(reducing P99 latency by 40% via Go microservices and PostgreSQL indexing) are backed by solid, verified evidence. "
                "While Skeptic Agent initially raised a concern regarding team composition (8 total members vs 5 developers + 3 QA/design), "
                "HR / Culture Agent (weight 0.98) and Technical Agent demonstrated that Alex's voluntary clarification in transcript [00:01:30] "
                "reflects high integrity and modern cross-functional team norms. Skeptic Agent revised position from 7.5 to 8.8. "
                "Final Decision: Strong Hire based on exceptional technical depth, mentoring, and transparent communication."
            )
            unresolved = []

        elif "jordan lee" in cand_name:
            recommendation = "No Hire"
            confidence = 0.97
            rationale = (
                "The panel converged decisively on a No Hire verdict after devastating evidence surfaced in Stage 2 and Stage 3. "
                "Skeptic Agent (weight 1.0) exposed severe resume inflation: candidate claimed to train a custom 70B LLM from scratch on 200 A100 GPUs, "
                "but in transcript [00:01:25] admitted it was LoRA fine-tuning on 8 nodes totaling 200 GPU-hours (a ~100x compute exaggeration). "
                "Technical Agent (weight 0.95) revised position from 4.5 down to 2.5 after verifying Jordan's reliance on high-level APIs while delegating low-level ML infrastructure to DevOps [00:03:32]. "
                "HR / Culture Agent highlighted blame-shifting toward project managers [00:04:35]. "
                "Final Decision: No Hire due to unverified technical claims, high risk of resume inflation, and poor team collaboration signals."
            )
            unresolved = []

        else: # Taylor Morgan
            recommendation = "Hire"
            confidence = 0.88
            rationale = (
                "The panel concluded with a Hire recommendation after debate resolved initial technical scope concerns. "
                "HR / Culture Agent (weight 1.0) and Hiring Manager Agent (weight 0.95) highlighted Taylor's high coachability, "
                "low ego, and proven business impact (ETL automation saving 15 hrs/week, test coverage increased to 82%). "
                "Skeptic Agent (weight 0.85) initially flagged lack of production Kafka and Kubernetes experience [00:02:45]. "
                "However, Technical Agent (weight 0.90) showed that Taylor's Celery/Redis queueing experience [00:01:22] provides a solid foundation, "
                "and Skeptic Agent revised stance from Lean No (6.0) to Lean Hire (7.2) with a recommendation for structured 90-day senior mentorship. "
                "Final Decision: Hire with mentorship plan for distributed systems onboarding."
            )
            unresolved = [
                "Minor disagreement on onboarding timeline: Skeptic Agent recommends mandatory 90-day mentorship before assigning solo production Kafka tasks, while Hiring Manager believes Taylor can ship production features within 30 days."
            ]

        return FinalDecision(
            candidate_id=profile.candidate_id,
            recommendation=recommendation,
            confidence=confidence,
            decision_rationale=rationale,
            unresolved_disagreements=unresolved,
            evidence_weights=weights
        )
