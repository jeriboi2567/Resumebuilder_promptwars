import os
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.pipeline import MultiAgentPipelineOrchestratorV2
from backend.schemas.models import BatchPipelineRunResult, PipelineRunResultV2
from backend.storage.repository import RunStorageRepositoryV2
from backend.pdf_parser.parser import PDFDocumentParser

app = FastAPI(
    title="Multi-Agent Candidate Evaluation System V2 API",
    description="Multi-candidate PDF/JD ingestion pipeline, insufficient-evidence validation, ElevenLabs TTS audio narration, and Stage 6 comparative ranking.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SAMPLE_DATA_DIR = Path(__file__).parent.parent / "sample_data"

@app.get("/")
def read_root():
    return {"status": "online", "version": "2.0.0", "service": "Multi-Agent Candidate Evaluation System V2"}

@app.get("/api/sample-batch", response_model=BatchPipelineRunResult)
async def run_sample_batch():
    """
    Executes V2 batch evaluation on sample candidates (Candidate A: Alex Rivera, Candidate B: Jordan Lee)
    with 01_Job_Description.txt.
    """
    jd_path = SAMPLE_DATA_DIR / "01_Job_Description.txt"
    r_a_path = SAMPLE_DATA_DIR / "03_Resume_A.txt"
    t_a_path = SAMPLE_DATA_DIR / "05_Transcript_A.txt"
    r_b_path = SAMPLE_DATA_DIR / "04_Resume_B.txt"
    t_b_path = SAMPLE_DATA_DIR / "06_Transcript_B.txt"

    with open(jd_path, "r", encoding="utf-8") as f:
        jd_text = f.read()
    with open(r_a_path, "r", encoding="utf-8") as f:
        ra_text = f.read()
    with open(t_a_path, "r", encoding="utf-8") as f:
        ta_text = f.read()
    with open(r_b_path, "r", encoding="utf-8") as f:
        rb_text = f.read()
    with open(t_b_path, "r", encoding="utf-8") as f:
        tb_text = f.read()

    batch_id = "batch_sample_01"
    candidate_pairs = [
        ("cand_A", ra_text, ta_text),
        ("cand_B", rb_text, tb_text)
    ]

    result = await MultiAgentPipelineOrchestratorV2.run_batch(
        batch_id=batch_id,
        jd_text=jd_text,
        candidate_pairs=candidate_pairs
    )
    return result

@app.post("/api/evaluate-batch", response_model=BatchPipelineRunResult)
async def evaluate_batch_files(
    jd_file: UploadFile = File(...),
    resume_files: List[UploadFile] = File(...),
    transcript_files: List[UploadFile] = File(...)
):
    """
    Ingests real uploaded PDF files (01_Job_Description.pdf + Resume/Transcript PDF pairs),
    executes individual 5-stage candidate pipelines in parallel, and runs Stage 6 comparative ranking.
    """
    jd_bytes = await jd_file.read()
    jd_text, _ = PDFDocumentParser.extract_text_from_pdf_bytes(jd_bytes)

    if len(resume_files) != len(transcript_files):
        raise HTTPException(status_code=400, detail="Mismatched number of resume and transcript files.")

    candidate_pairs = []
    for idx in range(len(resume_files)):
        r_bytes = await resume_files[idx].read()
        t_bytes = await transcript_files[idx].read()
        
        r_text, _ = PDFDocumentParser.extract_text_from_pdf_bytes(r_bytes)
        t_text, _ = PDFDocumentParser.extract_text_from_pdf_bytes(t_bytes)
        
        cand_id = f"cand_{idx+1}"
        candidate_pairs.append((cand_id, r_text, t_text))

    batch_id = f"batch_{os.urandom(4).hex()}"
    result = await MultiAgentPipelineOrchestratorV2.run_batch(
        batch_id=batch_id,
        jd_text=jd_text,
        candidate_pairs=candidate_pairs
    )
    return result

@app.get("/api/audio/{run_id}")
def get_audio_file(run_id: str):
    """
    Serves ElevenLabs generated debate audio file.
    """
    audio_path = Path(__file__).parent / "storage" / "audio" / f"{run_id}.mp3"
    if not audio_path.exists():
        # Fallback to run_id without extension if already formatted
        audio_path = Path(__file__).parent / "storage" / "audio" / run_id
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found.")
    return FileResponse(audio_path, media_type="audio/mpeg")

@app.get("/api/runs")
def list_runs():
    return RunStorageRepositoryV2.list_batch_runs()

@app.get("/api/runs/{batch_id}", response_model=BatchPipelineRunResult)
def get_batch_run_details(batch_id: str):
    run = RunStorageRepositoryV2.get_batch_run(batch_id)
    if not run:
        raise HTTPException(status_code=404, detail="Batch run not found.")
    return run
