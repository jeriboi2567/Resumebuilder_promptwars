from abc import ABC, abstractmethod
from typing import List, Tuple
from backend.schemas.models import (
    CandidateProfile, JobDescription, AgentOpinionV2, SupportingQuote, DimensionEvaluation
)
from backend.profile_builder.builder import verify_quote_in_source

class BaseAgentV2(ABC):
    """
    Abstract Base Agent class for Stage 2 isolated persona evaluation.
    Provides verified quote verification and Section B insufficient evidence enforcement.
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def evaluate(self, profile: CandidateProfile, jd: JobDescription) -> AgentOpinionV2:
        """
        Evaluates a candidate profile against a Job Description in strict isolation.

        Args:
            profile (CandidateProfile): Candidate profile object.
            jd (JobDescription): Target Job Description object.

        Returns:
            AgentOpinionV2: The agent persona's independent opinion.
        """
        pass

    def validate_quotes(self, quotes: List[SupportingQuote], profile: CandidateProfile) -> List[SupportingQuote]:
        """
        Validates cited quotes against candidate source documents.

        Args:
            quotes (List[SupportingQuote]): Cited supporting quotes.
            profile (CandidateProfile): Candidate profile object.

        Returns:
            List[SupportingQuote]: Validated supporting quotes with verification notes.
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

    def validate_dimensions(
        self,
        dimensions: List[DimensionEvaluation],
        profile: CandidateProfile
    ) -> Tuple[List[DimensionEvaluation], List[str]]:
        """
        Enforces Section B Rule:
        Any dimension that lacks verified source evidence MUST have insufficient_evidence=True
        and score=None with a reason string.

        Args:
            dimensions (List[DimensionEvaluation]): Dimension evaluations list.
            profile (CandidateProfile): Candidate profile object.

        Returns:
            Tuple[List[DimensionEvaluation], List[str]]: Validated dimensions and unassessed names list.
        """
        validated_dims: List[DimensionEvaluation] = []
        insufficient_names: List[str] = []

        for dim in dimensions:
            if dim.insufficient_evidence or dim.supporting_quote is None:
                dim_obj = DimensionEvaluation(
                    dimension_name=dim.dimension_name,
                    score=None,
                    insufficient_evidence=True,
                    reason=dim.reason or f"Source documents contain no verified quote or factual evidence for {dim.dimension_name}.",
                    supporting_quote=None
                )
                validated_dims.append(dim_obj)
                insufficient_names.append(dim.dimension_name)
            else:
                is_valid, _ = verify_quote_in_source(
                    dim.supporting_quote.quote,
                    profile.raw_resume_text,
                    profile.raw_transcript_text
                )
                if not is_valid:
                    dim_obj = DimensionEvaluation(
                        dimension_name=dim.dimension_name,
                        score=None,
                        insufficient_evidence=True,
                        reason=f"Supporting quote '{dim.supporting_quote.quote}' could not be verified in source documents.",
                        supporting_quote=None
                    )
                    validated_dims.append(dim_obj)
                    insufficient_names.append(dim.dimension_name)
                else:
                    validated_dims.append(dim)

        return validated_dims, insufficient_names
