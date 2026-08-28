export interface JobDescription {
  title: string;
  company: string;
  required_skills: string[];
  responsibilities: string[];
  qualifications: string[];
  raw_text: string;
}

export interface SourceCitation {
  source_doc: 'resume' | 'transcript' | 'pdf';
  location: string;
  quote_snippet: string;
}

export interface SkillClaim {
  skill_name: string;
  category: string;
  citation: SourceCitation;
}

export interface ExperienceItem {
  company: string;
  role: string;
  duration: string;
  responsibilities: string[];
  citation: SourceCitation;
}

export interface CandidateClaim {
  claim_type: 'quantitative' | 'qualitative';
  description: string;
  citation: SourceCitation;
}

export interface DirectQuote {
  id: string;
  quote: string;
  topic: string;
  location: string;
  speaker?: string;
}

export interface CandidateProfile {
  candidate_id: string;
  candidate_name: string;
  role_applied: string;
  seniority_level: string;
  skills: SkillClaim[];
  experiences: ExperienceItem[];
  claims: CandidateClaim[];
  quote_bank: DirectQuote[];
  raw_resume_text: string;
  raw_transcript_text: string;
}

export interface SupportingQuote {
  quote: string;
  source: string;
  verified: boolean;
  verification_note?: string;
}

export interface DimensionEvaluation {
  dimension_name: string;
  score?: number;
  insufficient_evidence: boolean;
  reason?: string;
  supporting_quote?: SupportingQuote;
}

export interface AgentOpinionV2 {
  agent_name: 'Technical Agent' | 'HR / Culture Agent' | 'Hiring Manager Agent' | 'Skeptic Agent';
  overall_score?: number;
  verdict: 'Strong Hire' | 'Hire' | 'Lean Hire' | 'Lean No' | 'No Hire' | 'Strong No';
  reasoning: string;
  supporting_quotes: SupportingQuote[];
  dimension_evaluations: DimensionEvaluation[];
  insufficient_dimensions: string[];
  confidence: number;
}

export interface IndependentOpinionsV2 {
  candidate_id: string;
  opinions: Record<string, AgentOpinionV2>;
}

export interface DebateTurn {
  round_number: number;
  agent_name: string;
  responding_to: string;
  stance: 'Agree' | 'Disagree' | 'Revise' | 'Reinforce';
  message: string;
  cites_quote?: string;
}

export interface AgentStanceDelta {
  agent_name: string;
  score_before?: number;
  verdict_before: string;
  score_after?: number;
  verdict_after: string;
  changed: boolean;
  change_reason: string;
}

export interface DebateState {
  candidate_id: string;
  rounds: number;
  turns: DebateTurn[];
  stance_deltas: Record<string, AgentStanceDelta>;
}

export interface FinalDecision {
  candidate_id: string;
  recommendation: 'Strong Hire' | 'Hire' | 'Lean No' | 'No Hire';
  confidence: number;
  decision_rationale: string;
  unresolved_disagreements: string[];
  not_assessed_dimensions: Array<{ dimension: string; agent: string; reason: string }>;
  evidence_weights: Record<string, number>;
}

export interface CandidateReportV2 {
  candidate_id: string;
  candidate_name: string;
  final_recommendation: string;
  confidence: number;
  strengths: Array<{ quote: string; source: string; agent: string; explanation: string }>;
  concerns: Array<{ quote: string; source: string; agent: string; explanation: string }>;
  not_assessed_dimensions: Array<{ dimension: string; agent: string; reason: string }>;
  agent_summaries: Array<{
    agent_name: string;
    initial_score: number;
    initial_verdict: string;
    final_score: number;
    final_verdict: string;
    changed: boolean;
    change_reason: string;
  }>;
  unresolved_disagreements: string[];
  debate_highlights: DebateTurn[];
  markdown_content: string;
}

export interface PipelineRunResultV2 {
  run_id: string;
  timestamp: string;
  profile: CandidateProfile;
  independent_opinions: IndependentOpinionsV2;
  debate_state: DebateState;
  final_decision: FinalDecision;
  report: CandidateReportV2;
  audio_url?: string;
}

export interface CandidateRankingItem {
  rank: number;
  candidate_id: string;
  candidate_name: string;
  final_recommendation: string;
  confidence: number;
  key_differentiators: string[];
}

export interface JDRequirementCompliance {
  requirement: string;
  candidate_evaluations: Record<string, { status: string; detail: string }>;
}

export interface Stage6ComparativeRanking {
  batch_id: string;
  timestamp: string;
  job_description_title: string;
  rankings: CandidateRankingItem[];
  jd_compliance_matrix: JDRequirementCompliance[];
  close_calls: string[];
  comparison_rationale: string;
}

export interface BatchPipelineRunResult {
  batch_id: string;
  timestamp: string;
  job_description: JobDescription;
  candidate_results: Record<string, PipelineRunResultV2>;
  stage6_comparison: Stage6ComparativeRanking;
}
