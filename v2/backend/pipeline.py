import uuid
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Tuple
from backend.schemas.models import (
    JobDescription, CandidateProfile, PipelineRunResultV2,
    BatchPipelineRunResult, Stage6ComparativeRanking
)
from backend.pdf_parser.parser import PDFDocumentParser
from backend.profile_builder.builder import CandidateProfileBuilderV2
from backend.agents.runner import run_stage2_independent_opinions_v2
from backend.debate.orchestrator import Stage3DebateOrchestratorV2
from backend.decision.synthesizer import Stage4DecisionSynthesizerV2
from backend.report.generator import Stage5ReportGeneratorV2
from backend.comparison.evaluator import Stage6ComparativeEvaluator
from backend.tts.elevenlabs_service import ElevenLabsTTSService
from backend.storage.repository import RunStorageRepositoryV2

class MultiAgentPipelineOrchestratorV2:
    @classmethod
    async def run_single_candidate(
        cls,
        candidate_id: str,
        resume_text: str,
        transcript_text: str,
        jd: JobDescription
    ) -> PipelineRunResultV2:
        run_id = f"run_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now(timezone.utc).isoformat()

        # Stage 1: Candidate Profile Builder
        profile = CandidateProfileBuilderV2.build_profile(candidate_id, resume_text, transcript_text)

        # Stage 2: Isolated Opinions (Parallel)
        opinions = await run_stage2_independent_opinions_v2(profile, jd)

        # Stage 3: Multi-Turn Structured Debate
        debate = Stage3DebateOrchestratorV2.run_debate(profile, jd, opinions)

        # Stage 4: Judge Decision Synthesizer
        decision = Stage4DecisionSynthesizerV2.synthesize_decision(profile, jd, opinions, debate)

        # Stage 5: Final Report Generator (with Insufficient Evidence section)
        report = Stage5ReportGeneratorV2.generate_report(profile, jd, opinions, debate, decision)

        # ElevenLabs Voice Debate Audio Synthesis
        audio_url = await ElevenLabsTTSService.synthesize_debate_audio(run_id, debate.turns)

        return PipelineRunResultV2(
            run_id=run_id,
            timestamp=timestamp,
            profile=profile,
            independent_opinions=opinions,
            debate_state=debate,
            final_decision=decision,
            report=report,
            audio_url=audio_url
        )

    @classmethod
    async def run_batch(
        cls,
        batch_id: str,
        jd_text: str,
        candidate_pairs: List[Tuple[str, str, str]]  # (cand_id, resume_text, transcript_text)
    ) -> BatchPipelineRunResult:
        timestamp = datetime.now(timezone.utc).isoformat()

        # Parse Job Description
        jd = PDFDocumentParser.parse_job_description(jd_text)

        # Run individual candidate pipelines in parallel with strict per-candidate isolation
        cand_results: List[PipelineRunResultV2] = await asyncio.gather(
            *(
                cls.run_single_candidate(cand_id, r_text, t_text, jd)
                for cand_id, r_text, t_text in candidate_pairs
            )
        )

        cand_map: Dict[str, PipelineRunResultV2] = {
            res.profile.candidate_id: res for res in cand_results
        }

        # Stage 6: Comparative Ranking Engine
        stage6_comparison = Stage6ComparativeEvaluator.evaluate_batch(
            batch_id=batch_id,
            jd=jd,
            candidate_results=cand_map
        )

        batch_result = BatchPipelineRunResult(
            batch_id=batch_id,
            timestamp=timestamp,
            job_description=jd,
            candidate_results=cand_map,
            stage6_comparison=stage6_comparison
        )

        # Persist batch run to storage
        RunStorageRepositoryV2.save_batch_run(batch_result)

        return batch_result
