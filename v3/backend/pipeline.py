import uuid
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Tuple
from backend.schemas.models import (
    JobDescription, CandidateProfile, PipelineRunResultV2,
    BatchPipelineRunResult, Stage6ComparativeRanking, HiringRoleV3
)
from backend.pdf_parser.parser import PDFDocumentParser
from backend.profile_builder.builder import CandidateProfileBuilderV2
from backend.agents.runner import run_stage2_independent_opinions_v2
from backend.debate.orchestrator import Stage3DebateOrchestratorV2
from backend.decision.synthesizer import Stage4DecisionSynthesizerV2
from backend.report.generator import Stage5ReportGeneratorV2
from backend.comparison.evaluator import Stage6ComparativeEvaluator
from backend.tts.elevenlabs_service import ElevenLabsTTSService
from backend.storage.repository import RoleStorageRepositoryV3

class MultiAgentPipelineOrchestratorV3:
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

        # Stage 1: Dynamic Candidate Profile Builder
        profile = CandidateProfileBuilderV2.build_profile(candidate_id, resume_text, transcript_text)

        # Stage 2: Dynamic Isolated Persona Opinions (Parallel)
        opinions = await run_stage2_independent_opinions_v2(profile, jd)

        # Stage 3: Dynamic Multi-Turn Debate
        debate = Stage3DebateOrchestratorV2.run_debate(profile, jd, opinions)

        # Stage 4: Dynamic Judge Decision Synthesizer
        decision = Stage4DecisionSynthesizerV2.synthesize_decision(profile, jd, opinions, debate)

        # Stage 5: Final Report Generator
        report = Stage5ReportGeneratorV2.generate_report(profile, jd, opinions, debate, decision)

        # ElevenLabs Multi-Voice Audio Synthesis
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
    async def process_role_candidates(
        cls,
        role_id: str,
        jd_text: str,
        candidate_pairs: List[Tuple[str, str, str]] # (cand_id, resume_text, transcript_text)
    ) -> HiringRoleV3:
        timestamp = datetime.now(timezone.utc).isoformat()

        # Check existing stored role or create new
        existing_role = RoleStorageRepositoryV3.get_role(role_id)
        if existing_role:
            jd = existing_role.job_description
            cand_map = existing_role.candidate_results
            created_at = existing_role.created_at
        else:
            jd = PDFDocumentParser.parse_job_description(jd_text, job_id=role_id)
            cand_map = {}
            created_at = timestamp

        # Process new uploaded candidates in parallel
        new_results: List[PipelineRunResultV2] = await asyncio.gather(
            *(
                cls.run_single_candidate(cand_id, r_text, t_text, jd)
                for cand_id, r_text, t_text in candidate_pairs
            )
        )

        for res in new_results:
            cand_map[res.profile.candidate_id] = res

        # Stage 6: Dynamic Comparative Ranking across ALL accumulated candidates for this role
        stage6_comparison = Stage6ComparativeEvaluator.evaluate_batch(
            batch_id=f"batch_{role_id}",
            jd=jd,
            candidate_results=cand_map
        )

        updated_role = HiringRoleV3(
            role_id=role_id,
            job_description=jd,
            created_at=created_at,
            updated_at=timestamp,
            candidate_results=cand_map,
            stage6_comparison=stage6_comparison
        )

        RoleStorageRepositoryV3.save_role(updated_role)
        return updated_role
