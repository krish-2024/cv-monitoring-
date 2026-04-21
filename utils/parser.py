"""
utils/parser.py
───────────────
PDF text extraction + section segmentation.
Uses pdfplumber (pure-Python, no native deps).
"""

import re
import pdfplumber


# ── Low-level extraction ───────────────────────────────────────────────────

def extract_text_from_pdf(file_obj) -> str:
    """Return all text from a PDF file-like object."""
    text_parts = []
    with pdfplumber.open(file_obj) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
    return "\n".join(text_parts)


# ── Section headings we recognise ─────────────────────────────────────────

_SECTION_PATTERNS = {
    "name":       re.compile(r"(?i)^(name)\s*[:\-]?\s*(.+)"),
    "email":      re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    "phone":      re.compile(r"(\+?\d[\d\s\-().]{7,}\d)"),
    "skills":     re.compile(r"(?i)(skills?|technical skills?|core competencies|technologies)"),
    "experience": re.compile(r"(?i)(experience|work history|employment|professional background)"),
    "projects":   re.compile(r"(?i)(projects?|personal projects?|key projects?)"),
    "education":  re.compile(r"(?i)(education|academic|qualifications?|degrees?)"),
    "summary":    re.compile(r"(?i)(summary|objective|profile|about me)"),
}


def _split_into_sections(text: str) -> dict[str, str]:
    """
    Heuristic section splitter.
    Returns a dict section_name → raw text block.
    """
    lines = text.splitlines()
    sections: dict[str, list[str]] = {k: [] for k in ["skills", "experience", "projects", "education", "summary"]}
    current = "summary"

    for line in lines:
        stripped = line.strip()
        matched = False
        for sec in ["skills", "experience", "projects", "education", "summary"]:
            if _SECTION_PATTERNS[sec].search(stripped) and len(stripped) < 60:
                current = sec
                matched = True
                break
        if not matched:
            sections[current].append(stripped)

    return {k: " ".join(v).strip() for k, v in sections.items()}


def extract_candidate_name(text: str) -> str:
    """Best-effort candidate name from first non-empty lines."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for line in lines[:5]:
        # skip lines that look like headers or contact info
        if "@" in line or re.search(r"\d{5,}", line):
            continue
        if len(line.split()) <= 5 and line[0].isupper():
            return line
    return "Unknown"


# ── Public API ────────────────────────────────────────────────────────────

def parse_resume(file_obj) -> dict:
    """
    Returns:
        {
          "raw_text": str,
          "name": str,
          "email": str,
          "phone": str,
          "sections": { skills, experience, projects, education, summary }
        }
    """
    raw = extract_text_from_pdf(file_obj)

    email_match = _SECTION_PATTERNS["email"].search(raw)
    phone_match = _SECTION_PATTERNS["phone"].search(raw)

    sections = _split_into_sections(raw)

    return {
        "raw_text": raw,
        "name":     extract_candidate_name(raw),
        "email":    email_match.group(0) if email_match else "N/A",
        "phone":    phone_match.group(1) if phone_match else "N/A",
        "sections": sections,
    }
