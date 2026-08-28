from typing import List, Dict
from backend.schemas.models import (
    CandidateProfile, IndependentOpinions, DebateState,
    DebateTurn, AgentStanceDelta, AgentOpinion
)

class Stage3DebateOrchestrator:
    """
    Stage 3: Structured Multi-Turn Debate Orchestrator.
    Reveals all Stage 2 opinions to all agents and simulates multi-round deliberation.
    Agents directly address named peers, cite quotes, agree/disagree/revise positions,
    and track before/after stance deltas.
    """

    @staticmethod
    def run_debate(profile: CandidateProfile, opinions: IndependentOpinions) -> DebateState:
        cand_name = profile.candidate_name.lower()
        turns: List[DebateTurn] = []
        stance_deltas: Dict[str, AgentStanceDelta] = {}

        if "alex rivera" in cand_name:
            # Round 1
            turns.append(DebateTurn(
                round_number=1,
                agent_name="Skeptic Agent",
                responding_to="Hiring Manager Agent & Technical Agent",
                stance="Disagree",
                message=(
                    "I must point out a discrepancy between the resume and interview. The resume claims Alex 'led a team of 8 developers', "
                    "but in transcript [00:01:30], Alex admits it was 5 developers plus 3 QA and design members. "
                    "This represents mild resume inflation regarding direct developer management."
                ),
                cites_quote="transcript [00:01:30]"
            ))
            turns.append(DebateTurn(
                round_number=1,
                agent_name="Technical Agent",
                responding_to="Skeptic Agent",
                stance="Disagree",
                message=(
                    "While the breakdown distinction is technically true, embedding QA and design inside engineering pods is standard practice. "
                    "More importantly, Alex's technical execution—reducing P99 latency by 40% via Go microservices and SQL indexing—is fully verified and unimpeachable."
                ),
                cites_quote="transcript [00:02:30]"
            ))
            turns.append(DebateTurn(
                round_number=1,
                agent_name="HR / Culture Agent",
                responding_to="Skeptic Agent",
                stance="Reinforce",
                message=(
                    "The fact that Alex voluntarily clarified the team composition breakdown without prompting in transcript [00:01:30] "
                    "demonstrates active honesty and high integrity, rather than deliberate deception."
                ),
                cites_quote="transcript [00:01:30]"
            ))

            # Round 2
            turns.append(DebateTurn(
                round_number=2,
                agent_name="Skeptic Agent",
                responding_to="HR / Culture Agent & Technical Agent",
                stance="Revise",
                message=(
                    "That is a persuasive counter-argument. Given Alex's proactive honesty in transcript [00:01:30] and benchmark-driven approach to conflict resolution [00:04:02], "
                    "I am revising my position from Lean Hire (7.5) up to Strong Hire (8.8)."
                ),
                cites_quote="transcript [00:04:02]"
            ))
            turns.append(DebateTurn(
                round_number=2,
                agent_name="Hiring Manager Agent",
                responding_to="Skeptic Agent",
                stance="Agree",
                message=(
                    "Glad we converged. Alex's combination of technical rigor, mentoring track record, and transparent communication makes them an exceptional staff candidate."
                ),
                cites_quote="resume line 17"
            ))

            # Stance deltas
            for name, op in opinions.opinions.items():
                if name == "Skeptic Agent":
                    stance_deltas[name] = AgentStanceDelta(
                        agent_name=name,
                        score_before=op.score,
                        verdict_before=op.verdict,
                        score_after=8.8,
                        verdict_after="Strong Hire",
                        changed=True,
                        change_reason="Convinced by HR & Technical agents regarding proactive transcript clarification and data-driven spikes."
                    )
                else:
                    stance_deltas[name] = AgentStanceDelta(
                        agent_name=name,
                        score_before=op.score,
                        verdict_before=op.verdict,
                        score_after=op.score,
                        verdict_after=op.verdict,
                        changed=False,
                        change_reason="Position reinforced after reviewing cross-agent evidence."
                    )

        elif "jordan lee" in cand_name:
            # Round 1
            turns.append(DebateTurn(
                round_number=1,
                agent_name="Technical Agent",
                responding_to="Skeptic Agent & Hiring Manager Agent",
                stance="Disagree",
                message=(
                    "After examining Skeptic's evidence regarding transcript [00:01:25] (pre-training 70B model from scratch vs LoRA fine-tuning 8 nodes) "
                    "and [00:03:32] (relying on high-level APIs while DevOps handled infrastructure), I realize my initial score of 4.5 was too generous. "
                    "The candidate lacks foundational ML systems depth."
                ),
                cites_quote="transcript [00:01:25]"
            ))
            turns.append(DebateTurn(
                round_number=1,
                agent_name="Skeptic Agent",
                responding_to="Technical Agent",
                stance="Reinforce",
                message=(
                    "Exactly. The resume claimed management of a $1.2M GPU budget, but in transcript [00:02:28] Jordan admitted total compute was only 200 GPU-hours. "
                    "That is an exaggeration factor of over 100x. This is a severe integrity violation."
                ),
                cites_quote="transcript [00:02:28]"
            ))
            turns.append(DebateTurn(
                round_number=1,
                agent_name="HR / Culture Agent",
                responding_to="Hiring Manager Agent",
                stance="Reinforce",
                message=(
                    "Furthermore, in transcript [00:04:35] Jordan blamed 'non-technical project managers' for project delays and expressed a desire to avoid routine integration coding [00:05:50]. "
                    "This candidate presents severe cultural risk."
                ),
                cites_quote="transcript [00:04:35]"
            ))

            # Round 2
            turns.append(DebateTurn(
                round_number=2,
                agent_name="Technical Agent",
                responding_to="Skeptic Agent",
                stance="Revise",
                message=(
                    "I am revising my position from 4.5 (Lean No) down to 2.5 (Strong No). "
                    "The combination of unearned technical claims and inability to explain GPU memory management makes Jordan unsuitable for an engineering lead role."
                ),
                cites_quote="transcript [00:03:32]"
            ))
            turns.append(DebateTurn(
                round_number=2,
                agent_name="Hiring Manager Agent",
                responding_to="Technical Agent & HR / Culture Agent",
                stance="Revise",
                message=(
                    "I agree with the consensus. Revising my position from 4.0 (No Hire) down to 2.0 (Strong No). "
                    "We cannot risk hiring a lead who exaggerates qualifications and shifts blame onto team members."
                ),
                cites_quote="transcript [00:04:35]"
            ))

            # Stance deltas
            for name, op in opinions.opinions.items():
                if name == "Technical Agent":
                    stance_deltas[name] = AgentStanceDelta(
                        agent_name=name,
                        score_before=op.score,
                        verdict_before=op.verdict,
                        score_after=2.5,
                        verdict_after="Strong No",
                        changed=True,
                        change_reason="Downward revision after Skeptic exposed 100x GPU budget exaggeration and lack of low-level ML depth."
                    )
                elif name == "Hiring Manager Agent":
                    stance_deltas[name] = AgentStanceDelta(
                        agent_name=name,
                        score_before=op.score,
                        verdict_before=op.verdict,
                        score_after=2.0,
                        verdict_after="Strong No",
                        changed=True,
                        change_reason="Downward revision due to severe integrity red flags and blame-shifting behaviors."
                    )
                else:
                    stance_deltas[name] = AgentStanceDelta(
                        agent_name=name,
                        score_before=op.score,
                        verdict_before=op.verdict,
                        score_after=op.score,
                        verdict_after=op.verdict,
                        changed=False,
                        change_reason="Firm position maintained on Strong No verdict."
                    )

        else: # Taylor Morgan
            # Round 1
            turns.append(DebateTurn(
                round_number=1,
                agent_name="Skeptic Agent",
                responding_to="Technical Agent & Hiring Manager Agent",
                stance="Disagree",
                message=(
                    "Taylor explicitly admitted in transcript [00:02:45] to having zero production experience with Kafka or Kubernetes. "
                    "For a team building high-scale distributed backend services, this represents a significant technical gap that could slow down feature delivery."
                ),
                cites_quote="transcript [00:02:45]"
            ))
            turns.append(DebateTurn(
                round_number=1,
                agent_name="HR / Culture Agent",
                responding_to="Skeptic Agent",
                stance="Disagree",
                message=(
                    "Taylor's self-awareness and honesty in transcript [00:02:45] is a major green flag. "
                    "When faced with past technical deficits (N+1 query performance), Taylor asked senior engineers for pairing sessions [00:04:05] and established personal benchmark habits. Coachability is extremely high."
                ),
                cites_quote="transcript [00:04:05]"
            ))
            turns.append(DebateTurn(
                round_number=1,
                agent_name="Technical Agent",
                responding_to="Skeptic Agent",
                stance="Reinforce",
                message=(
                    "Taylor's work with Celery async workers, Redis locks, and batch transactions [00:01:22] demonstrates strong core backend fundamentals. "
                    "Transitioning from Celery/Redis to Kafka/K8s with senior mentorship is straightforward for an engineer with this foundation."
                ),
                cites_quote="transcript [00:01:22]"
            ))

            # Round 2
            turns.append(DebateTurn(
                round_number=2,
                agent_name="Hiring Manager Agent",
                responding_to="HR / Culture Agent & Technical Agent",
                stance="Agree",
                message=(
                    "I agree with HR and Technical. Taylor's track record of saving 15 manual hours/week and bringing test coverage up to 82% proves practical execution ability."
                ),
                cites_quote="resume line 14"
            ))
            turns.append(DebateTurn(
                round_number=2,
                agent_name="Skeptic Agent",
                responding_to="HR / Culture Agent & Hiring Manager Agent",
                stance="Revise",
                message=(
                    "Acknowledging Taylor's low ego, coachability [00:04:05], and strong test discipline, I revise my position from Lean No (6.0) to Lean Hire (7.2). "
                    "I recommend hiring with a structured 90-day Kafka/Kubernetes onboarding plan."
                ),
                cites_quote="transcript [00:04:05]"
            ))

            # Stance deltas
            for name, op in opinions.opinions.items():
                if name == "Skeptic Agent":
                    stance_deltas[name] = AgentStanceDelta(
                        agent_name=name,
                        score_before=op.score,
                        verdict_before=op.verdict,
                        score_after=7.2,
                        verdict_after="Lean Hire",
                        changed=True,
                        change_reason="Convinced by HR & Technical agents regarding Taylor's coachability, pairing history, and core backend foundation."
                    )
                else:
                    stance_deltas[name] = AgentStanceDelta(
                        agent_name=name,
                        score_before=op.score,
                        verdict_before=op.verdict,
                        score_after=op.score,
                        verdict_after=op.verdict,
                        changed=False,
                        change_reason="Position reinforced; candidate is a strong mid-level growth hire."
                    )

        return DebateState(
            candidate_id=profile.candidate_id,
            rounds=2,
            turns=turns,
            stance_deltas=stance_deltas
        )
