"""
scoring/scorer.py
─────────────────
Computes section-wise cosine similarity and final weighted score.
Also produces human-readable explainability notes.
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from config import WEIGHTS
from models.embedder import embed


# ── Core scoring ──────────────────────────────────────────────────────────

def _safe_cos(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity clamped to [0, 1]."""
    if a.ndim == 1:
        a = a.reshape(1, -1)
    if b.ndim == 1:
        b = b.reshape(1, -1)
    sim = cosine_similarity(a, b)[0][0]
    return float(np.clip(sim, 0.0, 1.0))


def score_resume(sections: dict[str, str], jd_text: str) -> dict:
    """
    Parameters
    ----------
    sections : dict  –  { skills, experience, projects, education, summary }
    jd_text  : str   –  full job description

    Returns
    -------
    {
      "section_scores": { skills: float, experience: float, ... },
      "final_score":    float   (0-100),
      "explanation":    { strong: [...], weak: [...], gaps: [...] }
    }
    """
    jd_vec = embed([jd_text])[0]

    keys = ["skills", "experience", "projects", "education"]
    texts = [sections.get(k, "") or "N/A" for k in keys]
    vecs  = embed(texts)

    raw_scores = {k: _safe_cos(vecs[i], jd_vec) for i, k in enumerate(keys)}

    final = sum(WEIGHTS[k] * raw_scores[k] for k in keys) * 100

    explanation = _explain(raw_scores, sections, jd_text)

    return {
        "section_scores": {k: round(v * 100, 1) for k, v in raw_scores.items()},
        "final_score":    round(final, 1),
        "explanation":    explanation,
    }


# ── Explainability ────────────────────────────────────────────────────────

_THRESH_STRONG = 0.55
_THRESH_WEAK   = 0.35

def _explain(raw: dict, sections: dict, jd_text: str) -> dict:
    strong, weak, gaps = [], [], []

    labels = {
        "skills":     "Skills alignment",
        "experience": "Work experience relevance",
        "projects":   "Project portfolio match",
        "education":  "Education relevance",
    }

    for k, v in raw.items():
        if v >= _THRESH_STRONG:
            strong.append(f"{labels[k]} is strong ({v*100:.0f}/100)")
        elif v < _THRESH_WEAK:
            weak.append(f"{labels[k]} is low ({v*100:.0f}/100)")
            gaps.append(k)

    # naive keyword gap detection
    jd_words = set(jd_text.lower().split())
    resume_words = set(" ".join(sections.values()).lower().split())
    tech_keywords = {
        "python","java","javascript","typescript","react","node","sql","aws",
        "docker","kubernetes","mlflow","pytorch","tensorflow","fastapi","django",
        "git","linux","ci/cd","agile","scrum","rest","graphql","spark","kafka",
    }
    missing = sorted(tech_keywords & jd_words - resume_words)[:8]

    return {
        "strong":          strong,
        "weak":            weak,
        "gap_sections":    gaps,
        "missing_keywords": missing,
    }
