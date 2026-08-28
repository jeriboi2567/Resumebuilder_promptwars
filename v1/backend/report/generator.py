from typing import List, Dict, Any
from backend.schemas.models import (
    CandidateProfile, IndependentOpinions, DebateState,
    FinalDecision, CandidateReport
)

class Stage5ReportGenerator:
    """
    Stage 5: Final Report Generator
    Synthesizes all pipeline outputs into a comprehensive per-candidate report,
    available as structured UI data and exportable Markdown.
    """

    @staticmethod
    def generate_report(
        profile: CandidateProfile,
        opinions: IndependentOpinions,
        debate: DebateState,
        decision: FinalDecision
    ) -> CandidateReport:
        # Build Strengths with verified quotes
        strengths: List[Dict[str, str]] = []
        for name, op in opinions.opinions.items():
            if op.score >= 7.0:
                for q in op.supporting_quotes:
                    if q.verified:
                        strengths.append({
                            "quote": q.quote,
                            "source": q.source,
                            "agent": name,
                            "explanation": op.reasoning[:120] + "..."
                        })

        # Build Concerns / Red Flags with quotes
        concerns: List[Dict[str, str]] = []
        for name, op in opinions.opinions.items():
            if op.score <= 6.5 or name == "Skeptic Agent":
                for q in op.supporting_quotes:
                    concerns.append({
                        "quote": q.quote,
                        "source": q.source,
                        "agent": name,
                        "explanation": op.reasoning[:120] + "..."
                    })

        # Agent-by-agent initial vs final summary
        agent_summaries: List[Dict[str, Any]] = []
        for name, op in opinions.opinions.items():
            delta = debate.stance_deltas.get(name)
            agent_summaries.append({
                "agent_name": name,
                "initial_score": op.score,
                "initial_verdict": op.verdict,
                "final_score": delta.score_after if delta else op.score,
                "final_verdict": delta.verdict_after if delta else op.verdict,
                "changed": delta.changed if delta else False,
                "change_reason": delta.change_reason if delta else "Unchanged"
            })

        # Debate highlights (up to 4 key turns)
        debate_highlights = debate.turns[:4]

        # Markdown Report Generation
        md_lines = [
            f"# Candidate Evaluation Report: {profile.candidate_name}",
            f"**Applied Role:** {profile.role_applied} ({profile.seniority_level})  ",
            f"**Final Recommendation:** `{decision.recommendation}` | **Confidence Level:** `{int(decision.confidence * 100)}%`",
            "",
            "---",
            "",
            "## 1. Executive Summary & Rationale",
            decision.decision_rationale,
            "",
            "---",
            "",
            "## 2. Agent Deliberation Summary",
            "| Agent Persona | Initial Verdict (Score) | Final Verdict (Score) | Position Changed? | Key Driver |",
            "|---|---|---|---|---|",
        ]

        for summ in agent_summaries:
            chg = "Yes" if summ["changed"] else "No"
            md_lines.append(
                f"| {summ['agent_name']} | {summ['initial_verdict']} ({summ['initial_score']}) | {summ['final_verdict']} ({summ['final_score']}) | {chg} | {summ['change_reason']} |"
            )

        md_lines.extend([
            "",
            "---",
            "",
            "## 3. Verified Candidate Strengths",
        ])
        for st in strengths[:4]:
            md_lines.append(f"- **[{st['agent']}]** *\"{st['quote']}\"* ({st['source']})")

        md_lines.extend([
            "",
            "---",
            "",
            "## 4. Key Concerns & Red Flags",
        ])
        for cn in concerns[:4]:
            md_lines.append(f"- **[{cn['agent']}]** *\"{cn['quote']}\"* ({cn['source']})")

        if decision.unresolved_disagreements:
            md_lines.extend([
                "",
                "---",
                "",
                "## 5. Unresolved Disagreements",
            ])
            for ud in decision.unresolved_disagreements:
                md_lines.append(f"- ⚠️ {ud}")

        md_lines.extend([
            "",
            "---",
            "",
            "## 6. Debate Highlights",
        ])
        for turn in debate_highlights:
            md_lines.append(
                f"**Round {turn.round_number} - {turn.agent_name}** (responding to *{turn.responding_to}*) [{turn.stance}]:\n"
                f"> \"{turn.message}\"\n"
            )

        markdown_content = "\n".join(md_lines)

        return CandidateReport(
            candidate_id=profile.candidate_id,
            candidate_name=profile.candidate_name,
            final_recommendation=decision.recommendation,
            confidence=decision.confidence,
            strengths=strengths,
            concerns=concerns,
            agent_summaries=agent_summaries,
            unresolved_disagreements=decision.unresolved_disagreements,
            debate_highlights=debate_highlights,
            markdown_content=markdown_content
        )
