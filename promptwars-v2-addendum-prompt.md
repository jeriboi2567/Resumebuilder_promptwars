# Build Prompt (Addendum): Multi-Candidate Upload, Comparison, and Spec Alignment

This extends the existing Multi-Agent Candidate Evaluation System (Promptwars) to match the
updated hackathon problem statement. Do not rebuild the existing 5-stage pipeline — extend it.

---

## A. Real File Ingestion (replace synthetic sample data)

The system must now work from actual provided files, not just synthetic sample candidates:
- `01_Job_Description.pdf` (shared across all candidates)
- `03_Resume_A.pdf`, `04_Resume_B.pdf`
- `05_Transcript_A.pdf`, `06_Transcript_B.pdf`

### Requirements
- Add a PDF-to-text ingestion step ahead of Stage 1 (Candidate Profile Builder). Use a
  standard PDF text extraction library (e.g., `pdfplumber` or `PyMuPDF`); preserve line
  numbers / approximate positions so `SourceCitation` locations remain meaningful after
  extraction (resume "line 14" should map to something real, not an arbitrary index).
- The **Job Description** is now a first-class input to the pipeline, not just resume +
  transcript. Thread it through to:
  - The **Hiring Manager Agent**, which should evaluate fit against the JD's actual stated
    requirements (not a generic "is this person good" judgment) — cite specific JD
    requirements alongside candidate evidence when scoring fit.
  - Optionally the **Technical Agent**, if the JD specifies required technical skills, so it
    can flag skill gaps directly against what's asked for, not just general competence.
- Keep the existing sample-data pipeline working — add real-file ingestion as an additional
  input path (e.g., an "Upload real files" mode vs. "Use sample data" mode), don't replace one
  with the other.

---

## B. Insufficient-Evidence Handling (new explicit rule)

Per the updated rules: *"If there isn't enough information to judge something, say so — don't
make up a score."* This needs to be a real state in the data model, not just a low score.

### Requirements
- Extend each agent's opinion schema to allow, per evaluation dimension, an
  `insufficient_evidence: true` flag with a `reason` string, in place of a forced numeric
  score for that dimension. Do not let the LLM default to guessing a middling score (e.g., a
  "5/10") when the source material simply doesn't address a dimension — validate that any
  score is backed by at least one `supporting_quote`, same as the existing quote-verification
  check; if no quote is found for a dimension, that dimension must be marked insufficient
  rather than scored.
- The Judge (Stage 4) must handle a mix of scored and insufficient-evidence dimensions across
  agents — e.g., don't silently drop insufficient dimensions from the weighting; the final
  report should state plainly which aspects of the candidate could not be assessed and why,
  rather than only showing the aspects that were.
- Add this to the Final Report (Stage 5) as an explicit section: "Not Assessed" or "Insufficient
  Evidence," separate from Strengths/Concerns, so a reviewer can see the system didn't
  fabricate an opinion where the transcript/resume was silent.

---

## C. Multi-Candidate Upload and Side-by-Side Comparison (bonus)

### Requirements

**Upload flow**
- Replace the single-candidate selector with a batch upload flow: allow the user to upload N
  candidates, each as a (resume, transcript) pair, plus one shared job description for the
  batch.
- Run the existing 5-stage pipeline independently and in parallel for each candidate — no
  cross-candidate visibility during Stages 1-4 (a candidate's agents must not see another
  candidate's profile or opinions; this mirrors the existing agent-isolation requirement, just
  one level up).
- Show per-candidate progress (which stage each candidate's pipeline is currently on) so the
  UI doesn't look frozen during a batch run.

**Comparison view (new Stage 6, additive — doesn't replace individual reports)**
- Build a comparison dashboard showing all N candidates side by side:
  - Final recommendation + confidence per candidate
  - A shared-criteria table (derived from the Job Description's stated requirements) showing
    how each candidate scored against each requirement, with citations
  - Ranking: order candidates by final recommendation strength, but make the ranking
    rationale explicit (why candidate A ranked above B) rather than just sorting by a single
    number — this should reuse the Judge's evidence-weighted reasoning style, not introduce a
    new raw-score sort.
  - Surface cases where two candidates are close calls or where the panel's confidence differs
    meaningfully between them.
- This comparison step should be a distinct, clearly-labeled stage in the pipeline (Stage 6:
  Comparative Ranking), generated only after all individual candidate pipelines complete —
  keep it visually and architecturally separate from the per-candidate Stage 4 Judge step, so
  it's clear that individual verdicts weren't influenced by comparison.

**UI**
- Update the top-level candidate selector to a multi-select / batch view toggle: "Individual
  Candidate" (existing 5-stage view, per candidate) vs. "Compare Candidates" (new side-by-side
  view).
- Keep all existing per-candidate views (Profile, Isolated Opinions, Debate, Judge, Report)
  exactly as they are — comparison is additive, not a replacement.

---

## D. Deployment Note (for judges/reviewers to access the demo)

Add a short `DEPLOYMENT.md` with two options:
1. Local + tunnel: `ngrok http 3000` (proxy `/api` calls through the frontend dev server to
   avoid needing a second tunnel for the backend on port 8000).
2. Static hosting: brief steps for deploying frontend (Vercel/Netlify) and backend
   (Render/Railway) if a persistent URL is preferred over a live-tunnel demo.

---

## Definition of Done (addendum)

- [ ] Real JD/Resume/Transcript PDFs ingest correctly into `CandidateProfile`s with meaningful
      source citations
- [ ] Job Description is used by the Hiring Manager Agent (and optionally Technical Agent) for
      requirement-specific evaluation
- [ ] Agents can mark a dimension `insufficient_evidence` instead of forcing a score; Judge and
      Final Report both surface this explicitly
- [ ] Both provided candidates (A and B) process successfully end to end
- [ ] N-candidate batch upload works, with full per-candidate pipeline isolation preserved
- [ ] Comparison/ranking view shows evidence-weighted rationale, not a raw score sort
- [ ] `DEPLOYMENT.md` documents at least one way for a judge to access the running app remotely
