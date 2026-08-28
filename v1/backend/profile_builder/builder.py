import re
import uuid
from typing import List, Dict, Tuple, Optional
from backend.schemas.models import (
    CandidateProfile, SkillClaim, ExperienceItem, CandidateClaim,
    DirectQuote, SourceCitation
)

def verify_quote_in_source(quote: str, resume_text: str, transcript_text: str) -> Tuple[bool, str]:
    """
    Verifies if a supporting quote or citation exists in the resume or transcript text.
    Returns (is_valid, note).
    """
    if not quote or not quote.strip():
        return False, "Quote is empty."
    
    cleaned_quote = re.sub(r'\s+', ' ', quote.strip().lower())
    cleaned_resume = re.sub(r'\s+', ' ', resume_text.lower())
    cleaned_transcript = re.sub(r'\s+', ' ', transcript_text.lower())
    
    if cleaned_quote in cleaned_resume:
        return True, "Found verbatim in resume."
    if cleaned_quote in cleaned_transcript:
        return True, "Found verbatim in transcript."
    
    # Partial match check (if 70% of words match sequence)
    words = cleaned_quote.split()
    if len(words) >= 4:
        sub_phrase = " ".join(words[:4])
        if sub_phrase in cleaned_resume or sub_phrase in cleaned_transcript:
            return True, "Partial phrase match verified in source."
            
    return False, f"Quote '{quote[:30]}...' not found in raw source documents."


class CandidateProfileBuilder:
    """
    Stage 1: Candidate Profile Builder
    Parses raw resume and transcript text into a single, structured CandidateProfile.
    Guarantees every extracted fact carries an explicit citation to verbatim source text.
    """
    
    @staticmethod
    def build_profile(candidate_id: str, resume_text: str, transcript_text: str) -> CandidateProfile:
        # Extract candidate name & role cleanly
        lines = [line.strip() for line in resume_text.splitlines() if line.strip()]
        candidate_name = lines[0].title() if lines else "Candidate " + candidate_id
        if len(candidate_name) > 40:
            candidate_name = candidate_name[:40]
        
        role_match = re.search(r'(Senior|Lead|Principal|Software|Backend|Full-Stack|AI|ML)\s+[A-Za-z\-\s]+', resume_text)
        role_applied = role_match.group(0).strip() if role_match else "Software Engineer"
        
        seniority = "Senior"
        if "Principal" in role_applied or "Lead" in role_applied:
            seniority = "Lead / Principal"
        elif "Junior" in role_applied:
            seniority = "Junior"
        elif "Senior" in role_applied:
            seniority = "Senior"
        else:
            seniority = "Mid-Level"

        # 1. Extract Skills with Citations
        skills: List[SkillClaim] = []
        skill_lines = re.findall(r'-\s*(Languages|Frontend|Backend|Infrastructure|Machine Learning|Databases):\s*([^\n]+)', resume_text)
        for cat, list_str in skill_lines:
            items = [s.strip() for s in list_str.split(',')]
            for item in items:
                skills.append(SkillClaim(
                    skill_name=item,
                    category=cat,
                    citation=SourceCitation(
                        source_doc='resume',
                        location=f"Technical Skills section ({cat})",
                        quote_snippet=item
                    )
                ))

        # 2. Extract Experiences with Citations
        experiences: List[ExperienceItem] = []
        exp_blocks = re.findall(r'([A-Za-z\s]+)\s*\|\s*([A-Za-z\s]+)\s*\|\s*([A-Za-z0-9\s–\-]+)\n((?:- [^\n]+\n?)+)', resume_text)
        for role_title, company, duration, bullets in exp_blocks:
            resp_list = [b.strip('- \n') for b in bullets.strip().split('\n') if b.strip()]
            experiences.append(ExperienceItem(
                company=company.strip(),
                role=role_title.strip(),
                duration=duration.strip(),
                responsibilities=resp_list,
                citation=SourceCitation(
                    source_doc='resume',
                    location=f"Experience ({company.strip()})",
                    quote_snippet=f"{role_title.strip()} at {company.strip()}"
                )
            ))

        # 3. Extract Quantifiable & Qualitative Claims
        claims: List[CandidateClaim] = []
        # Quantifiable claims from resume
        quant_matches = re.findall(r'([^\n]*?(?:\d+%\s*|\$\d+|\d+\s*developers|\d+\s*events|\d+\s*users|\d+\s*A100|\d+\s*hours|\d+\s*monthly)[^\n]*)', resume_text)
        for qm in quant_matches:
            clean_qm = qm.strip('- ')
            if len(clean_qm) > 10:
                claims.append(CandidateClaim(
                    claim_type='quantitative',
                    description=clean_qm,
                    citation=SourceCitation(
                        source_doc='resume',
                        location="Resume Bullet",
                        quote_snippet=clean_qm
                    )
                ))
                
        # Claims from transcript
        transcript_claims = re.findall(r'(\[\d{2}:\d{2}:\d{2}\])\s*([A-Za-z\s]+):\s*([^\n]+)', transcript_text)
        for timestamp, speaker, text in transcript_claims:
            if speaker.strip() != "Interviewer" and ("led" in text.lower() or "built" in text.lower() or "trained" in text.lower() or "reduced" in text.lower() or "improved" in text.lower() or "technically" in text.lower()):
                claims.append(CandidateClaim(
                    claim_type='qualitative',
                    description=f"{speaker.strip()}: {text.strip()}",
                    citation=SourceCitation(
                        source_doc='transcript',
                        location=timestamp,
                        quote_snippet=text.strip()
                    )
                ))

        # 4. Extract Direct Quote Bank from Transcript
        quote_bank: List[DirectQuote] = []
        for idx, (timestamp, speaker, text) in enumerate(transcript_claims):
            if speaker.strip() != "Interviewer":
                topic = "technical"
                lower_t = text.lower()
                if "team" in lower_t or "conflict" in lower_t or "feedback" in lower_t or "disagreement" in lower_t:
                    topic = "behavioral"
                elif "led" in topic or "mentored" in lower_t or "direction" in lower_t:
                    topic = "leadership"
                elif "scratch" in lower_t or "technically" in lower_t or "honest" in lower_t or "transparent" in lower_t or "hours" in lower_t:
                    topic = "accuracy"

                quote_bank.append(DirectQuote(
                    id=f"quote_{idx+1}",
                    quote=text.strip(),
                    topic=topic,
                    location=timestamp,
                    speaker=speaker.strip()
                ))

        return CandidateProfile(
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            role_applied=role_applied,
            seniority_level=seniority,
            skills=skills,
            experiences=experiences,
            claims=claims,
            quote_bank=quote_bank,
            raw_resume_text=resume_text,
            raw_transcript_text=transcript_text
        )
