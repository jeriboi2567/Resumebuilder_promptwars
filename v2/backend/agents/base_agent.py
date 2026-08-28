from abc import ABC, abstractmethod
from typing import List, Tuple
from backend.schemas.models import (
    CandidateProfile, JobDescription, AgentOpinionV2, SupportingQuote, DimensionEvaluation
)
from backend.profile_builder.builder import verify_quote_in_source

class BaseAgentV2(ABC):
    """
    Abstract Base Class for Stage 2 V2 Agents.
    Enforces strict isolation: evaluate() accepts ONLY (profile: CandidateProfile, jd: JobDescription).
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def evaluate(self, profile: CandidateProfile, jd: JobDescription) -> AgentOpinionV2:
        pass

    def validate_quotes(self, quotes: List[SupportingQuote], profile: CandidateProfile) -> List[SupportingQuote]:
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

    def validate_dimensions(
        self,
        dimensions: List[DimensionEvaluation],
        profile: CandidateProfile
    ) -> Tuple[List[DimensionEvaluation], List[str]]:
        """
        Enforces Section B Insufficient Evidence Rule:
        If a dimension lacks a verified supporting quote, forces insufficient_evidence=True
        and appends dimension to insufficient_dimensions.
        """
        validated_dims: List[DimensionEvaluation] = []
        insufficient_list: List[str] = []

        for dim in dimensions:
            if dim.insufficient_evidence or dim.supporting_quote is None:
                validated_dims.append(DimensionEvaluation(
                    dimension_name=dim.dimension_name,
                    score=None,
                    insufficient_evidence=True,
                    reason=dim.reason or f"Source documents do not contain evidence for {dim.dimension_name}.",
                    supporting_quote=None
                ))
                insufficient_list.append(dim.dimension_name)
            else:
                is_valid, note = verify_quote_in_source(
                    dim.supporting_quote.quote, profile.raw_resume_text, profile.raw_transcript_text
                )
                if not is_valid:
                    # Quote check failed - convert to insufficient_evidence
                    validated_dims.append(DimensionEvaluation(
                        dimension_name=dim.dimension_name,
                        score=None,
                        insufficient_evidence=True,
                        reason=f"Quote validation failed for {dim.dimension_name}: {note}",
                        supporting_quote=None
                    ))
                    insufficient_list.append(dim.dimension_name)
                else:
                    validated_dims.append(dim)

        return validated_dims, insufficient_list
