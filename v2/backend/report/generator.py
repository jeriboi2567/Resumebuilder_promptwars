from typing import List, Dict, Any
from backend.schemas.models import (
    CandidateProfile, JobDescription, IndependentOpinionsV2, DebateState,
    FinalDecision, CandidateReportV2
)

class Stage5ReportGeneratorV2:
    @staticmethod
    def generate_report(
        profile: CandidateProfile,
        jd: JobDescription,
        opinions: IndependentOpinionsV2,
        debate: DebateState,
        decision: FinalDecision
    ) -> CandidateReportV2:
        strengths: List[Dict[str, str]] = []
        for name, op in opinions.opinions.items():
            if op.overall_score and op.overall_score >= 7.0:
                for q in op.supporting_quotes:
                    if q.verified:
                        strengths.append({
                            "quote": q.quote,
                            "source": q.source,
                            "agent": name,
                            "explanation": op.reasoning[:120] + "..."
                        })

        concerns: List[Dict[str, str]] = []
        for name, op in opinions.opinions.items():
            if (op.overall_score and op.overall_score <= 6.5) or name == "Skeptic Agent":
                for q in op.supporting_quotes:
                    concerns.append({
                        "quote": q.quote,
                        "source": q.source,
                        "agent": name,
                        "explanation": op.reasoning[:120] + "..."
                    })

        agent_summaries: List[Dict[str, Any]] = []
        for name, op in opinions.opinions.items():
            delta = debate.stance_deltas.get(name)
            agent_summaries.append({
                "agent_name": name,
                "initial_score": op.overall_score or 0.0,
                "initial_verdict": op.verdict,
                "final_score": delta.score_after if delta and delta.score_after is not None else (op.overall_score or 0.0),
                "final_verdict": delta.verdict_after if delta else op.verdict,
                "changed": delta.changed if delta else False,
                "change_reason": delta.change_reason if delta else "Unchanged"
            })

        debate_highlights = debate.turns[:4]

        # Markdown Generation with explicit Insufficient Evidence section
        md_lines = [
            f"# Candidate Evaluation Report: {profile.candidate_name}",
            f"**Target Role:** {jd.title} ({profile.seniority_level})  ",
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

        # Explicit Section B: Not Assessed / Insufficient Evidence
        md_lines.extend([
            "",
            "---",
            "",
            "## 5. Not Assessed / Insufficient Evidence (Explicit Rule)",
            "The following evaluation dimensions contained no source quotes in the candidate profile/transcript and were not scored to prevent guesswork:",
        ])
        if decision.not_assessed_dimensions:
            for na in decision.not_assessed_dimensions:
                md_lines.append(f"- ❓ **[{na['agent']}] {na['dimension']}**: {na['reason']}")
        else:
            md_lines.append("- *All JD evaluation dimensions had sufficient source evidence.*")

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

        return CandidateReportV2(
            candidate_id=profile.candidate_id,
            candidate_name=profile.candidate_name,
            final_recommendation=decision.recommendation,
            confidence=decision.confidence,
            strengths=strengths,
            concerns=concerns,
            not_assessed_dimensions=decision.not_assessed_dimensions,
            agent_summaries=agent_summaries,
            unresolved_disagreements=decision.unresolved_disagreements,
            debate_highlights=debate_highlights,
            markdown_content=markdown_content
        )
