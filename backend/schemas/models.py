from typing import List, Dict, Optional, Literal, Any
from pydantic import BaseModel, Field

# ==========================================
# STAGE 1: Candidate Profile Schemas
# ==========================================

class SourceCitation(BaseModel):
    source_doc: Literal['resume', 'transcript'] = Field(..., description="Document type")
    location: str = Field(..., description="Line number or transcript timestamp")
    quote_snippet: str = Field(..., description="Verbatim substring citation")

class SkillClaim(BaseModel):
    skill_name: str
    category: str
    citation: SourceCitation

class ExperienceItem(BaseModel):
    company: str
    role: str
    duration: str
    responsibilities: List[str]
    citation: SourceCitation

class CandidateClaim(BaseModel):
    claim_type: Literal['quantitative', 'qualitative']
    description: str
    citation: SourceCitation

class DirectQuote(BaseModel):
    id: str
    quote: str
    topic: str  # e.g., 'technical', 'behavioral', 'leadership', 'accuracy'
    location: str
    speaker: Optional[str] = None

class CandidateProfile(BaseModel):
    candidate_id: str
    candidate_name: str
    role_applied: str
    seniority_level: str
    skills: List[SkillClaim]
    experiences: List[ExperienceItem]
    claims: List[CandidateClaim]
    quote_bank: List[DirectQuote]
    raw_resume_text: str
    raw_transcript_text: str

# ==========================================
# STAGE 2: Independent Agent Opinions Schemas
# ==========================================

class SupportingQuote(BaseModel):
    quote: str = Field(..., description="Verbatim quote from candidate profile/source")
    source: str = Field(..., description="Citation location, e.g. transcript [00:02:15] or resume")
    verified: bool = Field(default=True, description="True if quote actually exists in source text")
    verification_note: Optional[str] = Field(default=None, description="Details if quote check failed or passed")

class AgentOpinion(BaseModel):
    agent_name: Literal['Technical Agent', 'HR / Culture Agent', 'Hiring Manager Agent', 'Skeptic Agent']
    score: float = Field(..., ge=1.0, le=10.0, description="Persona rating from 1 to 10")
    verdict: Literal['Strong Hire', 'Hire', 'Lean Hire', 'Lean No', 'No Hire', 'Strong No']
    reasoning: str = Field(..., description="Evidence-backed reasoning")
    supporting_quotes: List[SupportingQuote] = Field(..., min_length=1)
    confidence: float = Field(..., ge=0.0, le=1.0, description="Agent confidence score")

class IndependentOpinions(BaseModel):
    candidate_id: str
    opinions: Dict[str, AgentOpinion]

# ==========================================
# STAGE 3: Structured Debate Schemas
# ==========================================

class DebateTurn(BaseModel):
    round_number: int
    agent_name: str
    responding_to: str  # e.g., 'Skeptic Agent', 'Technical Agent', etc.
    stance: Literal['Agree', 'Disagree', 'Revise', 'Reinforce']
    message: str
    cites_quote: Optional[str] = None

class AgentStanceDelta(BaseModel):
    agent_name: str
    score_before: float
    verdict_before: str
    score_after: float
    verdict_after: str
    changed: bool
    change_reason: str

class DebateState(BaseModel):
    candidate_id: str
    rounds: int
    turns: List[DebateTurn]
    stance_deltas: Dict[str, AgentStanceDelta]

# ==========================================
# STAGE 4: Final Decision Synthesis Schemas
# ==========================================

class FinalDecision(BaseModel):
    candidate_id: str
    recommendation: Literal['Strong Hire', 'Hire', 'Lean No', 'No Hire']
    confidence: float = Field(..., ge=0.0, le=1.0)
    decision_rationale: str
    unresolved_disagreements: List[str]
    evidence_weights: Dict[str, float]

# ==========================================
# STAGE 5 & END-TO-END Schemas
# ==========================================

class CandidateReport(BaseModel):
    candidate_id: str
    candidate_name: str
    final_recommendation: str
    confidence: float
    strengths: List[Dict[str, str]]
    concerns: List[Dict[str, str]]
    agent_summaries: List[Dict[str, Any]]
    unresolved_disagreements: List[str]
    debate_highlights: List[DebateTurn]
    markdown_content: str

class PipelineRunResult(BaseModel):
    run_id: str
    timestamp: str
    profile: CandidateProfile
    independent_opinions: IndependentOpinions
    debate_state: DebateState
    final_decision: FinalDecision
    report: CandidateReport
