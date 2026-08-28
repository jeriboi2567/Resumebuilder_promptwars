# Multi-Agent Candidate Evaluation System (Promptwars)

An evidentiary multi-agent job candidate evaluation platform that ingests candidate resumes, interview transcripts, and job descriptions, runs **four architecturally isolated AI agent personas**, orchestrates a **multi-turn structured debate**, synthesizes **ElevenLabs multi-voice audio narration**, and converges on a **weighted hiring decision** and **Stage 6 comparative ranking**.

---

## 📁 Repository Structure

```
/
├── README.md                          # Repository Documentation & Quickstart
├── DEPLOYMENT.md                      # Remote Tunnel & Cloud Deployment Guide
├── hackathon/                         # Official Hackathon PDF Dataset & Problem Statement
├── .gitignore                         # Global Git Ignore rules
│
├── v1/                                # Version 1 Core Release (5-Stage Pipeline)
├── v2/                                # Version 2 Hackathon Release (PDF Ingestion, Insufficient Evidence & Stage 6)
└── v3/                                # Version 3 General-Purpose Platform (Arbitrary Employers/Roles/Candidates)
    ├── backend/                       # FastAPI V3 General-Purpose Server & Persistence
    │   ├── pdf_parser/                # Dynamic PDF & Text Extraction Engine
    │   ├── profile_builder/           # Dynamic Candidate Profile Builder (Arbitrary Resumes/Transcripts)
    │   ├── agents/                    # Isolated Agents with Dynamic Insufficient Evidence Rules
    │   ├── comparison/                # Dynamic Stage 6 Side-by-Side Comparative Ranking Engine
    │   ├── storage/                   # Persistent Hiring Roles & Accumulated Candidate Data
    │   └── tests/                     # Pytest V3 Test Suite
    ├── frontend/                      # React V3 Employer Dashboard & Role Management
    ├── pytest.ini                     # Pytest Path configuration
    └── .env                           # ElevenLabs API Key Storage (Ignored by git)
```

---

## 🚀 Version 3 (v3) General-Purpose Employer Platform

1. **Arbitrary Employer Job Roles**:
   - Create custom Hiring Roles for any employer/job title by uploading any custom Job Description PDF or TXT file (`POST /api/roles`).
2. **Arbitrary Candidate Ingestion**:
   - Upload Resume + Transcript PDF/TXT pairs for any candidate of choice (any name, role, or background) with zero hardcoded code changes (`POST /api/roles/{role_id}/candidates`).
3. **Candidate Accumulation & Stage 6 Comparison**:
   - Evaluates each new candidate through the full 5-stage pipeline and automatically appends them to the Hiring Role's Stage 6 side-by-side comparative ranking table.
4. **Preserved V2 Core Mechanics**:
   - Retains 100% of V2 core features: Candidate Profile Builder, 4 Isolated Agent Personas, Section B No-Guessing Rule (`insufficient_evidence: true`), Multi-Turn Debate Transcript, Non-Averaged Evidence-Weighted Judge Synthesis, and ElevenLabs Multi-Voice Debate Narration.

---

## ⚙️ Running Version 3 (v3) Locally

### 1. Run the V3 Backend API Server
```powershell
cd v3
$env:PYTHONPATH="."
.venv\Scripts\uvicorn backend.main:app --port 8000 --reload
```
- API Documentation available at: `http://localhost:8000/docs`

### 2. Run V3 Pytest Suite
```powershell
cd v3
uv run --with python-multipart --with fastapi --with pydantic --with pytest --with pytest-asyncio --with httpx --with pdfplumber --with pymupdf --with elevenlabs --with python-dotenv pytest backend/tests -v
```

### 3. Run the V3 Frontend Dev Server
```powershell
cd v3/frontend
npm run dev
```
- UI available at: `http://localhost:3000`

---

## ⚙️ Running Version 2 (v2) Hackathon Release
```powershell
cd v2
$env:PYTHONPATH="."
.venv\Scripts\uvicorn backend.main:app --port 8000 --reload
```
