import os
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.pipeline import MultiAgentPipelineOrchestratorV3
from backend.schemas.models import HiringRoleV3, BatchPipelineRunResult, JobDescription
from backend.storage.repository import RoleStorageRepositoryV3
from backend.pdf_parser.parser import PDFDocumentParser

app = FastAPI(
    title="Multi-Agent Candidate Evaluation System V3 API",
    description="General-purpose evidentiary multi-agent candidate evaluation platform for arbitrary employers, Job Descriptions, and accumulated candidates.",
    version="3.0.0"
)

allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
origins_list = [o.strip() for o in allowed_origins_env.split(",") if o.strip()] if allowed_origins_env != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HACKATHON_DIR = Path(__file__).parent.parent.parent / "hackathon"
FALLBACK_SAMPLE_DIR = Path(__file__).parent.parent.parent / "v2" / "sample_data"

@app.get("/")
def read_root():
    return {
        "status": "online",
        "version": "3.0.0",
        "service": "Multi-Agent Candidate Evaluation Platform V3 (General Purpose)",
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

@app.get("/api/sample-batch")
async def run_sample_batch():
    """
    Executes V3 evaluation on hackathon candidate files for quick demo/verification.
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

    role_id = "role_cargonet_ai"
    candidate_pairs = [
        ("cand_A", ra_text, ta_text),
        ("cand_B", rb_text, tb_text)
    ]

    role = await MultiAgentPipelineOrchestratorV3.process_role_candidates(
        role_id=role_id,
        jd_text=jd_text,
        candidate_pairs=candidate_pairs
    )

    # Format into BatchPipelineRunResult compatibility response
    return BatchPipelineRunResult(
        batch_id=f"batch_{role_id}",
        timestamp=role.updated_at,
        job_description=role.job_description,
        candidate_results=role.candidate_results,
        stage6_comparison=role.stage6_comparison
    )

@app.post("/api/roles", response_model=HiringRoleV3)
async def create_hiring_role(
    jd_file: UploadFile = File(...)
):
    """
    Creates a new general-purpose Hiring Role from an employer's uploaded Job Description (PDF/TXT).
    """
    jd_bytes = await jd_file.read()
    is_valid, msg = PDFDocumentParser.validate_file_input(jd_file.filename, jd_bytes)
    if not is_valid:
        raise HTTPException(status_code=400, detail=msg)

    jd_text, _ = PDFDocumentParser.extract_text_from_pdf_bytes(jd_bytes)

    role_id = f"role_{os.urandom(4).hex()}"
    role = await MultiAgentPipelineOrchestratorV3.process_role_candidates(
        role_id=role_id,
        jd_text=jd_text,
        candidate_pairs=[]
    )
    return role

@app.post("/api/roles/{role_id}/candidates", response_model=HiringRoleV3)
async def add_candidates_to_role(
    role_id: str,
    resume_files: List[UploadFile] = File(...),
    transcript_files: List[UploadFile] = File(...)
):
    """
    Uploads dynamic Resume + Transcript PDF/TXT pairs for any candidate of choice,
    runs the 5-stage pipeline, and updates Stage 6 comparative ranking across all accumulated candidates for that role!
    """
    existing_role = RoleStorageRepositoryV3.get_role(role_id)
    if not existing_role:
        raise HTTPException(status_code=404, detail="Hiring role not found. Create a role first.")

    if len(resume_files) != len(transcript_files):
        raise HTTPException(status_code=400, detail="Mismatched number of resume and transcript files.")

    candidate_pairs = []
    for idx in range(len(resume_files)):
        r_file = resume_files[idx]
        t_file = transcript_files[idx]
        
        r_bytes = await r_file.read()
        t_bytes = await t_file.read()
        
        r_valid, r_msg = PDFDocumentParser.validate_file_input(r_file.filename, r_bytes)
        if not r_valid:
            raise HTTPException(status_code=400, detail=f"Resume #{idx+1} invalid: {r_msg}")

        t_valid, t_msg = PDFDocumentParser.validate_file_input(t_file.filename, t_bytes)
        if not t_valid:
            raise HTTPException(status_code=400, detail=f"Transcript #{idx+1} invalid: {t_msg}")

        r_text, _ = PDFDocumentParser.extract_text_from_pdf_bytes(r_bytes)
        t_text, _ = PDFDocumentParser.extract_text_from_pdf_bytes(t_bytes)
        
        cand_id = f"cand_{os.urandom(3).hex()}"
        candidate_pairs.append((cand_id, r_text, t_text))

    updated_role = await MultiAgentPipelineOrchestratorV3.process_role_candidates(
        role_id=role_id,
        jd_text=existing_role.job_description.raw_text,
        candidate_pairs=candidate_pairs
    )
    return updated_role

@app.get("/api/roles", response_model=List[dict])
def list_roles():
    return RoleStorageRepositoryV3.list_roles()

@app.get("/api/roles/{role_id}", response_model=HiringRoleV3)
def get_role_details(role_id: str):
    role = RoleStorageRepositoryV3.get_role(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Hiring role not found.")
    return role

@app.get("/api/audio/{run_id}")
def get_audio_file(run_id: str):
    audio_path = Path(__file__).parent / "storage" / "audio" / f"{run_id}.mp3"
    if not audio_path.exists():
        audio_path = Path(__file__).parent / "storage" / "audio" / run_id
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found.")
    return FileResponse(audio_path, media_type="audio/mpeg")
