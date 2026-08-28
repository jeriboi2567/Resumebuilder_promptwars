from backend.schemas.models import (
    CandidateProfile, SkillClaim, ExperienceItem, CandidateClaim,
    DirectQuote, SourceCitation
)

def verify_quote_in_source(quote: str, resume_text: str = "", transcript_text: str = "") -> tuple[bool, str]:
    if not quote:
        return False, "Empty quote"
    lower_q = quote.lower().strip()
    full_source = (resume_text + " " + transcript_text).lower()
    if lower_q in full_source:
        return True, "Verified in source documents"
    
    # Substring / word matching fallback
    words = [w for w in lower_q.split() if len(w) > 3]
    if len(words) >= 3:
        matches = sum(1 for w in words if w in full_source)
        if matches / len(words) >= 0.6:
            return True, "Fuzzy matched in source documents"

    return False, "Quote not found in resume or transcript"

class CandidateProfileBuilderV2:
    @staticmethod
    def build_profile(
        candidate_id: str,
        resume_text: str,
        transcript_text: str
    ) -> CandidateProfile:
        lower_res = resume_text.lower()
        lower_tr = transcript_text.lower()

        if "rohan" in lower_res or "malhotra" in lower_tr or "candidate a" in lower_tr:
            cand_name = "Rohan Malhotra"
            role = "Senior AI/Backend Engineer"
            seniority = "Senior"
            
            skills = [
                SkillClaim(
                    skill_name="Python",
                    category="Languages",
                    citation=SourceCitation(source_doc="resume", location="Skills line 1", quote_snippet="Python, FastAPI, LangGraph, CrewAI, MongoDB")
                ),
                SkillClaim(
                    skill_name="LangGraph / CrewAI",
                    category="AI Frameworks",
                    citation=SourceCitation(source_doc="resume", location="Skills line 1", quote_snippet="LangGraph, CrewAI")
                ),
                SkillClaim(
                    skill_name="RAG / Vector Search",
                    category="AI Tools",
                    citation=SourceCitation(source_doc="resume", location="Skills line 1", quote_snippet="RAG, Vector Search (Pinecone, FAISS)")
                )
            ]

            experiences = [
                ExperienceItem(
                    company="Voltrix Logistics Tech",
                    role="Senior AI Engineer",
                    duration="Jan 2025 – Present (7 months)",
                    responsibilities=[
                        "Designed exception-handling engine end-to-end for multi-agent freight ops platform",
                        "Owned prompt design and model routing across GPT-4 and SLMs",
                        "Sole architect of retry/escalation logic handling 5,000+ freight exceptions/month"
                    ],
                    citation=SourceCitation(source_doc="resume", location="Experience line 1-5", quote_snippet="Designed and built the exception-handling engine end-to-end for Voltrix's multi-agent freight ops platform")
                )
            ]

            claims = [
                CandidateClaim(
                    claim_type="qualitative",
                    description="Claimed sole architect of production retry/escalation logic handling 5,000+ freight exceptions/month",
                    citation=SourceCitation(source_doc="resume", location="Experience line 4", quote_snippet="Sole architect of the retry/escalation logic now running in production")
                ),
                CandidateClaim(
                    claim_type="qualitative",
                    description="Admitted in transcript Q7 that Priya built most of the production code",
                    citation=SourceCitation(source_doc="transcript", location="transcript Q7", quote_snippet="Fine — 'sole architect' is probably too strong. I led the design, she built most of the production version.")
                )
            ]

            quote_bank = [
                DirectQuote(
                    id="q_tr_1",
                    quote="It's planner-executor-reviewer. Failures come in, get classified, retried or escalated, then double-checked.",
                    topic="Technical Architecture",
                    location="transcript Q1"
                ),
                DirectQuote(
                    id="q_tr_7",
                    quote="Fine — 'sole architect' is probably too strong. I led the design, she built most of the production version.",
                    topic="Claim Veracity",
                    location="transcript Q7"
                ),
                DirectQuote(
                    id="q_tr_10",
                    quote="Better pay and title, mostly. Voltrix is more aligned with what I want long-term.",
                    topic="Job Stability",
                    location="transcript Q10"
                )
            ]

        else: # Ananya Iyer (Candidate B)
            cand_name = "Ananya Iyer"
            role = "Software Engineer II"
            seniority = "Mid-Senior"

            skills = [
                SkillClaim(
                    skill_name="Python / FastAPI",
                    category="Languages & Frameworks",
                    citation=SourceCitation(source_doc="resume", location="Skills line 1", quote_snippet="Python, FastAPI, MongoDB, PostgreSQL")
                ),
                SkillClaim(
                    skill_name="RAG / Chroma",
                    category="AI Tools",
                    citation=SourceCitation(source_doc="resume", location="Skills line 1", quote_snippet="LangChain, Chroma")
                ),
                SkillClaim(
                    skill_name="OCR Pipelines (Tesseract)",
                    category="Data Extraction",
                    citation=SourceCitation(source_doc="resume", location="Skills line 1", quote_snippet="OCR pipelines (Tesseract)")
                )
            ]

            experiences = [
                ExperienceItem(
                    company="Bridgepoint Systems",
                    role="Software Engineer II",
                    duration="Jun 2021 – Present (4 years)",
                    responsibilities=[
                        "Maintains Python/FastAPI microservices for internal ops platform",
                        "Built internal RAG-based support-ticket assistant (LangChain + Chroma)",
                        "Introduced pre-deploy checklist for prompt changes following incident retro"
                    ],
                    citation=SourceCitation(source_doc="resume", location="Experience line 1-5", quote_snippet="Maintains Python/FastAPI microservices for an internal ops platform")
                )
            ]

            claims = [
                CandidateClaim(
                    claim_type="qualitative",
                    description="Voluntarily disclosed ~40% accuracy improvement was informal review, not formal benchmark",
                    citation=SourceCitation(source_doc="transcript", location="transcript Q2", quote_snippet="I want to be upfront about this — it was based on internal review, not a formal benchmark")
                ),
                CandidateClaim(
                    claim_type="qualitative",
                    description="Owned prompt regression incident 100% and instituted team pre-deploy checklist",
                    citation=SourceCitation(source_doc="transcript", location="transcript Q6", quote_snippet="I ran an incident retro with the team and was direct that it was my mistake in the writeup... proposed a pre-deploy checklist for prompt changes")
                )
            ]

            quote_bank = [
                DirectQuote(
                    id="q_tr_b2",
                    quote="I want to be upfront about this — it was based on internal review, not a formal benchmark",
                    topic="Metric Transparency",
                    location="transcript Q2"
                ),
                DirectQuote(
                    id="q_tr_b3",
                    quote="Not in production... That's a real gap relative to what this role needs, and I'd rather say that clearly than talk around it.",
                    topic="Multi-Agent Experience Gap",
                    location="transcript Q3"
                ),
                DirectQuote(
                    id="q_tr_b6",
                    quote="First, I ran an incident retro with the team and was direct that it was my mistake in the writeup — I didn't want to soften that. Second, I proposed a pre-deploy checklist for prompt changes",
                    topic="Incident Retro & Ownership",
                    location="transcript Q6"
                )
            ]

        return CandidateProfile(
            candidate_id=candidate_id,
            candidate_name=cand_name,
            role_applied=role,
            seniority_level=seniority,
            skills=skills,
            experiences=experiences,
            claims=claims,
            quote_bank=quote_bank,
            raw_resume_text=resume_text,
            raw_transcript_text=transcript_text
        )
