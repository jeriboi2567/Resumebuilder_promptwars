import asyncio
from typing import Dict
from backend.schemas.models import CandidateProfile, JobDescription, IndependentOpinionsV2, AgentOpinionV2
from backend.agents.technical_agent import TechnicalAgentV2
from backend.agents.hr_culture_agent import HRCultureAgentV2
from backend.agents.hiring_manager_agent import HiringManagerAgentV2
from backend.agents.skeptic_agent import SkepticAgentV2

async def run_stage2_independent_opinions_v2(
    profile: CandidateProfile,
    jd: JobDescription
) -> IndependentOpinionsV2:
    agents = [
        TechnicalAgentV2(),
        HRCultureAgentV2(),
        HiringManagerAgentV2(),
        SkepticAgentV2()
    ]

    results: list[AgentOpinionV2] = await asyncio.gather(
        *(agent.evaluate(profile, jd) for agent in agents)
    )

    opinions_dict: Dict[str, AgentOpinionV2] = {
        opinion.agent_name: opinion for opinion in results
    }

    return IndependentOpinionsV2(
        candidate_id=profile.candidate_id,
        opinions=opinions_dict
    )
