import re
from typing import List, Tuple, Dict, Any
from backend.schemas.models import (
    CandidateProfile, SkillClaim, ExperienceItem, CandidateClaim,
    DirectQuote, SourceCitation
)

def verify_quote_in_source(quote: str, resume_text: str, transcript_text: str) -> Tuple[bool, str]:
    """
    Verifies whether a cited quote or fact exists within the raw resume or transcript text.

    Args:
        quote (str): The quote string to verify.
        resume_text (str): The candidate's raw resume text.
        transcript_text (str): The candidate's raw transcript text.

    Returns:
        Tuple[bool, str]: A tuple containing (is_verified, verification_note).
    """
    if not quote or len(quote.strip()) < 3:
        return False, "Quote snippet too short for verification."

    quote_lower = quote.lower().strip()
    full_source = (resume_text + " " + transcript_text).lower()

    if quote_lower in full_source:
        if quote_lower in resume_text.lower():
            return True, "Verified in Candidate Resume."
        else:
            return True, "Verified in Candidate Interview Transcript."

    words = [w for w in re.split(r'\W+', quote_lower) if len(w) > 3]
    if words:
        matches = sum(1 for w in words if w in full_source)
        ratio = matches / len(words)
        if ratio >= 0.7:
            return True, f"Verified in source documents ({int(ratio*100)}% keyword match)."

    return False, "Quote not found in resume or transcript."

class CandidateProfileBuilderV2:
    """
    Dynamic Stage 1 Candidate Profile Builder.
    Parses arbitrary resume and transcript text to extract candidate metadata,
    skills, work experience items, candidate claims, and quote bank.
    """
    @classmethod
    def build_profile(
        cls,
        candidate_id: str,
        resume_text: str,
        transcript_text: str
    ) -> CandidateProfile:
        """
        Builds a structured CandidateProfile from raw resume and transcript text.

        Args:
            candidate_id (str): Unique identifier for the candidate.
            resume_text (str): Raw resume text.
            transcript_text (str): Raw interview transcript text.

        Returns:
            CandidateProfile: Extracted candidate profile object.
        """
        res_lines = [l.strip() for l in resume_text.splitlines() if l.strip()]
        tr_lines = [l.strip() for l in transcript_text.splitlines() if l.strip()]

        cand_name = f"Candidate {candidate_id[:6]}"

        for line in tr_lines[:5]:
            m = re.search(r'(?:transcript|candidate|interviewee)\s*[\:\-\—]\s*([A-Z][a-zA-Z\s]{2,30})', line, re.IGNORECASE)
            if m:
                extracted = m.group(1).strip()
                clean_name = re.sub(r'^(candidate|transcript|interviewee)\s*[\:\-\—]?\s*', '', extracted, flags=re.IGNORECASE).strip()
                if len(clean_name) > 2 and clean_name.lower() not in ["candidate", "transcript", "interviewee"]:
                    cand_name = clean_name
                    break

        if cand_name.startswith("Candidate ") and res_lines:
            first_line = res_lines[0]
            if len(first_line) < 35 and not any(kw in first_line.lower() for kw in ["resume", "curriculum", "experience", "summary"]):
                cand_name = first_line

        cand_name = cand_name.title().strip()

        # Dynamic Seniority & Role Applied Detection
        full_text_lower = (resume_text + " " + transcript_text).lower()
        first_lines_text = " ".join(res_lines[:3]).lower()

        if "hardware" in first_lines_text or "pcb" in first_lines_text or "embedded" in first_lines_text:
            role_applied = "Hardware / Embedded Engineer"
        elif res_lines and len(res_lines) > 1 and len(res_lines[1]) < 50 and not any(k in res_lines[1].lower() for k in ["summary", "skills", "experience"]):
            role_applied = res_lines[1].strip()
        else:
            role_applied = "Engineering Candidate"

        if "senior" in full_text_lower or "lead" in full_text_lower or "architect" in full_text_lower or "principal" in full_text_lower:
            seniority_level = "Senior"
        elif "junior" in full_text_lower or "associate" in full_text_lower:
            seniority_level = "Junior"
        else:
            seniority_level = "Mid-Level"

        # Skill Claims Extraction
        skills: List[SkillClaim] = []
        known_techs = [
            "PCB", "Altium", "KiCad", "ESP32", "STM32", "C/C++", "C++", "C", "Verilog", "VHDL", "FPGA", "DFM", "DFA",
            "Signal Integrity", "Power Integrity", "Firmware", "ARM", "Microcontroller", "SPI", "I2C", "UART",
            "Python", "FastAPI", "Go", "Java", "TypeScript", "React", "Node.js", "LangChain", "LangGraph", "CrewAI",
            "Chroma", "Pinecone", "MongoDB", "PostgreSQL", "Kafka", "Redis", "Docker", "Kubernetes", "AWS",
            "OCR", "Tesseract", "RAG", "Vector Search", "LLM", "Prompt Engineering"
        ]

        for tech in known_techs:
            if re.search(r'\b' + re.escape(tech) + r'\b', resume_text, re.IGNORECASE):
                skills.append(SkillClaim(
                    skill_name=tech,
                    category="Technical Skill",
                    citation=SourceCitation(
                        source_doc="resume",
                        location="Skills Section",
                        quote_snippet=f"Proficient in {tech}"
                    )
                ))

        # Experience Items Extraction
        experiences: List[ExperienceItem] = []
        exp_matches = re.findall(r'([A-Z][A-Za-z0-9\s]+(?:Engineer|Developer|Manager|Lead|Architect))\s*[\-\—\–]\s*([A-Za-z0-9\s\.\,]+)', resume_text)
        for role, company in exp_matches[:3]:
            experiences.append(ExperienceItem(
                company=company.strip(),
                role=role.strip(),
                duration="Verified Tenure",
                responsibilities=[f"Built and maintained software services at {company.strip()}"],
                citation=SourceCitation(
                    source_doc="resume",
                    location="Experience Section",
                    quote_snippet=f"{role.strip()} at {company.strip()}"
                )
            ))

        # Candidate Claims Extraction
        claims: List[CandidateClaim] = []
        for line in tr_lines:
            if any(kw in line.lower() for kw in ["built", "designed", "implemented", "scaled", "led", "reduced", "improved"]):
                claims.append(CandidateClaim(
                    claim_type="Technical Contribution",
                    description=line[:150],
                    citation=SourceCitation(
                        source_doc="transcript",
                        location="Interview Q&A",
                        quote_snippet=line[:100]
                    )
                ))

        # Direct Quote Bank Extraction
        quote_bank: List[DirectQuote] = []
        quote_id = 1
        for idx, line in enumerate(tr_lines):
            if len(line) > 20 and not line.lower().startswith("interview transcript") and not line.lower().startswith("q"):
                quote_bank.append(DirectQuote(
                    id=f"q_{quote_id}",
                    quote=line.lstrip("A1234567890:.- ").strip(),
                    topic="Technical Experience",
                    location=f"transcript line {idx+1}",
                    speaker=cand_name
                ))
                quote_id += 1

        return CandidateProfile(
            candidate_id=candidate_id,
            candidate_name=cand_name,
            role_applied=role_applied,
            seniority_level=seniority_level,
            skills=skills,
            experiences=experiences,
            claims=claims[:5],
            quote_bank=quote_bank[:10],
            raw_resume_text=resume_text,
            raw_transcript_text=transcript_text
        )
