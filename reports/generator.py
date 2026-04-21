"""
reports/generator.py
─────────────────────
Generates a formatted PDF report using ReportLab.
"""

import io
import textwrap
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from config import APP_NAME, TAGLINE


# ── Color palette ─────────────────────────────────────────────────────────
BRAND_DARK  = colors.HexColor("#0D1117")
BRAND_BLUE  = colors.HexColor("#2563EB")
BRAND_CYAN  = colors.HexColor("#06B6D4")
LIGHT_GRAY  = colors.HexColor("#F1F5F9")
MID_GRAY    = colors.HexColor("#64748B")


def _styles():
    base = getSampleStyleSheet()
    custom = {
        "title": ParagraphStyle("title", fontSize=22, textColor=BRAND_BLUE,
                                alignment=TA_CENTER, fontName="Helvetica-Bold", spaceAfter=4),
        "tagline": ParagraphStyle("tagline", fontSize=10, textColor=MID_GRAY,
                                  alignment=TA_CENTER, fontName="Helvetica-Oblique", spaceAfter=20),
        "h2": ParagraphStyle("h2", fontSize=13, textColor=BRAND_BLUE,
                              fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=4),
        "body": ParagraphStyle("body", fontSize=9.5, textColor=BRAND_DARK,
                               fontName="Helvetica", spaceAfter=4, leading=14),
        "bullet": ParagraphStyle("bullet", fontSize=9, textColor=BRAND_DARK,
                                 fontName="Helvetica", leftIndent=12, spaceAfter=2,
                                 bulletIndent=4, leading=13),
        "score_big": ParagraphStyle("score_big", fontSize=28, textColor=BRAND_BLUE,
                                    alignment=TA_CENTER, fontName="Helvetica-Bold"),
        "label": ParagraphStyle("label", fontSize=9, textColor=MID_GRAY,
                                alignment=TA_CENTER, fontName="Helvetica"),
    }
    return custom


def generate_pdf_report(
    candidate_name: str,
    score_result: dict,
    improvements: dict,
    jd_snippet: str = "",
    mode: str = "candidate",
) -> bytes:
    """Returns PDF bytes."""

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )

    S = _styles()
    story = []

    # ── Header ────────────────────────────────────────────────────────────
    story.append(Paragraph(APP_NAME, S["title"]))
    story.append(Paragraph(TAGLINE, S["tagline"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_BLUE))
    story.append(Spacer(1, 10))

    story.append(Paragraph(f"Screening Report — {candidate_name}", S["h2"]))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y  %H:%M')}",
        S["label"]
    ))
    story.append(Spacer(1, 14))

    # ── Overall Score ─────────────────────────────────────────────────────
    final = score_result["final_score"]
    color = ("#16A34A" if final >= 70 else "#D97706" if final >= 45 else "#DC2626")
    story.append(Paragraph(
        f'<font color="{color}">{final}</font>',
        S["score_big"]
    ))
    story.append(Paragraph("Overall Match Score (/100)", S["label"]))
    story.append(Spacer(1, 16))

    # ── Section Scores Table ──────────────────────────────────────────────
    story.append(Paragraph("Section-Wise Breakdown", S["h2"]))
    sec_scores = score_result["section_scores"]
    table_data = [["Section", "Score", "Weight", "Contribution"]]
    from config import WEIGHTS
    for k, v in sec_scores.items():
        w = WEIGHTS[k]
        contrib = round(v * w, 1)
        bar = "█" * int(v / 10) + "░" * (10 - int(v / 10))
        table_data.append([k.capitalize(), f"{v}/100", f"{int(w*100)}%", f"{contrib}  {bar}"])

    tbl = Table(table_data, colWidths=[3.5*cm, 2.5*cm, 2.5*cm, 8*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), BRAND_BLUE),
        ("TEXTCOLOR",    (0, 0), (-1, 0), colors.white),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_GRAY, colors.white]),
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ALIGN",        (1, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 14))

    # ── Explainability ────────────────────────────────────────────────────
    expl = score_result["explanation"]

    if expl.get("strong"):
        story.append(Paragraph("✅  Strong Areas", S["h2"]))
        for item in expl["strong"]:
            story.append(Paragraph(f"• {item}", S["bullet"]))
        story.append(Spacer(1, 6))

    if expl.get("weak"):
        story.append(Paragraph("⚠️  Areas Needing Attention", S["h2"]))
        for item in expl["weak"]:
            story.append(Paragraph(f"• {item}", S["bullet"]))
        story.append(Spacer(1, 6))

    if expl.get("missing_keywords"):
        story.append(Paragraph("🔍  Missing Keywords from JD", S["h2"]))
        story.append(Paragraph(", ".join(expl["missing_keywords"]), S["body"]))
        story.append(Spacer(1, 6))

    # ── Improvement Tips ──────────────────────────────────────────────────
    if mode == "candidate":
        story.append(Paragraph("💡  Improvement Recommendations", S["h2"]))

        sec_tips = improvements.get("section_tips", {})
        for sec, tips in sec_tips.items():
            story.append(Paragraph(f"  {sec.capitalize()}:", S["body"]))
            for t in tips:
                story.append(Paragraph(f"    – {t}", S["bullet"]))

        skill_tips = improvements.get("skill_tips", [])
        if skill_tips:
            story.append(Spacer(1, 6))
            story.append(Paragraph("  Skill Development:", S["body"]))
            for t in skill_tips:
                story.append(Paragraph(f"    – {t}", S["bullet"]))

    # ── Footer ────────────────────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY))
    story.append(Paragraph(
        f"{APP_NAME}  •  {TAGLINE}  •  Confidential Screening Report",
        S["label"]
    ))

    doc.build(story)
    return buf.getvalue()
