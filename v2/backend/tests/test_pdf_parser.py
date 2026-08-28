import pytest
from backend.pdf_parser.parser import PDFDocumentParser

def test_pdf_document_parser_text_extraction():
    sample_pdf_text = "JOB DESCRIPTION: Senior Staff Engineer\nRequired Skills: Python, Go, Kafka\n1. 6+ years experience with PostgreSQL."
    text, line_map = PDFDocumentParser.extract_text_from_pdf_bytes(sample_pdf_text.encode('utf-8'))

    assert "Senior Staff Engineer" in text
    assert len(line_map) >= 3
    assert line_map[0]["line_no"] == 1

def test_parse_job_description():
    jd_text = "JOB DESCRIPTION: Senior Staff Software & AI Infrastructure Engineer\nRequired Skills: Python, Go, Kafka, Redis, PyTorch"
    jd = PDFDocumentParser.parse_job_description(jd_text)

    assert "Senior Staff" in jd.title
    assert "Python" in jd.required_skills
    assert "Kafka" in jd.required_skills
