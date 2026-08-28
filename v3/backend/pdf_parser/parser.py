import io
import re
import uuid
from typing import Tuple, List, Dict, Any
from backend.schemas.models import JobDescription

try:
    import fitz
except ImportError:
    fitz = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit
ALLOWED_EXTENSIONS = {".pdf", ".txt"}

class PDFDocumentParser:
    @staticmethod
    def validate_file_input(filename: str, file_bytes: bytes) -> Tuple[bool, str]:
        if not filename:
            return False, "Filename cannot be empty."
        
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            return False, f"Invalid file extension '{ext}'. Only PDF and TXT files are allowed."
        
        if len(file_bytes) == 0:
            return False, "Uploaded file is empty (0 bytes)."
        
        if len(file_bytes) > MAX_FILE_SIZE_BYTES:
            return False, f"File size ({len(file_bytes)/1024/1024:.1f} MB) exceeds maximum allowed limit of 10 MB."
        
        return True, "Valid"

    @staticmethod
    def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> Tuple[str, List[Dict[str, Any]]]:
        if len(pdf_bytes) > MAX_FILE_SIZE_BYTES:
            pdf_bytes = pdf_bytes[:MAX_FILE_SIZE_BYTES]

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

        raw = pdf_bytes.decode('utf-8', errors='ignore')
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        line_map = [{"page": 1, "line_no": i+1, "page_line": i+1, "text": l} for i, l in enumerate(lines)]
        return "\n".join(lines), line_map

    @staticmethod
    def parse_job_description(jd_text: str, job_id: str = None) -> JobDescription:
        lines = [l.strip() for l in jd_text.splitlines() if l.strip()]
        
        # Dynamic Title Extraction
        title = "Target Position"
        company = "Target Company"
        for line in lines[:8]:
            l_clean = line.strip()
            if l_clean.lower().startswith("job description:") and title == "Target Position":
                title = re.sub(r'^job description\s*:\s*', '', l_clean, flags=re.IGNORECASE).strip()
            elif l_clean.lower().startswith("title:") and title == "Target Position":
                title = re.sub(r'^title\s*:\s*', '', l_clean, flags=re.IGNORECASE).strip()
            elif "role:" in l_clean.lower() and title == "Target Position":
                title = re.sub(r'^role\s*:\s*', '', l_clean, flags=re.IGNORECASE).strip()
            elif "company:" in l_clean.lower() and company == "Target Company":
                company = re.sub(r'^company\s*:\s*', '', l_clean, flags=re.IGNORECASE).strip()

        if title == "Target Position" and lines:
            title = lines[0]

        # Dynamic Skills Extraction
        required_skills = []
        responsibilities = []
        qualifications = []

        common_tech_keywords = [
            "Altium", "KiCad", "PCB", "PCB Layout", "Signal Integrity", "Power Integrity", "DFM", "DFA",
            "ESP32", "STM32", "C/C++", "C++", "C", "Firmware", "Schematic Capture", "FPGA", "Verilog", "VHDL",
            "Embedded", "Microcontroller", "ARM", "SPI", "I2C", "UART", "Board Bring-up",
            "Python", "FastAPI", "Go", "Java", "TypeScript", "React", "Node.js",
            "MongoDB", "PostgreSQL", "Kafka", "Redis", "Docker", "Kubernetes", "AWS",
            "PyTorch", "TensorFlow", "LangChain", "LangGraph", "CrewAI", "RAG", "Vector Search",
            "Triton", "OCR", "SQL", "LLM", "Microservices", "REST API"
        ]

        for kw in common_tech_keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', jd_text, re.IGNORECASE):
                if kw not in required_skills:
                    required_skills.append(kw)

        # Dynamic Responsibilities & Qualifications Bullet Extraction
        curr_section = None
        for line in lines:
            l_lower = line.lower()
            if "what you'll do" in l_lower or "responsibilities" in l_lower or "what you will do" in l_lower:
                curr_section = "resp"
                continue
            elif "looking for" in l_lower or "requirements" in l_lower or "qualifications" in l_lower or "required skills" in l_lower:
                curr_section = "qual"
                continue
            elif "what this role is not" in l_lower or "about the role" in l_lower:
                curr_section = None
                continue

            clean_line = line.lstrip("•-* ").strip()
            if curr_section == "resp" and len(clean_line) > 8:
                responsibilities.append(clean_line)
            elif curr_section == "qual" and len(clean_line) > 8:
                qualifications.append(clean_line)
                if len(clean_line) < 60 and clean_line not in required_skills:
                    required_skills.append(clean_line)

        if not required_skills:
            if qualifications:
                required_skills = [q[:45] for q in qualifications[:5]]
            else:
                required_skills = ["Core Engineering Deliverables", "System Architecture", "Technical Execution"]

        return JobDescription(
            job_id=job_id or f"jd_{uuid.uuid4().hex[:6]}",
            title=title,
            company=company,
            required_skills=required_skills[:10],
            responsibilities=responsibilities[:6],
            qualifications=qualifications[:6],
            raw_text=jd_text
        )
