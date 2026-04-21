# ─────────────────────────────────────────────
#  HIREX AI  –  Central Configuration
# ─────────────────────────────────────────────

import os

# ── Brand ──────────────────────────────────────
APP_NAME        = "HIREX AI"
TAGLINE         = "Smarter Hiring. Clearer Decisions."
DESCRIPTION     = (
    "An AI-powered platform that evaluates resumes using semantic intelligence, "
    "ranks candidates with transparent scoring, and provides actionable insights "
    "for both recruiters and job seekers."
)

# ── Model ──────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ── Scoring Weights ────────────────────────────
WEIGHTS = {
    "skills":     0.40,
    "experience": 0.30,
    "projects":   0.20,
    "education":  0.10,
}

# ── Groq (backend only – never exposed in UI) ──
GROQ_API_KEY   = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL     = "llama-3.3-70b-versatile"  

# ── Report ─────────────────────────────────────
REPORT_DIR = "reports"
