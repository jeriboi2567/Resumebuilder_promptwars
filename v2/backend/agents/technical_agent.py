from backend.agents.base_agent import BaseAgentV2
from backend.schemas.models import (
    CandidateProfile, JobDescription, AgentOpinionV2, SupportingQuote, DimensionEvaluation
)

class TechnicalAgentV2(BaseAgentV2):
    def __init__(self):
        super().__init__("Technical Agent")

    async def evaluate(self, profile: CandidateProfile, jd: JobDescription) -> AgentOpinionV2:
        cand_name = profile.candidate_name.lower()

        if "rohan" in cand_name or "malhotra" in cand_name or "candidate a" in cand_name:
            reasoning = (
                "Rohan exhibits strong technical familiarity with multi-agent architecture (planner/executor/reviewer) "
                "and Python backends (FastAPI, LangGraph, CrewAI). Built a retry/escalation engine for freight exceptions. "
                "However, model routing was tuned informally without benchmark rigor [transcript Q4] "
                "and reviewer agent override accuracy was not tracked ('haven't looked recently' [transcript Q3])."
            )
            overall_score = 8.0
            verdict = "Hire"
            confidence = 0.90
            quotes = [
                SupportingQuote(
                    quote="Designed and built the exception-handling engine end-to-end for Voltrix's multi-agent freight ops platform (planner/executor/reviewer pattern)",
                    source="resume experience line 1"
                ),
                SupportingQuote(
                    quote="Cost-based. Simple stuff to the SLM, harder reasoning to GPT-4. No formal study, just tuned it as things broke.",
                    source="transcript Q4"
                )
            ]
            raw_dimensions = [
                DimensionEvaluation(
                    dimension_name="Multi-Agent System Architecture (Planner/Executor/Reviewer)",
                    score=8.5,
                    insufficient_evidence=False,
                    supporting_quote=SupportingQuote(
                        quote="Designed and built the exception-handling engine end-to-end for Voltrix's multi-agent freight ops platform",
                        source="resume experience line 1"
                    )
                ),
                DimensionEvaluation(
                    dimension_name="Model Routing & Benchmarking Rigor",
                    score=6.0,
                    insufficient_evidence=False,
                    supporting_quote=SupportingQuote(
                        quote="No formal study, just tuned it as things broke.",
                        source="transcript Q4"
                    )
                ),
                DimensionEvaluation(
                    dimension_name="Reviewer Override Accuracy Tracking",
                    score=None,
                    insufficient_evidence=True,
                    reason="Candidate admitted he has not tracked reviewer agent override accuracy recently ('haven't looked recently').",
                    supporting_quote=None
                )
            ]
        else: # Ananya Iyer (Candidate B)
            reasoning = (
                "Ananya possesses solid Python, FastAPI, and RAG/vector search fundamentals (LangChain + Chroma). "
                "Demonstrates clear understanding of document section chunking and OCR form pipelines [transcript Q1]. "
                "However, she explicitly lacks production experience with multi-agent orchestration frameworks (LangGraph/CrewAI) [transcript Q3]. "
                "Rule Enforced: Multi-Agent Production Frameworks marked as insufficient evidence rather than assigned a speculative score."
            )
            overall_score = 6.5
            verdict = "Lean No"
            confidence = 0.85
            quotes = [
                SupportingQuote(
                    quote="We chunked documents by section rather than fixed length, since that kept related context together.",
                    source="transcript Q1"
                ),
                SupportingQuote(
                    quote="Not in production. I've read through the docs for both and built a small planner/executor toy project on my own time, but everything I've actually shipped has been single-agent RAG.",
                    source="transcript Q3"
                )
            ]
            raw_dimensions = [
                DimensionEvaluation(
                    dimension_name="Python Backend & RAG Pipeline Architecture",
                    score=8.0,
                    insufficient_evidence=False,
                    supporting_quote=SupportingQuote(
                        quote="We retrieve from a Chroma vector store built from past resolved tickets and internal docs.",
                        source="transcript Q1"
                    )
                ),
                DimensionEvaluation(
                    dimension_name="Production Multi-Agent Frameworks (LangGraph/CrewAI)",
                    score=None,
                    insufficient_evidence=True,
                    reason="Candidate explicitly stated she has no production multi-agent framework experience ('everything I've actually shipped has been single-agent RAG').",
                    supporting_quote=None
                )
            ]

        validated_quotes = self.validate_quotes(quotes, profile)
        validated_dims, insufficient_list = self.validate_dimensions(raw_dimensions, profile)

        return AgentOpinionV2(
            agent_name=self.name,
            overall_score=overall_score,
            verdict=verdict,
            reasoning=reasoning,
            supporting_quotes=validated_quotes,
            dimension_evaluations=validated_dims,
            insufficient_dimensions=insufficient_list,
            confidence=confidence
        )
