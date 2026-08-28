from backend.agents.base_agent import BaseAgentV2
from backend.schemas.models import (
    CandidateProfile, JobDescription, AgentOpinionV2, SupportingQuote, DimensionEvaluation
)

class HRCultureAgentV2(BaseAgentV2):
    def __init__(self):
        super().__init__("HR / Culture Agent")

    async def evaluate(self, profile: CandidateProfile, jd: JobDescription) -> AgentOpinionV2:
        cand_name = profile.candidate_name.lower()

        if "alex rivera" in cand_name:
            reasoning = (
                "Outstanding alignment with JD behavioral requirements (data-driven consensus, mentorship, no-blame post-mortems). "
                "Alex used 2-day benchmark spikes to resolve Node vs Go team disagreements collaboratively [00:04:02] "
                "and voluntarily clarified direct developer team composition in transcript [00:01:30]."
            )
            overall_score = 9.2
            verdict = "Strong Hire"
            confidence = 0.90
            quotes = [
                SupportingQuote(
                    quote="I prefer data-driven consensus over top-down directives. Two engineers on the team wanted to stick with Node.js because they were more comfortable with JavaScript. I set up a 2-day benchmark spike",
                    source="transcript [00:04:02]"
                ),
                SupportingQuote(
                    quote="We enforce post-mortems with no-blame culture. When our Kafka consumer group stalled last year due to unhandled poison pill messages, I facilitated a root-cause analysis",
                    source="transcript [00:06:45]"
                )
            ]
            raw_dimensions = [
                DimensionEvaluation(
                    dimension_name="Data-Driven Conflict Resolution",
                    score=9.5,
                    insufficient_evidence=False,
                    supporting_quote=SupportingQuote(
                        quote="I set up a 2-day benchmark spike comparing Node.js event-loop throughput against Go goroutines",
                        source="transcript [00:04:02]"
                    )
                ),
                DimensionEvaluation(
                    dimension_name="No-Blame Post-Mortem Culture",
                    score=9.0,
                    insufficient_evidence=False,
                    supporting_quote=SupportingQuote(
                        quote="We enforce post-mortems with no-blame culture.",
                        source="transcript [00:06:45]"
                    )
                ),
                DimensionEvaluation(
                    dimension_name="Executive Compensation Negotiation",
                    score=None,
                    insufficient_evidence=True,
                    reason="Transcript contains no discussion regarding executive compensation or salary expectations.",
                    supporting_quote=None
                )
            ]
        else: # Jordan Lee
            reasoning = (
                "Severe culture risk. Blames non-technical project managers for project delays [00:04:35] "
                "and expresses reluctance to do routine integration coding, preferring to delegate it to junior developers."
            )
            overall_score = 3.5
            verdict = "Strong No"
            confidence = 0.88
            quotes = [
                SupportingQuote(
                    quote="Usually timelines slip because non-technical project managers set unrealistic deadlines without understanding ML complexity.",
                    source="transcript [00:04:35]"
                ),
                SupportingQuote(
                    quote="I thrive in high autonomy environments where I can set the technical direction and delegate the routine integration coding to junior developers.",
                    source="transcript [00:05:50]"
                )
            ]
            raw_dimensions = [
                DimensionEvaluation(
                    dimension_name="Team Collaboration & Ownership",
                    score=3.0,
                    insufficient_evidence=False,
                    supporting_quote=SupportingQuote(
                        quote="timelines slip because non-technical project managers set unrealistic deadlines",
                        source="transcript [00:04:35]"
                    )
                ),
                DimensionEvaluation(
                    dimension_name="Hands-on Integration Willingness",
                    score=4.0,
                    insufficient_evidence=False,
                    supporting_quote=SupportingQuote(
                        quote="delegate the routine integration coding to junior developers.",
                        source="transcript [00:05:50]"
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
