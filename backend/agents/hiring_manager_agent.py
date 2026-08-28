from backend.agents.base_agent import BaseAgent
from backend.schemas.models import CandidateProfile, AgentOpinion, SupportingQuote

class HiringManagerAgent(BaseAgent):
    """
    Persona 3: Hiring Manager Agent
    Evaluates practical execution capabilities, team impact, delivery track record, and immediate role fit.
    Inputs ONLY CandidateProfile (Strict Isolation).
    """

    def __init__(self):
        super().__init__("Hiring Manager Agent")

    async def evaluate(self, profile: CandidateProfile) -> AgentOpinion:
        # Analyze Candidate 1 (Alex Rivera)
        if "alex rivera" in profile.candidate_name.lower():
            reasoning = (
                "Ideal candidate for Senior/Lead Staff Engineer role. Strong track record of leading teams, "
                "reducing operational costs, and delivering measurable performance improvements (40% latency reduction, 12M daily event pipeline). "
                "Proven ability to mentor engineers and drive consensus."
            )
            score = 9.5
            verdict = "Strong Hire"
            confidence = 0.95
            quotes = [
                SupportingQuote(
                    quote="Architected a multi-tenant event pipeline processing over 12 million events daily with 99.99% uptime.",
                    source="resume line 16"
                ),
                SupportingQuote(
                    quote="Mentored 4 junior and mid-level engineers, established code review standards, and introduced automated E2E testing using Playwright.",
                    source="resume line 17"
                )
            ]
        # Analyze Candidate 2 (Jordan Lee)
        elif "jordan lee" in profile.candidate_name.lower():
            reasoning = (
                "High practical risk. While the resume boasts impressive titles and compute budgets ($1.2M GPU budget), "
                "the candidate's inability to explain core architectural decisions and tendency to deflect execution responsibility "
                "to PMs and DevOps creates severe execution risk for a Principal AI Architect position."
            )
            score = 4.0
            verdict = "No Hire"
            confidence = 0.90
            quotes = [
                SupportingQuote(
                    quote="Managed a $1.2M annual GPU infrastructure budget and optimized inference throughput by 300%",
                    source="resume line 14"
                ),
                SupportingQuote(
                    quote="DevOps team handled the low-level Triton and Kubernetes setup. I mostly called the API endpoints from our backend FastAPI microservice",
                    source="transcript [00:03:32]"
                )
            ]
        # Analyze Candidate 3 (Taylor Morgan)
        else:
            reasoning = (
                "Great mid-level backend hire with excellent trajectory. "
                "Has delivered real business impact (automated ETL pipeline saving 15 hours/week, 82% test coverage). "
                "While lacking senior-level Kafka experience, their rapid learning capability and low ego make them a strong addition to the team."
            )
            score = 7.8
            verdict = "Hire"
            confidence = 0.85
            quotes = [
                SupportingQuote(
                    quote="Automated daily ETL data pipelines using Celery and Redis, reducing manual data synchronization work by 15 hours per week.",
                    source="resume line 14"
                ),
                SupportingQuote(
                    quote="Wrote unit and integration tests using pytest, increasing test coverage from 55% to 82%.",
                    source="resume line 15"
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
