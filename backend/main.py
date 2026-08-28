import os
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.pipeline import MultiAgentPipelineOrchestrator
from backend.storage.repository import RunStorageRepository
from backend.schemas.models import PipelineRunResult

app = FastAPI(
    title="Multi-Agent Candidate Evaluation API",
    description="Pipeline orchestrator for candidate profile extraction, isolated agent opinions, multi-round debate, decision synthesis, and report generation.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SAMPLE_DATA_DIR = Path(__file__).parent.parent / "sample_data"

class EvaluateRequest(BaseModel):
    candidate_id: Optional[str] = "cand_1"
    resume_text: Optional[str] = None
    transcript_text: Optional[str] = None

@app.get("/")
def read_root():
    return {"status": "online", "service": "Multi-Agent Candidate Evaluation System API"}

@app.get("/api/candidates")
def list_sample_candidates():
    """
    Returns list of sample candidates available in /sample_data.
    """
    candidates = [
        {"id": "cand_1", "name": "Alex Rivera", "role": "Senior Full-Stack Engineer", "resume_file": "resume_1.txt", "transcript_file": "transcript_1.txt"},
        {"id": "cand_2", "name": "Jordan Lee", "role": "Principal AI/ML Architect", "resume_file": "resume_2.txt", "transcript_file": "transcript_2.txt"},
        {"id": "cand_3", "name": "Taylor Morgan", "role": "Backend Developer", "resume_file": "resume_3.txt", "transcript_file": "transcript_3.txt"}
    ]
    return candidates

@app.get("/api/candidates/{cand_id}")
def get_sample_candidate(cand_id: str):
    num_map = {"cand_1": "1", "cand_2": "2", "cand_3": "3"}
    num = num_map.get(cand_id, "1")
    
    resume_path = SAMPLE_DATA_DIR / f"resume_{num}.txt"
    transcript_path = SAMPLE_DATA_DIR / f"transcript_{num}.txt"
    
    if not resume_path.exists() or not transcript_path.exists():
        raise HTTPException(status_code=404, detail="Candidate sample files not found.")
        
    with open(resume_path, "r", encoding="utf-8") as r_f:
        resume_text = r_f.read()
    with open(transcript_path, "r", encoding="utf-8") as t_f:
        transcript_text = t_f.read()
        
    return {
        "candidate_id": cand_id,
        "resume_text": resume_text,
        "transcript_text": transcript_text
    }

@app.post("/api/evaluate", response_model=PipelineRunResult)
async def evaluate_candidate(req: EvaluateRequest):
    """
    Triggers end-to-end multi-agent evaluation pipeline.
    """
    resume_text = req.resume_text
    transcript_text = req.transcript_text
    
    if not resume_text or not transcript_text:
        # Load sample candidate text if not directly provided
        num_map = {"cand_1": "1", "cand_2": "2", "cand_3": "3"}
        num = num_map.get(req.candidate_id, "1")
        resume_path = SAMPLE_DATA_DIR / f"resume_{num}.txt"
        transcript_path = SAMPLE_DATA_DIR / f"transcript_{num}.txt"
        
        if resume_path.exists() and transcript_path.exists():
            with open(resume_path, "r", encoding="utf-8") as r_f:
                resume_text = r_f.read()
            with open(transcript_path, "r", encoding="utf-8") as t_f:
                transcript_text = t_f.read()
        else:
            raise HTTPException(status_code=400, detail="Missing resume_text or transcript_text.")

    result = await MultiAgentPipelineOrchestrator.run(
        candidate_id=req.candidate_id or "custom",
        resume_text=resume_text,
        transcript_text=transcript_text
    )
    return result

@app.get("/api/runs")
def list_runs():
    return RunStorageRepository.list_runs()

@app.get("/api/runs/{run_id}", response_model=PipelineRunResult)
def get_run_details(run_id: str):
    run = RunStorageRepository.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found.")
    return run
