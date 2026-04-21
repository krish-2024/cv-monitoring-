"""
scoring/improver.py
───────────────────
Generates improvement suggestions based on score results
without any external API call.
"""

from config import WEIGHTS


_SKILL_SUGGESTIONS = {
    "python":      "Deepen Python with projects in FastAPI, async programming, or data pipelines.",
    "aws":         "Earn AWS Cloud Practitioner or Solutions Architect certification.",
    "docker":      "Containerise a personal project and publish it on Docker Hub.",
    "kubernetes":  "Deploy a multi-service app on a local Kubernetes cluster (minikube).",
    "react":       "Build a full-stack app with React + a REST/GraphQL backend.",
    "sql":         "Practice advanced SQL on LeetCode or Mode Analytics.",
    "tensorflow":  "Complete TensorFlow Developer Certificate course.",
    "pytorch":     "Implement a paper from scratch and share on GitHub.",
    "git":         "Contribute to open-source repos; build a visible GitHub profile.",
    "ci/cd":       "Set up GitHub Actions or GitLab CI for an existing project.",
}

_SECTION_ADVICE = {
    "skills": [
        "Add a 'Technical Skills' section with explicit technology categories.",
        "Quantify skill proficiency levels (e.g., Proficient, Intermediate, Familiar).",
    ],
    "experience": [
        "Use STAR format (Situation, Task, Action, Result) for each bullet.",
        "Add metrics: 'Reduced latency by 30%', 'Served 1M+ users'.",
        "Align job titles and responsibilities with the target role's language.",
    ],
    "projects": [
        "Include GitHub links and live demos for every project.",
        "Describe the problem, your solution, and measurable impact.",
        "Add a project specifically relevant to the target role.",
    ],
    "education": [
        "List relevant coursework, GPA (if ≥ 3.5), and academic awards.",
        "Include online certifications from Coursera, edX, or LinkedIn Learning.",
    ],
}


def generate_improvements(score_result: dict) -> dict:
    """
    Returns { "section_tips": {section: [str]}, "skill_tips": [str] }
    """
    section_tips: dict[str, list[str]] = {}
    skill_tips: list[str] = []

    gaps = score_result["explanation"].get("gap_sections", [])
    missing_kw = score_result["explanation"].get("missing_keywords", [])

    for gap in gaps:
        section_tips[gap] = _SECTION_ADVICE.get(gap, [])

    # Even non-gap sections get tips if score < 80
    for sec, score in score_result["section_scores"].items():
        if score < 80 and sec not in section_tips:
            section_tips[sec] = _SECTION_ADVICE.get(sec, [])

    for kw in missing_kw:
        tip = _SKILL_SUGGESTIONS.get(kw)
        if tip:
            skill_tips.append(tip)

    if not skill_tips:
        skill_tips.append("Review the job description carefully and mirror its technology stack in your resume.")

    return {"section_tips": section_tips, "skill_tips": skill_tips}
