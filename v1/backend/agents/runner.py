import asyncio
from typing import Dict
from backend.schemas.models import CandidateProfile, IndependentOpinions, AgentOpinion
from backend.agents.technical_agent import TechnicalAgent
from backend.agents.hr_culture_agent import HRCultureAgent
from backend.agents.hiring_manager_agent import HiringManagerAgent
from backend.agents.skeptic_agent import SkepticAgent

async def run_stage2_independent_opinions(profile: CandidateProfile) -> IndependentOpinions:
    """
    Executes Stage 2: Independent Agent Opinions.
    Runs 4 isolated agent personas concurrently using asyncio.gather.
    No agent function accepts or sees the opinions of other agents.
    """
    agents = [
        TechnicalAgent(),
        HRCultureAgent(),
        HiringManagerAgent(),
        SkepticAgent()
    ]

    # Execute all 4 isolated calls in parallel
    results: list[AgentOpinion] = await asyncio.gather(
        *(agent.evaluate(profile) for agent in agents)
    )

    opinions_dict: Dict[str, AgentOpinion] = {
        opinion.agent_name: opinion for opinion in results
    }

    return IndependentOpinions(
        candidate_id=profile.candidate_id,
        opinions=opinions_dict
    )
