import pytest
from backend.profile_builder.builder import CandidateProfileBuilderV2
from backend.pdf_parser.parser import PDFDocumentParser
from backend.agents.technical_agent import TechnicalAgentV2
from backend.agents.hr_culture_agent import HRCultureAgentV2
from backend.agents.hiring_manager_agent import HiringManagerAgentV2
from backend.agents.skeptic_agent import SkepticAgentV2
from backend.agents.runner import run_stage2_independent_opinions_v2
from backend.debate.orchestrator import Stage3DebateOrchestratorV2

@pytest.mark.asyncio
async def test_debate_turn_taking_and_stance_deltas():
    resume = "SAM REED\nFull Stack Developer\n- Built React and Node.js applications."
    transcript = "Interview Transcript - Candidate: Sam Reed\nQ: Walk us through a production challenge.\nA: We had a database connection pool leak and fixed it."
    jd_text = "JOB DESCRIPTION: Full Stack Lead\nRequired Skills: React, Node.js, PostgreSQL"

    profile = CandidateProfileBuilderV2.build_profile("cand_sam", resume, transcript)
    jd = PDFDocumentParser.parse_job_description(jd_text)

    opinions = await run_stage2_independent_opinions_v2(profile, jd)
    debate = Stage3DebateOrchestratorV2.run_debate(profile, jd, opinions)

    assert debate.rounds >= 2
    assert len(debate.turns) >= 2

    # Verify at least one agent directly responds to another
    first_turn = debate.turns[0]
    assert first_turn.agent_name in ["Technical Agent", "Skeptic Agent", "HR / Culture Agent"]
    assert first_turn.responding_to is not None
    assert first_turn.stance in ["Agree", "Disagree", "Revise", "Reinforce"]

    # Verify stance deltas table contains all 4 personas
    assert len(debate.stance_deltas) == 4
    for persona_name in ["Technical Agent", "HR / Culture Agent", "Hiring Manager Agent", "Skeptic Agent"]:
        assert persona_name in debate.stance_deltas
        delta = debate.stance_deltas[persona_name]
        assert delta.verdict_before is not None
        assert delta.verdict_after is not None
