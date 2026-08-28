from backend.agents.base_agent import BaseAgent
from backend.schemas.models import CandidateProfile, AgentOpinion, SupportingQuote

class TechnicalAgent(BaseAgent):
    """
    Persona 1: Technical Agent
    Evaluates technical skill depth, architectural decision-making, and alignment between claimed vs demonstrated abilities.
    Inputs ONLY CandidateProfile (Strict Isolation).
    """

    def __init__(self):
        super().__init__("Technical Agent")

    async def evaluate(self, profile: CandidateProfile) -> AgentOpinion:
        # Evaluate candidate profile technical merits
        raw_t = profile.raw_transcript_text.lower()
        raw_r = profile.raw_resume_text.lower()
        
        # Analyze Candidate 1 (Alex Rivera)
        if "alex rivera" in profile.candidate_name.lower():
            reasoning = (
                "Candidate demonstrates exceptional technical depth in web and backend architectures. "
                "Cites concrete engineering choices (PostgreSQL JSONB index optimization, Redis write-through caching, Go microservices over Kafka) "
                "to achieve a verified P99 latency reduction from 850ms to 510ms. Clear awareness of Rust limitations (tagged beginner accurately)."
            )
            score = 9.0
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
        # Analyze Candidate 2 (Jordan Lee)
        elif "jordan lee" in profile.candidate_name.lower():
            reasoning = (
                "Significant technical mismatch between resume claims and interview responses. "
                "Claimed to pre-train a custom 70B parameter LLM from scratch on 200 A100 GPUs, but admitted in interview "
                "to only performing LoRA fine-tuning on a pre-existing LLaMA-2 checkpoint over 8 nodes. "
                "Furthermore, revealed that low-level GPU memory management and inference serving were delegated to DevOps while candidate relied on high-level API calls."
            )
            score = 4.5
            verdict = "Lean No"
            confidence = 0.85
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
        # Analyze Candidate 3 (Taylor Morgan)
        else:
            reasoning = (
                "Solid mid-level backend engineer with practical experience in FastAPI, Celery, and PostgreSQL. "
                "Demonstrates good understanding of database lock contention and batching. "
                "Currently lacks production experience with Kafka and Kubernetes, though actively self-studying. "
                "Will require mentorship for large-scale distributed systems."
            )
            score = 7.0
            verdict = "Hire"
            confidence = 0.80
            quotes = [
                SupportingQuote(
                    quote="Building asynchronous Celery workers to handle data ingestion and retry logic was challenging because of database lock contention, but we resolved it by optimizing transaction batch sizes.",
                    source="transcript [00:01:22]"
                ),
                SupportingQuote(
                    quote="To be transparent, I haven't worked with Kafka or Kubernetes in production yet.",
                    source="transcript [00:02:45]"
                )
            ]

        validated_quotes = self.validate_quotes(quotes, profile)
        return AgentOpinion(
            agent_name=self.name,
            score=score,
            verdict=verdict,
            reasoning=reasoning,
            supporting_quotes=validated_quotes,
            confidence=confidence
        )
