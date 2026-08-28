# Build Prompt: Multi-Agent Candidate Evaluation System

## Project Overview

Build a full-stack application that evaluates job candidates by reading their resume and transcript, then running **four independent AI agent personas** that each form their own opinion, engage in a **structured debate**, and converge on a **final hiring recommendation** through a weighted reasoning step (not score averaging).

The core value of this system is **evidentiary rigor** — every claim any agent makes must be traceable to a real quote or fact from the source documents — and **genuine multi-agent deliberation**, not four parallel opinions dressed up as a debate.

---

## System Architecture

Build this as a pipeline with clearly separated stages. Each stage's output should be a structured, typed object (e.g., a Pydantic model or TypeScript interface) that gets passed to the next stage and is also persisted (e.g., as JSON) so the full reasoning trail is inspectable and auditable after the fact.

```
Resume + Transcript
        │
        ▼
[1] Candidate Profile Builder
        │
        ▼
[2] Independent Agent Opinions (4 parallel, isolated LLM calls)
        │
        ▼
[3] Structured Debate (multi-round, agents see each other's opinions)
        │
        ▼
[4] Final Decision Synthesis (weighted reasoning, not averaging)
        │
        ▼
[5] Final Report
```

---

## Stage 1 — Candidate Profile Builder

Build a module that ingests the raw resume text and interview/transcript text and extracts a **shared structured profile** that all downstream agents will consume. This is the single source of truth — agents should not each re-parse the raw documents independently, to avoid inconsistent readings of the same facts.

The profile should extract and structure:
- **Identity/role context**: candidate name, role applied for, seniority level
- **Skills claimed**: technical skills, tools, frameworks, with the source snippet where each was mentioned
- **Experience**: roles, companies, durations, described responsibilities and achievements
- **Claims made**: any specific quantifiable or qualitative claims ("led a team of 8," "improved latency by 40%," "fluent in Rust") tagged with their exact source location (resume line / transcript timestamp or turn number)
- **Direct quotes bank**: a searchable index of quotable spans from the transcript, tagged by topic (technical, behavioral, communication, etc.) so agents can cite precisely instead of paraphrasing from memory

Output this as a single structured `CandidateProfile` object (JSON/Pydantic/TS interface). Store the raw source text alongside it so agents can pull exact quotes rather than reconstructing them.

**Important:** every fact in this profile must carry a citation back to the exact source text (verbatim substring + location), so later stages can enforce "no claim without a quote."

---

## Stage 2 — Independent Agent Opinions

Implement at least these four personas, each as a **separate, isolated LLM call**:

1. **Technical Agent** — evaluates technical skill and depth: does the candidate's described experience match the claimed skill level? Are technical claims specific and plausible, or vague/generic?
2. **HR / Culture Agent** — evaluates communication quality, teamwork signals, and honesty/consistency in how the candidate talks about their work and colleagues.
3. **Hiring Manager Agent** — evaluates overall role fit: given everything in the profile, is this person worth hiring for the specific role, weighing both strengths and practical risk.
4. **Skeptic Agent** — actively hunts for contradictions, exaggeration, unverifiable claims, and red flags. This agent's job is adversarial: assume claims need to be earned, not accepted.

### Hard requirements for this stage
- **True isolation**: each agent call must receive only the `CandidateProfile` (and raw source text) — never the outputs of the other agents. Implement this as genuinely separate API calls with separate prompts/contexts, not one call asked to role-play four personas. This is the part most likely to be faked — enforce it architecturally (e.g., each agent function only accepts `CandidateProfile` as input, no `other_opinions` parameter exists at this stage).
- **Evidence-backed opinions only**: each agent's output must be a structured object containing, at minimum:
  - `score` or `verdict` (persona-specific scale)
  - `reasoning` (free text)
  - `supporting_quotes`: a list of `{quote: str, source: str}` pairs pulled from the actual transcript/resume — reject or flag any agent output where a claim isn't backed by a quote/fact from the profile. Consider a validation pass that checks each `supporting_quotes` entry actually appears (or closely matches) the source text.
  - `confidence` (numeric or categorical) — this feeds directly into Stage 4's weighting.

Run these four calls concurrently for latency, then collect results into a single `IndependentOpinions` object before proceeding.

---

## Stage 3 — Structured Debate

This is not "show all four opinions side by side." Implement an actual multi-turn exchange:

1. Reveal all four independent opinions to each agent (now, for the first time, each agent sees what the others said).
2. Run at least one, ideally two, rounds where each agent is prompted specifically to:
   - Identify a point of disagreement or reinforcement with a **named other agent**
   - Explicitly agree, disagree, or revise its own position, and say *why* — referencing the other agent's evidence, not just its score
3. Track opinion deltas: store each agent's position before and after the debate round(s) (`opinion_before`, `opinion_after`, `changed: bool`, `change_reason`) so you can prove the debate actually moved someone, or explicitly log that it didn't.
4. Require the debate transcript to be structured, not just a blob of text — e.g., a list of `DebateTurn { agent, responding_to (agent name), stance, message, cites_quote }` objects. This also makes it easy to render in a UI.

