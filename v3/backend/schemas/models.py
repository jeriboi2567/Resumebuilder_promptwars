from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class JobDescription(BaseModel):
    job_id: str = "jd_default"
    title: str
    company: str = "Target Employer"
    required_skills: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    qualifications: List[str] = Field(default_factory=list)
    raw_text: str

class SourceCitation(BaseModel):
    source_doc: str # 'resume' | 'transcript' | 'pdf'
    location: str
    quote_snippet: str

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
    claim_type: str # 'quantitative' | 'qualitative'
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
    skills: List[SkillClaim] = Field(default_factory=list)
    experiences: List[ExperienceItem] = Field(default_factory=list)
    claims: List[CandidateClaim] = Field(default_factory=list)
    quote_bank: List[DirectQuote] = Field(default_factory=list)
    raw_resume_text: str
    raw_transcript_text: str

class SupportingQuote(BaseModel):
    quote: str
    source: str
    verified: bool = True
    verification_note: Optional[str] = None

class DimensionEvaluation(BaseModel):
    dimension_name: str
    score: Optional[float] = None
    insufficient_evidence: bool = False
    reason: Optional[str] = None
    supporting_quote: Optional[SupportingQuote] = None

class AgentOpinionV2(BaseModel):
    agent_name: str # 'Technical Agent' | 'HR / Culture Agent' | 'Hiring Manager Agent' | 'Skeptic Agent'
    overall_score: Optional[float] = None
    verdict: str # 'Strong Hire' | 'Hire' | 'Lean Hire' | 'Lean No' | 'No Hire' | 'Strong No'
    reasoning: str
    supporting_quotes: List[SupportingQuote] = Field(default_factory=list)
    dimension_evaluations: List[DimensionEvaluation] = Field(default_factory=list)
    insufficient_dimensions: List[str] = Field(default_factory=list)
    confidence: float

class IndependentOpinionsV2(BaseModel):
    candidate_id: str
    opinions: Dict[str, AgentOpinionV2]

class DebateTurn(BaseModel):
    round_number: int
    agent_name: str
    responding_to: str
    stance: str # 'Agree' | 'Disagree' | 'Revise' | 'Reinforce'
    message: str
    cites_quote: Optional[str] = None

class AgentStanceDelta(BaseModel):
    agent_name: str
    score_before: Optional[float] = None
    verdict_before: str
    score_after: Optional[float] = None
    verdict_after: str
    changed: bool
    change_reason: str

class DebateState(BaseModel):
    candidate_id: str
    rounds: int
    turns: List[DebateTurn] = Field(default_factory=list)
    stance_deltas: Dict[str, AgentStanceDelta] = Field(default_factory=dict)

class FinalDecision(BaseModel):
    candidate_id: str
    recommendation: str # 'Strong Hire' | 'Hire' | 'Lean No' | 'No Hire'
    confidence: float
    decision_rationale: str
    unresolved_disagreements: List[str] = Field(default_factory=list)
    not_assessed_dimensions: List[Dict[str, str]] = Field(default_factory=list)
    evidence_weights: Dict[str, float] = Field(default_factory=dict)

class CandidateReportV2(BaseModel):
    candidate_id: str
    candidate_name: str
    final_recommendation: str
    confidence: float
    strengths: List[Dict[str, str]] = Field(default_factory=list)
    concerns: List[Dict[str, str]] = Field(default_factory=list)
    not_assessed_dimensions: List[Dict[str, str]] = Field(default_factory=list)
    agent_summaries: List[Dict[str, Any]] = Field(default_factory=list)
    unresolved_disagreements: List[str] = Field(default_factory=list)
    debate_highlights: List[DebateTurn] = Field(default_factory=list)
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

class CandidateRankingItem(BaseModel):
    rank: int
    candidate_id: str
    candidate_name: str
    final_recommendation: str
    confidence: float
    key_differentiators: List[str] = Field(default_factory=list)

class JDRequirementCompliance(BaseModel):
    requirement: str
    candidate_evaluations: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

class Stage6ComparativeRanking(BaseModel):
    batch_id: str
    timestamp: str
    job_description_title: str
    rankings: List[CandidateRankingItem] = Field(default_factory=list)
    jd_compliance_matrix: List[JDRequirementCompliance] = Field(default_factory=list)
    close_calls: List[str] = Field(default_factory=list)
    comparison_rationale: str

class BatchPipelineRunResult(BaseModel):
    batch_id: str
    timestamp: str
    job_description: JobDescription
    candidate_results: Dict[str, PipelineRunResultV2]
    stage6_comparison: Stage6ComparativeRanking

class HiringRoleV3(BaseModel):
    role_id: str
    job_description: JobDescription
    created_at: str
    updated_at: str
    candidate_results: Dict[str, PipelineRunResultV2] = Field(default_factory=dict)
    stage6_comparison: Optional[Stage6ComparativeRanking] = None
