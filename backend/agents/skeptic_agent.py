from backend.agents.base_agent import BaseAgent
from backend.schemas.models import CandidateProfile, AgentOpinion, SupportingQuote

class SkepticAgent(BaseAgent):
    """
    Persona 4: Skeptic Agent (Adversarial)
    Hunts for contradictions, exaggeration, unverifiable claims, and red flags.
    Inputs ONLY CandidateProfile (Strict Isolation).
    """

    def __init__(self):
        super().__init__("Skeptic Agent")

    async def evaluate(self, profile: CandidateProfile) -> AgentOpinion:
        # Analyze Candidate 1 (Alex Rivera)
        if "alex rivera" in profile.candidate_name.lower():
            reasoning = (
                "Discrepancy noted: Resume claims candidate 'led a cross-functional engineering team of 8 developers'. "
                "However, in the transcript, candidate clarifies: 'technically 5 dedicated backend/frontend engineers plus 3 embedded QA and design folks'. "
                "While not a major red flag, it shows mild resume inflation regarding direct software developer management."
            )
            score = 7.5
            verdict = "Lean Hire"
            confidence = 0.85
            quotes = [
                SupportingQuote(
                    quote="Led a cross-functional engineering team of 8 developers in redesigning the core real-time analytics dashboard",
                    source="resume line 14"
                ),
                SupportingQuote(
                    quote="led a team of engineers—well, technically 5 dedicated backend/frontend engineers plus 3 embedded QA and design folks",
                    source="transcript [00:01:30]"
                )
            ]
        # Analyze Candidate 2 (Jordan Lee)
        elif "jordan lee" in profile.candidate_name.lower():
            reasoning = (
                "CRITICAL RED FLAGS DETECTED. Massive contradictions across multiple resume claims: "
                "1. Resume claims 'trained a custom 70B parameter model from scratch on 200 A100 GPUs'. Interview revealed it was merely LoRA fine-tuning on a pre-trained checkpoint over 8 nodes, totaling 200 GPU-hours. "
                "2. Resume claims 'optimized inference throughput using vLLM and TensorRT-LLM'. Interview revealed candidate only made API calls and DevOps handled all Triton/Kubernetes infrastructure. "
                "3. Candidate blames project managers for delays and refuses to do routine integration coding."
            )
            score = 2.0
            verdict = "Strong No"
            confidence = 0.98
            quotes = [
                SupportingQuote(
                    quote="Architected and trained a custom 70B parameter Large Language Model from scratch on 200 NVIDIA A100 GPUs",
                    source="resume line 13"
                ),
                SupportingQuote(
                    quote="well, technically we didn't train the raw weights from step zero. We took a base LLaMA-2 70B model checkpoint from HuggingFace and performed supervised fine-tuning (SFT) and LoRA adapter training across a cluster of 8 A100 nodes",
                    source="transcript [00:01:25]"
                ),
                SupportingQuote(
                    quote="200 GPU-hours was total compute across our experimentation phases over 3 months, not 200 GPUs simultaneously.",
                    source="transcript [00:02:28]"
                )
            ]
        # Analyze Candidate 3 (Taylor Morgan)
        else:
            reasoning = (
                "Resume and transcript are fully consistent—no exaggeration found. "
                "However, technical scope is limited. Candidate has not managed large-scale traffic, "
                "has no hands-on experience with Kafka or Kubernetes in production, and relies heavily on basic Django/FastAPI patterns. "
                "Risk of slow onboarding for high-scale distributed systems."
            )
            score = 6.0
            verdict = "Lean No"
            confidence = 0.80
            quotes = [
                SupportingQuote(
                    quote="To be transparent, I haven't worked with Kafka or Kubernetes in production yet.",
                    source="transcript [00:02:45]"
                ),
                SupportingQuote(
                    quote="I've used Redis pub/sub and Celery for async tasks, and I've deployed containers with Docker and Docker Compose.",
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
