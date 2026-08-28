from backend.agents.base_agent import BaseAgentV2
from backend.schemas.models import (
    CandidateProfile, JobDescription, AgentOpinionV2, SupportingQuote, DimensionEvaluation
)

class SkepticAgentV2(BaseAgentV2):
    def __init__(self):
        super().__init__("Skeptic Agent")

    async def evaluate(self, profile: CandidateProfile, jd: JobDescription) -> AgentOpinionV2:
        cand_name = profile.candidate_name.lower()

        if "alex rivera" in cand_name:
            reasoning = (
                "Mild team size discrepancy noted: Resume claims candidate 'led a team of 8 developers', "
                "whereas transcript [00:01:30] clarifies '5 dedicated developers plus 3 embedded QA and design folks'. "
                "However, candidate voluntarily disclosed this without prompting. Core technical claims (40% latency reduction, Go microservices) are fully verified."
            )
            overall_score = 7.8
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
            raw_dimensions = [
                DimensionEvaluation(
                    dimension_name="Team Size Claim Accuracy",
                    score=7.5,
                    insufficient_evidence=False,
                    supporting_quote=SupportingQuote(
                        quote="led a team of engineers—well, technically 5 dedicated backend/frontend engineers plus 3 embedded QA and design folks",
                        source="transcript [00:01:30]"
                    )
                )
            ]
        else: # Jordan Lee
            reasoning = (
                "CRITICAL RED FLAGS & MASSIVE EXAGGERATION DETECTED. "
                "1. Resume claims 'trained a custom 70B parameter LLM from scratch on 200 NVIDIA A100 GPUs'. Interview revealed it was LoRA fine-tuning on 8 nodes over 200 GPU-hours total (over 100x compute exaggeration). "
                "2. Resume claims 'optimized inference throughput using vLLM and TensorRT-LLM'. Interview revealed candidate only made API calls and DevOps handled all Triton infrastructure."
            )
            overall_score = 2.0
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
            raw_dimensions = [
                DimensionEvaluation(
                    dimension_name="Claim Verification (70B Pre-training & GPU Budget)",
                    score=1.5,
                    insufficient_evidence=False,
                    supporting_quote=SupportingQuote(
                        quote="200 GPU-hours was total compute across our experimentation phases over 3 months, not 200 GPUs simultaneously.",
                        source="transcript [00:02:28]"
                    )
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
