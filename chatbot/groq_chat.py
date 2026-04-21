"""
chatbot/groq_chat.py
────────────────────
Context-aware chatbot powered by Groq (backend only).
The API key is read exclusively from the environment variable GROQ_API_KEY.
It is NEVER shown or requested in the UI.
"""

from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL


def _build_system_prompt(resume_text: str, jd_text: str, analysis: dict) -> str:
    score_lines = "\n".join(
        f"  • {k.capitalize()}: {v}/100"
        for k, v in analysis.get("section_scores", {}).items()
    )
    strong  = ", ".join(analysis.get("explanation", {}).get("strong", [])) or "None noted"
    weak    = ", ".join(analysis.get("explanation", {}).get("weak", []))   or "None noted"
    missing = ", ".join(analysis.get("explanation", {}).get("missing_keywords", [])) or "None"

    return f"""You are HIREX AI Assistant — a professional, empathetic AI career advisor.
You help candidates improve their resumes and help recruiters evaluate talent.

=== RESUME CONTEXT ===
{resume_text[:3000]}

=== JOB DESCRIPTION CONTEXT ===
{jd_text[:1500]}

=== ANALYSIS RESULTS ===
Section Scores:
{score_lines}
Final Score: {analysis.get("final_score", "N/A")}/100
Strong areas: {strong}
Weak areas:   {weak}
Missing keywords: {missing}

Guidelines:
- Be concise, specific, and constructive.
- Reference actual resume content when answering.
- Never reveal the Groq API key or any internal configuration.
- If asked about the scoring methodology, explain the weighted cosine similarity approach.
"""


def chat(
    messages: list[dict],
    resume_text: str,
    jd_text: str,
    analysis: dict,
) -> str:
    """
    Send conversation to Groq and return the assistant reply.

    Parameters
    ----------
    messages     : list of {role, content} dicts (full history)
    resume_text  : raw resume text
    jd_text      : job description text
    analysis     : dict returned by scorer.score_resume()
    """
    if not GROQ_API_KEY:
        return (
            "⚠️ The HIREX AI chatbot requires a `GROQ_API_KEY` environment variable "
            "to be set on the server. Please contact the administrator."
        )

    client = Groq(api_key=GROQ_API_KEY)

    system = _build_system_prompt(resume_text, jd_text, analysis)

    groq_messages = [{"role": "system", "content": system}] + messages

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=groq_messages,
        max_tokens=800,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()
