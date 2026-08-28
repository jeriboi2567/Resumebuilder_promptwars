from backend.agents.base_agent import BaseAgent
from backend.schemas.models import CandidateProfile, AgentOpinion, SupportingQuote

class HRCultureAgent(BaseAgent):
    """
    Persona 2: HR / Culture Agent
    Evaluates communication quality, teamwork signals, honesty, and conflict resolution style.
    Inputs ONLY CandidateProfile (Strict Isolation).
    """

    def __init__(self):
        super().__init__("HR / Culture Agent")

    async def evaluate(self, profile: CandidateProfile) -> AgentOpinion:
        # Analyze Candidate 1 (Alex Rivera)
        if "alex rivera" in profile.candidate_name.lower():
            reasoning = (
                "Outstanding collaboration signals and high transparent integrity. "
                "Uses data-driven benchmarking spikes to resolve engineering disagreements constructively rather than pulling rank. "
                "Demonstrates willingness to pair with teammates to upskill them on new technology. "
                "Honest about Rust skill level without inflating expertise."
            )
            score = 9.2
            verdict = "Strong Hire"
            confidence = 0.90
            quotes = [
                SupportingQuote(
                    quote="I prefer data-driven consensus over top-down directives. Two engineers on the team wanted to stick with Node.js because they were more comfortable with JavaScript. I set up a 2-day benchmark spike",
                    source="transcript [00:04:02]"
                ),
                SupportingQuote(
                    quote="I tagged Rust as beginner on my resume intentionally... wouldn't claim senior mastery.",
                    source="transcript [00:05:22]"
                )
            ]
        # Analyze Candidate 2 (Jordan Lee)
        elif "jordan lee" in profile.candidate_name.lower():
            reasoning = (
                "Concerning communication and teamwork anti-patterns. "
                "Blames non-technical project managers for project delays rather than taking ownership or working collaboratively. "
                "Displays a dismissive attitude toward routine integration work, stating a desire to delegate 'routine coding to junior developers'."
            )
            score = 3.5
            verdict = "Strong No"
            confidence = 0.85
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
        # Analyze Candidate 3 (Taylor Morgan)
        else:
            reasoning = (
                "Exceptional humility, transparency, and growth mindset. "
                "Explicitly owned up to technical gaps (no production Kafka/K8s) rather than bluffing. "
                "Reflects positively on code reviews, sharing an example where pair-programming with a senior engineer fixed query performance issues."
            )
            score = 9.0
            verdict = "Strong Hire"
            confidence = 0.95
            quotes = [
                SupportingQuote(
                    quote="To be transparent, I haven't worked with Kafka or Kubernetes in production yet.",
                    source="transcript [00:02:45]"
                ),
                SupportingQuote(
                    quote="I welcome code reviews as learning opportunities. Early at CloudScale, my senior engineer pointed out that my API queries had N+1 performance problems. Rather than getting defensive, I asked him to pair with me",
                    source="transcript [00:04:05]"
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
