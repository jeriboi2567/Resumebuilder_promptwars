# Multi-Agent Candidate Evaluation System (Promptwars)

An evidentiary multi-agent job candidate evaluation platform that ingests candidate resumes, interview transcripts, and job descriptions, runs **four architecturally isolated AI agent personas**, orchestrates a **multi-turn structured debate**, synthesizes **ElevenLabs multi-voice audio narration**, and converges on a **weighted hiring decision** and **Stage 6 comparative ranking**.

---

## 📁 Repository Structure

```
/
├── README.md                          # Repository Documentation & Quickstart
├── DEPLOYMENT.md                      # Remote Tunnel & Cloud Deployment Guide
├── promptwars-v2-addendum-prompt.md   # V2 Prompt Specification & Addendum
├── .gitignore                         # Global Git Ignore rules
│
├── v1/                                # Version 1 Core Release (5-Stage Pipeline)
│   ├── backend/                       # FastAPI Backend & Orchestrator
│   ├── frontend/                      # React UI & Web Speech Audio Player
│   ├── sample_data/                   # Candidate Resume/Transcript Datasets
│   └── projectfile.md                 # V1 Prompt Specification
│
└── v2/                                # Version 2 Release (PDF/JD Ingestion & Stage 6)
    ├── backend/                       # FastAPI V2 Server, PDF Parser, ElevenLabs TTS
    │   ├── pdf_parser/                # PDF Text & Location Extractor (pdfplumber/fitz)
    │   ├── tts/                       # ElevenLabs Voice Debate Audio Generator
    │   ├── agents/                    # Isolated Agents with Insufficient Evidence Rules
    │   ├── comparison/                # Stage 6 Side-by-Side Comparative Ranking Engine
    │   └── tests/                     # Pytest V2 Test Suite
    ├── frontend/                      # React V2 UI with Stage 6 Dashboard & Audio Player
    ├── sample_data/                   # 01_Job_Description.txt & Candidate PDF Datasets
    └── .env                           # ElevenLabs API Key Storage (Ignored by git)
```

---

## 🚀 Version 2 (v2) Features & Enhancements

1. **PDF & Job Description (JD) Ingestion**:
   - Ingests `01_Job_Description.pdf` alongside candidate resumes and transcripts using `pdfplumber` / `PyMuPDF`.
   - Threads JD requirements directly into Technical & Hiring Manager Agent prompts for requirement-specific scoring.
2. **Section B: Insufficient-Evidence Rule (`insufficient_evidence: true`)**:
   - If an evaluation dimension lacks supporting quotes in the candidate profile/transcript, the system **forces `insufficient_evidence: true` with a reason string**, preventing fake scores (e.g. middling 5/10 guesses).
   - Renders an explicit **"Not Assessed / Insufficient Evidence"** section in Stage 5 reports.
3. **ElevenLabs Multi-Voice Audio Debate Narration**:
   - Synthesizes Stage 3 multi-turn debate exchanges into audio tracks using 4 distinct ElevenLabs persona voices (Adam, Rachel, Arnold, Sam).
4. **Stage 6: Comparative Ranking Engine & Side-by-Side Dashboard**:
   - Runs concurrently for $N$ candidates with strict per-candidate isolation.
   - Executes Stage 6 after all candidate individual pipelines complete, rendering an evidence-weighted comparative ranking matrix, key differentiators, and shared JD requirement compliance table.
5. **Batch PDF Upload Modal**:
   - Allows users to drag-and-drop 1 shared Job Description PDF + $N$ candidate PDF pairs directly in the UI.

---

## ⚙️ Running Version 2 (v2) Locally

### 1. Run the V2 Backend API Server
```powershell
cd v2
$env:PYTHONPATH="."
.venv\Scripts\uvicorn backend.main:app --port 8000 --reload
```
- API Documentation available at: `http://localhost:8000/docs`

### 2. Run V2 Pytest Suite
```powershell
cd v2
$env:PYTHONPATH="."; uv run --with fastapi --with pydantic --with pytest --with pytest-asyncio --with httpx --with pdfplumber --with pymupdf --with elevenlabs --with python-dotenv pytest backend/tests -v
```

### 3. Run the V2 Frontend Dev Server
```powershell
cd v2/frontend
npm run dev
```
- UI available at: `http://localhost:3000`

---

## ⚙️ Running Version 1 (v1) Locally

### 1. Run V1 Backend
```powershell
cd v1
$env:PYTHONPATH="."
.venv\Scripts\uvicorn backend.main:app --port 8000 --reload
```

### 2. Run V1 Frontend
```powershell
cd v1/frontend
npm run dev
```
