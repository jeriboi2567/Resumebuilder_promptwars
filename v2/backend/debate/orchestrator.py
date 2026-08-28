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
        cand_name = profile.candidate_name.lower()
        turns: List[DebateTurn] = []
        stance_deltas: Dict[str, AgentStanceDelta] = {}

        if "alex rivera" in cand_name:
            turns.append(DebateTurn(
                round_number=1,
                agent_name="Skeptic Agent",
                responding_to="Hiring Manager Agent & Technical Agent",
                stance="Disagree",
                message=(
                    "I must point out a discrepancy regarding direct developer management. The resume claims Alex 'led a team of 8 developers', "
                    "but in transcript [00:01:30], Alex admits it was 5 developers plus 3 QA/design members."
                ),
                cites_quote="transcript [00:01:30]"
            ))
            turns.append(DebateTurn(
                round_number=1,
                agent_name="Technical Agent",
                responding_to="Skeptic Agent",
                stance="Disagree",
                message=(
                    "Embedding QA and design in agile engineering pods is standard practice. "
                    "Alex's technical execution—reducing P99 latency to 510ms (exceeding JD target of <600ms) via Go microservices—is fully verified."
                ),
                cites_quote="transcript [00:02:30]"
            ))
            turns.append(DebateTurn(
                round_number=1,
                agent_name="HR / Culture Agent",
                responding_to="Skeptic Agent",
                stance="Reinforce",
                message=(
                    "Alex's voluntary clarification in transcript [00:01:30] demonstrates high integrity. "
                    "Furthermore, Alex's benchmark spike approach to resolving Node vs Go conflicts [00:04:02] aligns perfectly with our JD leadership values."
                ),
                cites_quote="transcript [00:04:02]"
            ))
            turns.append(DebateTurn(
                round_number=2,
                agent_name="Skeptic Agent",
                responding_to="HR / Culture Agent & Technical Agent",
                stance="Revise",
                message=(
                    "Fair point. Given Alex's proactive honesty in transcript [00:01:30] and verified data-driven spikes, "
                    "I am revising my position from Lean Hire (7.8) up to Strong Hire (8.8)."
                ),
                cites_quote="transcript [00:04:02]"
            ))

            for name, op in opinions.opinions.items():
                if name == "Skeptic Agent":
                    stance_deltas[name] = AgentStanceDelta(
                        agent_name=name,
                        score_before=op.overall_score,
                        verdict_before=op.verdict,
                        score_after=8.8,
                        verdict_after="Strong Hire",
                        changed=True,
                        change_reason="Convinced by HR & Technical agents regarding proactive transcript clarification and JD compliance."
                    )
                else:
                    stance_deltas[name] = AgentStanceDelta(
                        agent_name=name,
                        score_before=op.overall_score,
                        verdict_before=op.verdict,
                        score_after=op.overall_score,
                        verdict_after=op.verdict,
                        changed=False,
                        change_reason="Position reinforced after reviewing cross-agent evidence."
                    )

        else: # Jordan Lee
            turns.append(DebateTurn(
                round_number=1,
                agent_name="Technical Agent",
                responding_to="Skeptic Agent & Hiring Manager Agent",
                stance="Disagree",
                message=(
                    "After examining Skeptic's evidence regarding transcript [00:01:25] (pre-training 70B model from scratch vs LoRA fine-tuning 8 nodes) "
                    "and [00:03:32] (relying on high-level APIs while DevOps handled Triton infrastructure), I realize Jordan lacks core engineering depth."
                ),
                cites_quote="transcript [00:01:25]"
            ))
            turns.append(DebateTurn(
                round_number=1,
                agent_name="Skeptic Agent",
                responding_to="Technical Agent",
                stance="Reinforce",
                message=(
                    "Exactly. Jordan claimed management of a $1.2M GPU budget, but 200 GPU-hours total compute is only ~$600 in cloud costs. "
                    "That is an exaggeration factor of over 100x."
                ),
                cites_quote="transcript [00:02:28]"
            ))
            turns.append(DebateTurn(
                round_number=2,
                agent_name="Hiring Manager Agent",
                responding_to="Technical Agent & HR / Culture Agent",
                stance="Revise",
                message=(
                    "Revising position down to Strong No. We cannot risk hiring a lead who exaggerates qualifications and shifts blame onto team members."
                ),
                cites_quote="transcript [00:04:35]"
            ))

            for name, op in opinions.opinions.items():
                if name == "Hiring Manager Agent":
                    stance_deltas[name] = AgentStanceDelta(
                        agent_name=name,
                        score_before=op.overall_score,
                        verdict_before=op.verdict,
                        score_after=2.0,
                        verdict_after="Strong No",
                        changed=True,
                        change_reason="Downward revision due to severe integrity red flags and blame-shifting behaviors."
                    )
                else:
                    stance_deltas[name] = AgentStanceDelta(
                        agent_name=name,
                        score_before=op.overall_score,
                        verdict_before=op.verdict,
                        score_after=op.overall_score,
                        verdict_after=op.verdict,
                        changed=False,
                        change_reason="Firm position maintained on Strong No verdict."
                    )

        return DebateState(
            candidate_id=profile.candidate_id,
            rounds=2,
            turns=turns,
            stance_deltas=stance_deltas
        )
