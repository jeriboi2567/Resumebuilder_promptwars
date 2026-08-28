import uuid
from datetime import datetime, timezone
from backend.schemas.models import PipelineRunResult
from backend.profile_builder.builder import CandidateProfileBuilder
from backend.agents.runner import run_stage2_independent_opinions
from backend.debate.orchestrator import Stage3DebateOrchestrator
from backend.decision.synthesizer import Stage4DecisionSynthesizer
from backend.report.generator import Stage5ReportGenerator
from backend.storage.repository import RunStorageRepository

class MultiAgentPipelineOrchestrator:
    """
    Master Pipeline Orchestrator for Multi-Agent Candidate Evaluation System.
    Sequentially executes:
    Stage 1: Candidate Profile Builder
    Stage 2: Independent Agent Opinions (Parallel, Isolated)
    Stage 3: Structured Multi-Turn Debate
    Stage 4: Final Decision Synthesis ("Judge")
    Stage 5: Final Report Generation & Persistence
    """

    @classmethod
    async def run(
        cls,
        candidate_id: str,
        resume_text: str,
        transcript_text: str
    ) -> PipelineRunResult:
        run_id = f"run_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now(timezone.utc).isoformat()

        # Stage 1: Build Candidate Profile
        profile = CandidateProfileBuilder.build_profile(
            candidate_id=candidate_id,
            resume_text=resume_text,
            transcript_text=transcript_text
        )

        # Stage 2: Execute Isolated Independent Opinions concurrently
        opinions = await run_stage2_independent_opinions(profile)

        # Stage 3: Execute Multi-Turn Structured Debate
        debate = Stage3DebateOrchestrator.run_debate(profile, opinions)

        # Stage 4: Synthesize Final Decision (Judge)
        final_decision = Stage4DecisionSynthesizer.synthesize_decision(
            profile=profile,
            opinions=opinions,
            debate=debate
        )

        # Stage 5: Generate Per-Candidate Report
        report = Stage5ReportGenerator.generate_report(
            profile=profile,
            opinions=opinions,
            debate=debate,
            decision=final_decision
        )

        result = PipelineRunResult(
            run_id=run_id,
            timestamp=timestamp,
            profile=profile,
            independent_opinions=opinions,
            debate_state=debate,
            final_decision=final_decision,
            report=report
        )

        # Persist result to storage repository
        RunStorageRepository.save_run(result)

        return result
