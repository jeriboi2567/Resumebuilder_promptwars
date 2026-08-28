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
    description="Hackathon Ingestion Pipeline for Cargonet AI (02_Job_Description.pdf, Rohan Malhotra, Ananya Iyer) with multi-voice ElevenLabs TTS and Stage 6 comparative ranking.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HACKATHON_DIR = Path(__file__).parent.parent.parent / "hackathon"
FALLBACK_SAMPLE_DIR = Path(__file__).parent.parent / "sample_data"

@app.get("/")
def read_root():
    return {
        "status": "online",
        "version": "2.0.0",
        "service": "Multi-Agent Candidate Evaluation System V2",
        "hackathon_folder_detected": HACKATHON_DIR.exists()
    }

def _load_file_content(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if path.suffix.lower() == ".pdf":
        with open(path, "rb") as f:
            text, _ = PDFDocumentParser.extract_text_from_pdf_bytes(f.read())
            return text
    else:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

@app.get("/api/sample-batch", response_model=BatchPipelineRunResult)
async def run_sample_batch():
    """
    Executes V2 batch evaluation on the actual Hackathon candidate files:
    - Shared Job Description: 02_Job_Description.pdf
    - Candidate A: Rohan Malhotra (03_Resume_A.pdf, 05_Transcript_A.pdf)
    - Candidate B: Ananya Iyer (04_Resume_B.pdf, 06_Transcript_B.pdf)
    Falls back to v2/sample_data if hackathon folder is missing.
    """
    if HACKATHON_DIR.exists():
        jd_path = HACKATHON_DIR / "02_Job_Description.pdf"
        r_a_path = HACKATHON_DIR / "03_Resume_A.pdf"
        t_a_path = HACKATHON_DIR / "05_Transcript_A.pdf"
        r_b_path = HACKATHON_DIR / "04_Resume_B.pdf"
        t_b_path = HACKATHON_DIR / "06_Transcript_B.pdf"
    else:
        jd_path = FALLBACK_SAMPLE_DIR / "01_Job_Description.txt"
        r_a_path = FALLBACK_SAMPLE_DIR / "03_Resume_A.txt"
        t_a_path = FALLBACK_SAMPLE_DIR / "05_Transcript_A.txt"
        r_b_path = FALLBACK_SAMPLE_DIR / "04_Resume_B.txt"
        t_b_path = FALLBACK_SAMPLE_DIR / "06_Transcript_B.txt"

    jd_text = _load_file_content(jd_path)
    ra_text = _load_file_content(r_a_path)
    ta_text = _load_file_content(t_a_path)
    rb_text = _load_file_content(r_b_path)
    tb_text = _load_file_content(t_b_path)

    batch_id = "batch_hackathon_01"
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
    Ingests uploaded PDF/TXT files (Job Description PDF + Resume/Transcript PDF pairs),
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
