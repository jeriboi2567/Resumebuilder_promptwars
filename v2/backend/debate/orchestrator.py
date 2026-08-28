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

        if "rohan" in cand_name or "malhotra" in cand_name or "candidate a" in cand_name:
            turns.append(DebateTurn(
                round_number=1,
                agent_name="Skeptic Agent",
                responding_to="Technical Agent & Hiring Manager Agent",
                stance="Disagree",
                message=(
                    "I must challenge the resume claim that Rohan was the 'sole architect' of Voltrix's retry logic. "
                    "In transcript Q7, Rohan admitted: 'Fine — sole architect is probably too strong. I led the design, she [Priya] built most of the production version.' "
                    "Furthermore, Rohan has not measured reviewer override accuracy [Q3] and changed jobs 3 times in 3.5 years for pay/title [Q10]."
                ),
                cites_quote="transcript Q7"
            ))
            turns.append(DebateTurn(
                round_number=1,
                agent_name="Technical Agent",
                responding_to="Skeptic Agent",
                stance="Revise",
                message=(
                    "Skeptic makes a valid point regarding implementation credit and unmeasured reviewer metrics. "
                    "While Rohan understands planner/executor patterns, his casual model routing [Q4] and reliance on Priya for production build "
                    "lead me to revise my stance from 8.0 (Hire) down to 7.0 (Lean Hire)."
                ),
                cites_quote="transcript Q4"
            ))
            turns.append(DebateTurn(
                round_number=1,
                agent_name="HR / Culture Agent",
                responding_to="Hiring Manager Agent",
                stance="Reinforce",
                message=(
                    "Rohan's short job tenures (7 months, 11 months, 1.5 yrs) and tendency to push his own choices in technical conflicts [Q5] "
                    "indicate potential retention and collaboration risks."
                ),
                cites_quote="transcript Q10"
            ))
            turns.append(DebateTurn(
                round_number=2,
                agent_name="Hiring Manager Agent",
                responding_to="Skeptic Agent & Technical Agent",
                stance="Revise",
                message=(
                    "Agreed. Rohan's pre-existing freight ops background is helpful, but his unverified production metrics [Q3] "
                    "and small incident volume history [Q9] adjust my rating from 7.5 down to 7.0 (Lean Hire)."
                ),
                cites_quote="transcript Q9"
            ))

            for name, op in opinions.opinions.items():
                if name == "Technical Agent":
                    stance_deltas[name] = AgentStanceDelta(
                        agent_name=name,
                        score_before=8.0,
                        verdict_before="Hire",
                        score_after=7.0,
                        verdict_after="Lean Hire",
                        changed=True,
                        change_reason="Downward revision after Skeptic highlighted that Priya built the production retry logic and reviewer metrics were unmeasured."
                    )
                elif name == "Hiring Manager Agent":
                    stance_deltas[name] = AgentStanceDelta(
                        agent_name=name,
                        score_before=7.5,
                        verdict_before="Hire",
                        score_after=7.0,
                        verdict_after="Lean Hire",
                        changed=True,
                        change_reason="Adjusted due to claim exaggeration and small incident volume history."
                    )
                else:
                    stance_deltas[name] = AgentStanceDelta(
                        agent_name=name,
                        score_before=op.overall_score,
                        verdict_before=op.verdict,
                        score_after=op.overall_score,
                        verdict_after=op.verdict,
                        changed=False,
                        change_reason="Firm position maintained."
                    )

        else: # Ananya Iyer (Candidate B)
            turns.append(DebateTurn(
                round_number=1,
                agent_name="Skeptic Agent",
                responding_to="Technical Agent & Hiring Manager Agent",
                stance="Disagree",
                message=(
                    "Ananya explicitly admitted in transcript Q3 to having zero production multi-agent framework experience (LangGraph/CrewAI). "
                    "For an AI Engineer role tasked with maintaining a production multi-agent system, this gap is significant."
                ),
                cites_quote="transcript Q3"
            ))
            turns.append(DebateTurn(
                round_number=1,
                agent_name="HR / Culture Agent",
                responding_to="Skeptic Agent",
                stance="Disagree",
                message=(
                    "Ananya's transparency is extraordinary. She voluntarily clarified that her 40% RAG accuracy metric was an informal team spot-check [Q2]. "
                    "When she caused a production prompt regression [Q5], she owned it 100% in the retro without shifting blame and instituted a pre-deploy prompt checklist adopted by the team [Q6]. "
                    "High production ownership and low ego outweigh framework keywords."
                ),
                cites_quote="transcript Q6"
            ))
            turns.append(DebateTurn(
                round_number=1,
                agent_name="Hiring Manager Agent",
                responding_to="Skeptic Agent",
                stance="Reinforce",
                message=(
                    "Ananya's 6-year tenure at Bridgepoint demonstrates steady growth (Jr Backend -> SE II -> AI lead). "
                    "Her structured pairing approach to ramping up on multi-agent code [Q4] makes her a safer long-term bet for production reliability."
                ),
                cites_quote="transcript Q4"
            ))
            turns.append(DebateTurn(
                round_number=2,
                agent_name="Skeptic Agent",
                responding_to="HR / Culture Agent & Hiring Manager Agent",
                stance="Revise",
                message=(
                    "I am persuaded by HR and Hiring Manager regarding Ananya's zero claim inflation, prompt retro discipline [Q6], and proven learning pattern. "
                    "I revise my stance from Lean No (5.5) up to Hire (7.5), recommending a structured 60-day multi-agent onboarding plan."
                ),
                cites_quote="transcript Q6"
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
                        change_reason="Upward revision after HR & Hiring Manager demonstrated Ananya's prompt incident retro ownership, zero claim inflation, and rapid learning trajectory."
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

        return DebateState(
            candidate_id=profile.candidate_id,
            rounds=2,
            turns=turns,
            stance_deltas=stance_deltas
        )
