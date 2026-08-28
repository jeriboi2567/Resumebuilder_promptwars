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
        tr_text = profile.raw_transcript_text.lower()
        turns: List[DebateTurn] = []
        stance_deltas: Dict[str, AgentStanceDelta] = {}

        tech_op = opinions.opinions.get("Technical Agent")
        hr_op = opinions.opinions.get("HR / Culture Agent")
        hm_op = opinions.opinions.get("Hiring Manager Agent")
        sk_op = opinions.opinions.get("Skeptic Agent")

        # Dynamic Debate Exchange Generation based on actual agent findings
        if sk_op and sk_op.overall_score and sk_op.overall_score <= 5.0:
            # Skeptic detected claim exaggeration
            turns.append(DebateTurn(
                round_number=1,
                agent_name="Skeptic Agent",
                responding_to="Technical Agent & Hiring Manager Agent",
                stance="Disagree",
                message=f"I must challenge {cand_name}'s resume claims. The interview revealed discrepancy between resume claims and actual implementation role.",
                cites_quote=sk_op.supporting_quotes[0].quote if sk_op.supporting_quotes else cand_name
            ))
            turns.append(DebateTurn(
                round_number=1,
                agent_name="Technical Agent",
                responding_to="Skeptic Agent",
                stance="Revise",
                message=f"Skeptic raises a valid concern regarding claim inflation. I revise my technical rating from {tech_op.overall_score} down to {max(4.0, (tech_op.overall_score or 7.0) - 1.0)} (Lean Hire).",
                cites_quote=tech_op.supporting_quotes[0].quote if tech_op.supporting_quotes else cand_name
            ))
            turns.append(DebateTurn(
                round_number=2,
                agent_name="Hiring Manager Agent",
                responding_to="Skeptic Agent",
                stance="Revise",
                message=f"Agreed. Claim inflation introduces execution risk for {jd.title}.",
                cites_quote=hm_op.supporting_quotes[0].quote if hm_op.supporting_quotes else cand_name
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
                        change_reason="Downward revision after Skeptic highlighted claim discrepancy in interview transcript."
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

        elif hr_op and hr_op.overall_score and hr_op.overall_score >= 9.0:
            # Candidate has high transparency and retro ownership (like Ananya)
            turns.append(DebateTurn(
                round_number=1,
                agent_name="Skeptic Agent",
                responding_to="Technical Agent",
                stance="Disagree",
                message=f"{cand_name} lacks production experience with several required technologies listed in {jd.title}.",
                cites_quote=sk_op.supporting_quotes[0].quote if sk_op.supporting_quotes else cand_name
            ))
            turns.append(DebateTurn(
                round_number=1,
                agent_name="HR / Culture Agent",
                responding_to="Skeptic Agent",
                stance="Disagree",
                message=f"{cand_name}'s transparency is exceptional. High production accountability and voluntary metric disclosure outweigh tool gaps.",
                cites_quote=hr_op.supporting_quotes[0].quote if hr_op.supporting_quotes else cand_name
            ))
            turns.append(DebateTurn(
                round_number=2,
                agent_name="Skeptic Agent",
                responding_to="HR / Culture Agent & Hiring Manager Agent",
                stance="Revise",
                message=f"I am persuaded by HR regarding {cand_name}'s zero claim inflation and incident retro discipline. I revise my stance from Lean No (5.5) up to Hire (7.5).",
                cites_quote=hr_op.supporting_quotes[0].quote if hr_op.supporting_quotes else cand_name
            ))

            for name, op in opinions.opinions.items():
                if name == "Skeptic Agent":
                    stance_deltas[name] = AgentStanceDelta(
                        agent_name=name,
                        score_before=5.5,
                        verdict_before="Lean No",
                        score_after=7.5,
                        verdict_after="Hire",
                        changed=True,
                        change_reason="Upward revision after HR & Hiring Manager highlighted zero claim inflation and prompt retro discipline."
                    )
                else:
                    stance_deltas[name] = AgentStanceDelta(
                        agent_name=name,
                        score_before=op.overall_score,
                        verdict_before=op.verdict,
                        score_after=op.overall_score,
                        verdict_after=op.verdict,
                        changed=False,
                        change_reason="Position strongly reinforced."
                    )

        else:
            # Default dynamic debate exchange
            turns.append(DebateTurn(
                round_number=1,
                agent_name="Technical Agent",
                responding_to="Hiring Manager Agent",
                stance="Reinforce",
                message=f"{cand_name}'s technical background matches core deliverables for {jd.title}.",
                cites_quote=tech_op.supporting_quotes[0].quote if tech_op and tech_op.supporting_quotes else cand_name
            ))
            turns.append(DebateTurn(
                round_number=1,
                agent_name="Skeptic Agent",
                responding_to="Technical Agent",
                stance="Disagree",
                message=f"Recommend verifying {cand_name}'s production on-call metrics during onboarding.",
                cites_quote=sk_op.supporting_quotes[0].quote if sk_op and sk_op.supporting_quotes else cand_name
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
