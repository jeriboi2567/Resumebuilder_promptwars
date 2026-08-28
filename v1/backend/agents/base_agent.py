import os
import json
import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from backend.schemas.models import CandidateProfile, AgentOpinion, SupportingQuote
from backend.profile_builder.builder import verify_quote_in_source

class BaseAgent(ABC):
    """
    Abstract Base Class for Stage 2 Independent Agents.
    Guarantees strict architectural isolation: evaluate() only takes CandidateProfile as input.
    """
    
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def evaluate(self, profile: CandidateProfile) -> AgentOpinion:
        """
        Evaluate candidate profile in complete isolation.
        No other agent opinions are passed here.
        """
        pass

    def validate_quotes(self, quotes: List[SupportingQuote], profile: CandidateProfile) -> List[SupportingQuote]:
        """
        Validation pass enforcing that every supporting quote exists in source documents.
        """
        validated: List[SupportingQuote] = []
        for q in quotes:
            is_valid, note = verify_quote_in_source(
                q.quote, profile.raw_resume_text, profile.raw_transcript_text
            )
            validated.append(SupportingQuote(
                quote=q.quote,
                source=q.source,
                verified=is_valid,
                verification_note=note
            ))
        return validated
