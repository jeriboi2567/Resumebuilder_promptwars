# Deployment Guide: Multi-Agent Candidate Evaluation System

This document provides deployment options for hackathon judges and employers to access the live demo remotely.

---

## Option 1: Local Server + ngrok Tunnel (Recommended for Live Demo)

This option runs the FastAPI backend and Vite React frontend locally on your machine and exposes a single public HTTPS URL using `ngrok`.

### Step 1: Start the Backend API Server
```powershell
# For V3 Platform (General-Purpose Hiring Platform):
cd v3
$env:PYTHONPATH="."
.venv\Scripts\uvicorn backend.main:app --port 8000 --reload
```

### Step 2: Start the Frontend Dev Server
```powershell
# For V3 Frontend:
cd v3/frontend
npm run dev
```
The Vite frontend runs at `http://localhost:3000` and automatically proxies all `/api` REST endpoints to `http://localhost:8000`.

### Step 3: Launch ngrok Tunnel
In a new terminal window, expose port `3000`:
```bash
ngrok http 3000
```

`ngrok` will provide a public URL (e.g., `https://a1b2c3d4.ngrok-free.app`). Employers and judges can open this single URL in any web browser to create custom Hiring Roles (with any uploaded Job Description PDF/TXT), evaluate arbitrary new candidates over time, stream ElevenLabs debate audio, and view Stage 6 comparative rankings across all accumulated candidates.

---

## Option 2: Production Cloud Hosting (Vercel + Render)

### Backend Deployment (Render / Railway)
1. Push this repository to GitHub.
2. Create a new **Web Service** on Render (or Railway).
3. Set the Root Directory to `v3` (or `v2`/`v1`).
4. Set Build Command: `pip install -r backend/requirements.txt`
5. Set Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
6. Add Environment Variable: `ELEVENLABS_API_KEY=sk_b43bc43a...`

### Frontend Deployment (Vercel / Netlify)
1. Create a new project on Vercel.
2. Set Root Directory to `v3/frontend`.
3. Set Framework Preset to **Vite**.
4. Set Build Command: `npm run build`
5. Set Output Directory: `dist`