A good implementation pattern: an orchestrator loop that, for each round, prompts each agent with "here is the current state of the debate + the other agents' latest positions; respond directly to at least one specific point another agent made."

---

## Stage 4 — Final Decision Synthesis

Do **not** average the four scores. Implement a distinct reasoning stage — ideally its own LLM call (a "Judge" or "Decision Synthesizer") that is given:
- All four independent opinions
- The full debate transcript (including who changed their mind and why)
- The confidence levels attached to each opinion

The Judge must:
- Weigh evidence quality over raw scores (an agent with one strong, specific quote should outweigh an agent with three vague assertions)
- Explicitly account for confidence — down-weight low-confidence opinions, especially ones that were contradicted in debate and not defended
- Explicitly surface any **unresolved disagreement** — cases where agents debated but did not converge — rather than silently smoothing it into an average
- Produce a `FinalDecision` object with: `recommendation` (e.g., Strong Hire / Hire / Lean No / No Hire), `confidence`, `decision_rationale` (must reference specific agent evidence, not just restate scores), and `unresolved_disagreements` (list)

This stage is the crux of the assignment — make the reasoning transparent and inspectable, not a black box that outputs a number.

---

## Stage 5 — Final Report

Render a per-candidate report (in the UI and as an exportable artifact — e.g., Markdown or PDF) containing:
- **Final recommendation** + **confidence level**
- **Strengths** (with supporting quotes)
- **Concerns / red flags** (with supporting quotes, especially from the Skeptic Agent)
- **Agent-by-agent summary**: each agent's initial stance vs. final stance post-debate
- **Unresolved disagreements**: anything the agents debated but didn't fully reconcile — state this honestly rather than papering over it
- **Debate highlights**: 2-4 key exchanges that most influenced the final decision

---

## Bonus (Optional but Encouraged)

**Voice debate session**: use a TTS pipeline (e.g., distinct voices per persona) to narrate the Stage 3 debate as audio/video, so a user can "listen in" on the four agents arguing about the candidate. Even a simple sequential TTS readout of the structured `DebateTurn` list, with a different voice per agent, satisfies this.

---

## Suggested Tech Stack

- **Backend**: Python (FastAPI) or Node/TypeScript — pick based on your LLM SDK preference
- **LLM orchestration**: direct Anthropic/OpenAI SDK calls per agent, or a lightweight agent framework (avoid heavyweight multi-agent frameworks unless they clearly simplify the isolation and debate requirements — the isolation requirement is easiest to enforce with plain, explicit function boundaries)
- **Data validation**: Pydantic (Python) or Zod (TS) for every stage's output schema, especially to enforce "quote must be present" on agent opinions
- **Frontend**: React — render the pipeline as a visual flow (profile → 4 opinion cards → debate thread → final report), so the debate and disagreement are visible, not just the end score
- **Storage**: persist every stage's output per candidate (profile, independent opinions, debate transcript, final decision) so runs are auditable and reproducible

---

## Suggested Project Structure

```
/backend
  /profile_builder/        # Stage 1
  /agents/
    technical_agent.py
    hr_culture_agent.py
    hiring_manager_agent.py
    skeptic_agent.py
  /debate/                 # Stage 3 orchestrator
  /decision/                # Stage 4 judge/synthesizer
  /report/                  # Stage 5 rendering
  /schemas/                 # shared Pydantic/Zod models
  /storage/                 # per-run persistence
/frontend
  /components/
    ProfileView.tsx
    OpinionCard.tsx
    DebateThread.tsx
    FinalReport.tsx
/sample_data
  resume_1.txt
  transcript_1.txt
```

---

## Definition of Done — Checklist

- [ ] Candidate profile is extracted once and shared across all agents, with citations to source text
- [ ] Four agent personas run as genuinely separate, isolated LLM calls with no cross-visibility at Stage 2
- [ ] Every agent opinion includes at least one real quote/fact from the transcript or resume; unsupported claims are rejected or flagged
- [ ] Debate stage shows at least one agent explicitly responding to, and potentially revising its view because of, another named agent's point
- [ ] Before/after positions are tracked per agent so debate impact is provable
- [ ] Final decision comes from a distinct reasoning/synthesis step that weighs evidence and confidence — not a numeric average of the four scores
- [ ] Final report includes recommendation, confidence, strengths, concerns, and any unresolved disagreement
- [ ] (Bonus) Debate is narratable as a multi-voice audio/voice session

---

## Instructions to Antigravity

Build this end to end: scaffold the project structure above, implement each stage as a separately testable module, wire up the pipeline orchestrator, and build a frontend that visually exposes the pipeline stages (especially the debate thread and final decision rationale) rather than just showing a final score. Use two or three sample resume/transcript pairs (you may synthesize realistic sample data) to test and demo the full flow end to end. Prioritize correctness of the isolation and debate requirements above visual polish — these are the two most heavily weighted and most commonly faked parts of this assignment.
