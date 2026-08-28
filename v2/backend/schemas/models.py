from typing import List, Dict, Optional, Literal, Any
from pydantic import BaseModel, Field

# ==========================================
# V2: Job Description Schema
# ==========================================

class JobDescription(BaseModel):
    title: str = Field(default="Software Engineer")
    company: str = Field(default="Promptwars Inc.")
    required_skills: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    qualifications: List[str] = Field(default_factory=list)
    raw_text: str = Field(..., description="Raw text extracted from 01_Job_Description.pdf")

# ==========================================
# STAGE 1: Candidate Profile Schemas
# ==========================================

class SourceCitation(BaseModel):
    source_doc: Literal['resume', 'transcript', 'pdf'] = Field(..., description="Document type")
    location: str = Field(..., description="Page, line number, or transcript timestamp")
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
    topic: str
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
# STAGE 2: Independent Agent Opinions (V2 - Insufficient Evidence Support)
# ==========================================

class SupportingQuote(BaseModel):
    quote: str = Field(..., description="Verbatim quote from candidate profile/source")
    source: str = Field(..., description="Citation location")
    verified: bool = Field(default=True, description="True if quote exists in source text")
    verification_note: Optional[str] = Field(default=None)

class DimensionEvaluation(BaseModel):
    dimension_name: str = Field(..., description="Evaluation dimension or JD requirement")
    score: Optional[float] = Field(default=None, ge=1.0, le=10.0)
    insufficient_evidence: bool = Field(default=False)
    reason: Optional[str] = Field(default=None, description="Reason if score is missing or marked insufficient")
    supporting_quote: Optional[SupportingQuote] = Field(default=None)

class AgentOpinionV2(BaseModel):
    agent_name: Literal['Technical Agent', 'HR / Culture Agent', 'Hiring Manager Agent', 'Skeptic Agent']
    overall_score: Optional[float] = Field(default=None, ge=1.0, le=10.0)
    verdict: Literal['Strong Hire', 'Hire', 'Lean Hire', 'Lean No', 'No Hire', 'Strong No']
    reasoning: str = Field(..., description="Evidence-backed reasoning")
    supporting_quotes: List[SupportingQuote] = Field(..., min_length=1)
    dimension_evaluations: List[DimensionEvaluation] = Field(default_factory=list)
    insufficient_dimensions: List[str] = Field(default_factory=list, description="Dimensions lacking supporting quotes")
    confidence: float = Field(..., ge=0.0, le=1.0)

class IndependentOpinionsV2(BaseModel):
    candidate_id: str
    opinions: Dict[str, AgentOpinionV2]

# ==========================================
# STAGE 3: Structured Debate Schemas
# ==========================================

class DebateTurn(BaseModel):
    round_number: int
    agent_name: str
    responding_to: str
    stance: Literal['Agree', 'Disagree', 'Revise', 'Reinforce']
    message: str
    cites_quote: Optional[str] = None

class AgentStanceDelta(BaseModel):
    agent_name: str
    score_before: Optional[float]
    verdict_before: str
    score_after: Optional[float]
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
    not_assessed_dimensions: List[Dict[str, str]] = Field(default_factory=list)
    evidence_weights: Dict[str, float]

# ==========================================
# STAGE 5: Final Report Schemas
# ==========================================

class CandidateReportV2(BaseModel):
    candidate_id: str
    candidate_name: str
    final_recommendation: str
    confidence: float
    strengths: List[Dict[str, str]]
    concerns: List[Dict[str, str]]
    not_assessed_dimensions: List[Dict[str, str]]  # Explicit Section B requirement
    agent_summaries: List[Dict[str, Any]]
    unresolved_disagreements: List[str]
    debate_highlights: List[DebateTurn]
    markdown_content: str

class PipelineRunResultV2(BaseModel):
    run_id: str
    timestamp: str
    profile: CandidateProfile
    independent_opinions: IndependentOpinionsV2
    debate_state: DebateState
    final_decision: FinalDecision
    report: CandidateReportV2
    audio_url: Optional[str] = None

# ==========================================
# STAGE 6: Comparative Ranking Schemas
# ==========================================

class CandidateRankingItem(BaseModel):
    rank: int
    candidate_id: str
    candidate_name: str
    final_recommendation: str
    confidence: float
    key_differentiators: List[str]

class JDRequirementCompliance(BaseModel):
    requirement: str
    candidate_evaluations: Dict[str, Dict[str, Any]]  # cand_id -> {status, citation/reason}

class Stage6ComparativeRanking(BaseModel):
    batch_id: str
    timestamp: str
    job_description_title: str
    rankings: List[CandidateRankingItem]
    jd_compliance_matrix: List[JDRequirementCompliance]
    close_calls: List[str]
    comparison_rationale: str

class BatchPipelineRunResult(BaseModel):
    batch_id: str
    timestamp: str
    job_description: JobDescription
    candidate_results: Dict[str, PipelineRunResultV2]
    stage6_comparison: Stage6ComparativeRanking
