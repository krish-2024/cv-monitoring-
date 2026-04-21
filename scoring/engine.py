"""
scoring/engine.py
Section-wise cosine similarity scoring with explainable output.
"""

from __future__ import annotations
import numpy as np
from typing import Dict, Any
from sklearn.metrics.pairwise import cosine_similarity

from config import SECTION_WEIGHTS
from models.embedder import get_embedder


# ─────────────────────────────────────────────────────────────────────────────
# Core scoring
# ─────────────────────────────────────────────────────────────────────────────

def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two 1-D vectors, clamped to [0, 1]."""
    sim = cosine_similarity(a.reshape(1, -1), b.reshape(1, -1))[0][0]
    return float(np.clip(sim, 0.0, 1.0))


def score_resume(
    resume_sections: Dict[str, str],
    jd_text: str,
) -> Dict[str, Any]:
    """
    Compute section-wise cosine scores and weighted final score.

    Returns a dict:
        {
            "section_scores": {"skills": 0.82, ...},
            "final_score":    0.74,
            "jd_embedding":   np.ndarray,   # for downstream use
            "section_embeddings": {...},
        }
    """
    embedder = get_embedder()
    jd_emb = embedder.encode(jd_text)

    section_scores: Dict[str, float] = {}
    section_embeddings: Dict[str, np.ndarray] = {}

    for section, text in resume_sections.items():
        emb = embedder.encode(text if text.strip() else " ")
        section_embeddings[section] = emb
        section_scores[section] = _cosine(emb, jd_emb)

    final = sum(
        section_scores.get(s, 0.0) * w
        for s, w in SECTION_WEIGHTS.items()
    )

    return {
        "section_scores":     section_scores,
        "final_score":        round(final, 4),
        "jd_embedding":       jd_emb,
        "section_embeddings": section_embeddings,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Explainability
# ─────────────────────────────────────────────────────────────────────────────

# Simple keyword lists for gap detection (no external API needed)
_COMMON_TECH_SKILLS = [
    "python", "java", "javascript", "typescript", "sql", "react", "node",
    "docker", "kubernetes", "aws", "azure", "gcp", "machine learning",
    "deep learning", "nlp", "data analysis", "pandas", "tensorflow", "pytorch",
    "fastapi", "django", "flask", "git", "ci/cd", "agile", "scrum",
    "communication", "leadership", "problem solving",
]


def explain_scores(
    section_scores: Dict[str, float],
    resume_sections: Dict[str, str],
    jd_text: str,
) -> Dict[str, Any]:
    """
    Generate human-readable explanation for the scoring result.
    Returns strengths, gaps, improvement suggestions.
    """
    jd_lower = jd_text.lower()

    # Identify skills mentioned in JD but absent from resume
    resume_text = " ".join(resume_sections.values()).lower()
    missing_skills = [
        skill for skill in _COMMON_TECH_SKILLS
        if skill in jd_lower and skill not in resume_text
    ]

    strong_sections = [
        s for s, v in section_scores.items() if v >= 0.65
    ]
    weak_sections = [
        s for s, v in section_scores.items() if v < 0.45
    ]

    suggestions = []
    if "skills" in weak_sections:
        suggestions.append("Add more technical keywords that match the job description.")
    if "experience" in weak_sections:
        suggestions.append("Quantify your work experience with metrics (e.g., 'reduced latency by 30%').")
    if "projects" in weak_sections:
        suggestions.append("Highlight projects that are relevant to the target role.")
    if "education" in weak_sections:
        suggestions.append("Include relevant coursework, certifications, or academic achievements.")
    if missing_skills:
        suggestions.append(
            f"Consider acquiring or showcasing these skills: {', '.join(missing_skills[:6])}."
        )

    score_breakdown_text = " | ".join(
        f"{s.capitalize()}: {v*100:.1f}%" for s, v in section_scores.items()
    )

    reasoning = (
        f"Your resume was evaluated across four dimensions — Skills (40%), "
        f"Experience (30%), Projects (20%), and Education (10%). "
        f"Section breakdown: {score_breakdown_text}. "
    )
    if strong_sections:
        reasoning += f"Your strongest areas are: {', '.join(strong_sections)}. "
    if weak_sections:
        reasoning += f"Areas needing improvement: {', '.join(weak_sections)}."

    return {
        "strong_sections":  strong_sections,
        "weak_sections":    weak_sections,
        "missing_skills":   missing_skills[:8],
        "suggestions":      suggestions,
        "reasoning":        reasoning,
    }
