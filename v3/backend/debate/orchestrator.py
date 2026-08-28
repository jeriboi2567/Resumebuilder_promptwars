from typing import List, Dict
from backend.schemas.models import (
    CandidateProfile, JobDescription, IndependentOpinionsV2, DebateState,
    DebateTurn, AgentStanceDelta
)

class Stage3DebateOrchestratorV2:
    @staticmethod
    def run_debate(
        profile: CandidateProfile,
        jd: JobDescription,
        opinions: IndependentOpinionsV2
    ) -> DebateState:
        cand_name = profile.candidate_name
        turns: List[DebateTurn] = []
        stance_deltas: Dict[str, AgentStanceDelta] = {}

        tech_op = opinions.opinions.get("Technical Agent")
        hr_op = opinions.opinions.get("HR / Culture Agent")
        hm_op = opinions.opinions.get("Hiring Manager Agent")
        sk_op = opinions.opinions.get("Skeptic Agent")

        tech_quote = tech_op.supporting_quotes[0].quote if tech_op and tech_op.supporting_quotes else f"{cand_name} technical skills"
        hr_quote = hr_op.supporting_quotes[0].quote if hr_op and hr_op.supporting_quotes else f"{cand_name} interview responses"
        hm_quote = hm_op.supporting_quotes[0].quote if hm_op and hm_op.supporting_quotes else f"{cand_name} experience"
        sk_quote = sk_op.supporting_quotes[0].quote if sk_op and sk_op.supporting_quotes else f"{cand_name} profile audit"

        if sk_op and sk_op.overall_score and sk_op.overall_score <= 5.0:
            # Skeptic detected claim exaggeration
            turns.append(DebateTurn(
                round_number=1,
                agent_name="Skeptic Agent",
                responding_to="Technical Agent & Hiring Manager Agent",
                stance="Disagree",
                message=f"I must challenge {cand_name}'s resume claims. Probing in the interview revealed discrepancy between claimed depth and actual implementation role.",
                cites_quote=sk_quote
            ))
            turns.append(DebateTurn(
                round_number=1,
                agent_name="Technical Agent",
                responding_to="Skeptic Agent",
                stance="Revise",
                message=f"Skeptic raises a valid point regarding claim depth. I revise my rating down to Lean Hire.",
                cites_quote=tech_quote
            ))
            turns.append(DebateTurn(
                round_number=2,
                agent_name="Hiring Manager Agent",
                responding_to="Skeptic Agent",
                stance="Revise",
                message=f"Agreed. Claim inflation introduces execution risk for deliverable goals in {jd.title}.",
                cites_quote=hm_quote
            ))

            for name, op in opinions.opinions.items():
                if name in ["Technical Agent", "Hiring Manager Agent"]:
                    new_score = max(4.0, (op.overall_score or 7.0) - 1.0)
                    stance_deltas[name] = AgentStanceDelta(
                        agent_name=name,
                        score_before=op.overall_score,
                        verdict_before=op.verdict,
                        score_after=new_score,
                        verdict_after="Lean Hire" if new_score >= 6.5 else "Lean No",
                        changed=True,
                        change_reason=f"Downward revision after Skeptic highlighted discrepancy in interview responses."
                    )
                else:
                    stance_deltas[name] = AgentStanceDelta(
                        agent_name=name,
                        score_before=op.overall_score,
                        verdict_before=op.verdict,
                        score_after=op.overall_score,
                        verdict_after=op.verdict,
                        changed=False,
                        change_reason="Position maintained."
                    )

        else:
            # Standard dynamic deliberation exchange
            turns.append(DebateTurn(
                round_number=1,
                agent_name="Technical Agent",
                responding_to="Hiring Manager Agent",
                stance="Reinforce",
                message=f"{cand_name}'s technical evidence directly aligns with primary deliverables required for {jd.title}.",
                cites_quote=tech_quote
            ))
            turns.append(DebateTurn(
                round_number=1,
                agent_name="Skeptic Agent",
                responding_to="Technical Agent",
                stance="Disagree",
                message=f"Recommend verifying {cand_name}'s hands-on depth during initial onboarding milestones.",
                cites_quote=sk_quote
            ))
            turns.append(DebateTurn(
                round_number=2,
                agent_name="HR / Culture Agent",
                responding_to="Skeptic Agent",
                stance="Agree",
                message=f"{cand_name}'s communication and transparency in source documents provide high confidence in team integration.",
                cites_quote=hr_quote
            ))

            for name, op in opinions.opinions.items():
                stance_deltas[name] = AgentStanceDelta(
                    agent_name=name,
                    score_before=op.overall_score,
                    verdict_before=op.verdict,
                    score_after=op.overall_score,
                    verdict_after=op.verdict,
                    changed=False,
                    change_reason="Position reinforced after reviewing cross-agent evidence."
                )

        return DebateState(
            candidate_id=profile.candidate_id,
            rounds=2,
            turns=turns,
            stance_deltas=stance_deltas
        )
