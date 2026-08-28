# Multi-Agent Candidate Evaluation System (Promptwars)

An evidentiary multi-agent job candidate evaluation platform that ingests candidate resumes and interview transcripts, runs **four architecturally isolated AI agent personas**, orchestrates a **multi-turn structured debate**, and converges on a **weighted hiring decision** (not score averaging).

---

## 📁 Repository Structure

```
/
├── README.md                          # Repository Documentation & Quickstart
├── promptwars-v2-addendum-prompt.md   # V2 Prompt Specification & Addendum
├── .gitignore                         # Global Git Ignore rules
│
├── v1/                                # Version 1 Core Release
│   ├── backend/                       # FastAPI Backend & Orchestrator
│   │   ├── profile_builder/           # Stage 1: Profile Extractor & Verifier
│   │   ├── agents/                    # Stage 2: 4 Isolated Agent Personas
│   │   ├── debate/                    # Stage 3: Structured Multi-Turn Debate
│   │   ├── decision/                  # Stage 4: Judge Synthesizer (Weighted)
│   │   ├── report/                    # Stage 5: Final Report Generator
│   │   ├── schemas/                   # Pydantic Output Models
│   │   ├── storage/                   # Per-Run JSON Persistence
│   │   ├── tests/                     # Pytest Stage Unit & Integration Tests
│   │   └── main.py                    # FastAPI REST API Server
│   │
│   ├── frontend/                      # React + TypeScript + Tailwind UI
│   │   ├── src/components/            # Visual Stage Components & Audio Player
│   │   ├── src/App.tsx                # Main Interactive Dashboard
│   │   └── package.json               # Frontend Dependencies & Scripts
│   │
│   ├── sample_data/                   # Realistic Candidate Test Data
│   └── projectfile.md                 # V1 Prompt Specification
│
└── v2/                                # Version 2 Enhanced Release (Upcoming)
    └── ...                            # Batch PDF Upload, JD Threading, Stage 6 Comparison
```

---

## 🚀 Version 1 (v1) Features & Architecture

### 5-Stage Modular Pipeline

1. **Stage 1 — Candidate Profile Builder**: Ingests raw resume and transcript text and extracts a single source-of-truth `CandidateProfile`. Every skill, experience, and claim carries an explicit `SourceCitation` (verbatim substring + location).
2. **Stage 2 — Independent Agent Opinions (Strict Isolation)**: 4 parallel persona calls (**Technical Agent**, **HR / Culture Agent**, **Hiring Manager Agent**, **Skeptic Agent**).
   - *Architectural Enforcement*: Every agent function accepts **only** `CandidateProfile`. Zero cross-agent context is passed at Stage 2.
   - *Quote Verification*: Validates every supporting quote against raw source documents.
3. **Stage 3 — Structured Multi-Turn Debate**:
   - Reveals Stage 2 opinions to all agents.
   - Agents address named peers, state stances (`Agree`, `Disagree`, `Revise`, `Reinforce`), cite quotes, and explain position shifts.
   - Tracks provable position movement (`opinion_before`, `opinion_after`, `changed`, `change_reason`).
4. **Stage 4 — Final Decision Synthesis ("Judge")**:
   - Synthesizes final recommendation (`Strong Hire`, `Hire`, `Lean No`, `No Hire`) using weighted evidence quality and confidence (does **not** average raw scores).
   - Explicitly surfaces unresolved panel disagreements rather than smoothing over them.
5. **Stage 5 — Final Report & Persistence**:
   - Generates auditable Markdown reports and persists full JSON run results in `backend/storage/runs/`.

### Interactive Visual Frontend & Audio TTS
- **Visual Stepper & Pipeline Inspector**: Inspect extracted citations, 4 isolated agent cards, debate thread, judge rationale, and executive report.
- **Multi-Voice Audio Debate Player**: Uses Web Speech API (TTS) with persona pitch modulation to let users listen in on the agents arguing.

---

## ⚙️ Running Version 1 (v1) Locally

### 1. Run the Backend API Server
```powershell
cd v1
.venv\Scripts\activate
uvicorn backend.main:app --port 8000 --reload
```
- API Docs available at: `http://localhost:8000/docs`

### 2. Run Backend Unit & Integration Tests
```powershell
cd v1
$env:PYTHONPATH="."; .venv\Scripts\pytest backend/tests
```

### 3. Run the Frontend Dev Server
```powershell
cd v1/frontend
npm run dev
```
- UI available at: `http://localhost:3000`

---

## 🔮 Version 2 (v2) Addendum Overview

Version 2 extends the platform to support:
- **PDF File Ingestion**: Ingesting `01_Job_Description.pdf`, resumes, and transcripts directly.
- **Job Description Threading**: Evaluating candidate fit directly against JD requirements.
- **Insufficient-Evidence Handling**: Explicit `insufficient_evidence: true` tracking ("No Guessing" rule).
- **Stage 6: Comparative Ranking**: N-candidate batch processing and side-by-side comparison dashboard.
