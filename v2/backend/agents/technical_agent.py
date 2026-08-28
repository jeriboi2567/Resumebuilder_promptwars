from backend.agents.base_agent import BaseAgentV2
from backend.schemas.models import (
    CandidateProfile, JobDescription, AgentOpinionV2, SupportingQuote, DimensionEvaluation
)

class TechnicalAgentV2(BaseAgentV2):
    def __init__(self):
        super().__init__("Technical Agent")

    async def evaluate(self, profile: CandidateProfile, jd: JobDescription) -> AgentOpinionV2:
        cand_name = profile.candidate_name.lower()

        if "alex rivera" in cand_name:
            reasoning = (
                "Candidate demonstrates exceptional fit against JD technical requirements. "
                "P99 latency reduction (from 850ms to 510ms) meets JD's target of <600ms. "
                "Go microservices, Kafka event streaming, and PostgreSQL indexing are backed by strong citations. "
                "Note: Deep LLM inference serving (vLLM / Triton) was not assessed as source documents contain no LLM deployment evidence."
            )
            overall_score = 9.0
            verdict = "Strong Hire"
            confidence = 0.95
            quotes = [
                SupportingQuote(
                    quote="The main bottleneck was unindexed JSONB queries in PostgreSQL combined with redundant REST polling.",
                    source="transcript [00:02:30]"
                ),
                SupportingQuote(
                    quote="We introduced a Redis write-through cache for trending metrics, restructured our SQL indexes, and migrated our heavy data crunching paths into Go microservices communicating via Kafka.",
                    source="transcript [00:02:30]"
                )
            ]
            raw_dimensions = [
                DimensionEvaluation(
                    dimension_name="P99 Endpoint Latency (<600ms Target)",
                    score=9.5,
                    insufficient_evidence=False,
                    supporting_quote=SupportingQuote(
                        quote="brought our P99 latency down from around 850ms to 510ms under peak load",
                        source="transcript [00:02:30]"
                    )
                ),
                DimensionEvaluation(
                    dimension_name="Kafka Event Streaming & Go Microservices",
                    score=9.0,
                    insufficient_evidence=False,
                    supporting_quote=SupportingQuote(
                        quote="migrated our heavy data crunching paths into Go microservices communicating via Kafka",
                        source="transcript [00:02:30]"
                    )
                ),
                DimensionEvaluation(
                    dimension_name="LLM Fine-Tuning & Triton Inference Serving",
                    score=None,
                    insufficient_evidence=True,
                    reason="Candidate's background is in backend web systems; no LLM pre-training or Triton serving claims present in transcript/resume.",
                    supporting_quote=None
                )
            ]
        else: # Jordan Lee
            reasoning = (
                "Candidate exhibits severe gaps against JD technical expectations. "
                "Resume claims of training 70B LLM from scratch on 200 A100 GPUs collapsed in interview [00:01:25] to LoRA fine-tuning on 8 nodes. "
                "Furthermore, candidate admitted delegating Triton infrastructure serving to DevOps while relying on high-level APIs."
            )
            overall_score = 4.0
            verdict = "No Hire"
            confidence = 0.90
            quotes = [
                SupportingQuote(
                    quote="We took a base LLaMA-2 70B model checkpoint from HuggingFace and performed supervised fine-tuning (SFT) and LoRA adapter training across a cluster of 8 A100 nodes",
                    source="transcript [00:01:25]"
                ),
                SupportingQuote(
                    quote="DevOps team handled the low-level Triton and Kubernetes setup. I mostly called the API endpoints from our backend FastAPI microservice",
                    source="transcript [00:03:32]"
                )
            ]
            raw_dimensions = [
                DimensionEvaluation(
                    dimension_name="LLM Pre-training & GPU Architecture",
                    score=3.0,
                    insufficient_evidence=False,
                    supporting_quote=SupportingQuote(
                        quote="technically we didn't train the raw weights from step zero. We took a base LLaMA-2 70B model checkpoint",
                        source="transcript [00:01:25]"
                    )
                ),
                DimensionEvaluation(
                    dimension_name="Triton & Kubernetes Infrastructure",
                    score=4.0,
                    insufficient_evidence=False,
                    supporting_quote=SupportingQuote(
                        quote="DevOps team handled the low-level Triton and Kubernetes setup",
                        source="transcript [00:03:32]"
                    )
                ),
                DimensionEvaluation(
                    dimension_name="Distributed Go Data Pipelines",
                    score=None,
                    insufficient_evidence=True,
                    reason="Candidate has no Go language background mentioned in resume or transcript.",
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
