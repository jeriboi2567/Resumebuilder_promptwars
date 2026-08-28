import re
import io
from typing import Tuple, List, Dict
from backend.schemas.models import JobDescription

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

class PDFDocumentParser:
    """
    V2 PDF Ingestion Engine.
    Extracts text from PDF files using pdfplumber / PyMuPDF while preserving
    page numbers and line coordinates so SourceCitations remain meaningful.
    """

    @staticmethod
    def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Extracts text from PDF bytes.
        Returns (full_text, line_map where line_map is list of {page, line_no, text}).
        """
        full_text_lines = []
        line_map = []

        if fitz is not None:
            try:
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                current_line_no = 1
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text = page.get_text()
                    lines = text.splitlines()
                    for idx, line in enumerate(lines):
                        clean = line.strip()
                        if clean:
                            full_text_lines.append(clean)
                            line_map.append({
                                "page": page_num + 1,
                                "line_no": current_line_no,
                                "page_line": idx + 1,
                                "text": clean
                            })
                            current_line_no += 1
                doc.close()
                if full_text_lines:
                    return "\n".join(full_text_lines), line_map
            except Exception:
                pass

        if pdfplumber is not None:
            try:
                with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                    current_line_no = 1
                    for page_num, page in enumerate(pdf.pages):
                        text = page.extract_text() or ""
                        lines = text.splitlines()
                        for idx, line in enumerate(lines):
                            clean = line.strip()
                            if clean:
                                full_text_lines.append(clean)
                                line_map.append({
                                    "page": page_num + 1,
                                    "line_no": current_line_no,
                                    "page_line": idx + 1,
                                    "text": clean
                                })
                                current_line_no += 1
                if full_text_lines:
                    return "\n".join(full_text_lines), line_map
            except Exception:
                pass

        # Fallback for plain text bytes
        raw = pdf_bytes.decode('utf-8', errors='ignore')
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        line_map = [{"page": 1, "line_no": i+1, "page_line": i+1, "text": l} for i, l in enumerate(lines)]
        return "\n".join(lines), line_map

    @staticmethod
    def parse_job_description(jd_text: str) -> JobDescription:
        """
        Parses Job Description text into structured JobDescription requirements.
        """
        lines = [l.strip() for l in jd_text.splitlines() if l.strip()]
        title = "Software Engineer"
        for line in lines[:5]:
            if "JOB DESCRIPTION" in line.upper() or "ROLE:" in line.upper() or "TITLE:" in line.upper() or "ENGINEER" in line.upper():
                title = re.sub(r'^(JOB DESCRIPTION:\s*|ROLE:\s*|TITLE:\s*)', '', line, flags=re.IGNORECASE).strip()
                break

        # Extract required skills
        skills = []
        skills_match = re.findall(r'(?:Python|Go|TypeScript|JavaScript|PostgreSQL|Redis|Kafka|Kubernetes|Docker|AWS|PyTorch|TensorFlow|vLLM|DeepSpeed|RAG)', jd_text, re.IGNORECASE)
        for s in set(skills_match):
            skills.append(s.strip())

        # Extract responsibilities
        resp = []
        resp_matches = re.findall(r'-\s*([^\n]+)', jd_text)
        for r in resp_matches:
            if len(r.strip()) > 10:
                resp.append(r.strip())

        # Extract qualifications
        qual = []
        qual_matches = re.findall(r'\d+\.\s*([^\n]+)', jd_text)
        for q in qual_matches:
            qual.append(q.strip())

        return JobDescription(
            title=title,
            company="Promptwars Inc.",
            required_skills=sorted(list(set(skills))),
            responsibilities=resp,
            qualifications=qual,
            raw_text=jd_text
        )
