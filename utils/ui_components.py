"""
utils/ui_components.py
Reusable Streamlit UI building blocks for HIREX AI.
"""

from __future__ import annotations
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from typing import Dict, Any, List


# ─────────────────────────────────────────────────────────────────────────────
# Score gauge
# ─────────────────────────────────────────────────────────────────────────────

def render_score_gauge(score: float, title: str = "Match Score") -> None:
    pct = round(score * 100, 1)
    color = "#22c55e" if pct >= 65 else "#eab308" if pct >= 45 else "#ef4444"
    label = "Excellent" if pct >= 65 else "Good" if pct >= 45 else "Needs Work"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=pct,
        number={"suffix": "%", "font": {"size": 36, "color": color}},
        title={"text": f"<b>{title}</b><br><span style='font-size:13px;color:#94a3b8'>{label}</span>",
               "font": {"size": 16}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#334155"},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "#1e293b",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 45],  "color": "#1e293b"},
                {"range": [45, 65], "color": "#1e293b"},
                {"range": [65, 100],"color": "#1e293b"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "thickness": 0.8,
                "value": pct,
            },
        },
    ))
    fig.update_layout(
        height=240,
        margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e2e8f0"},
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# Section radar chart
# ─────────────────────────────────────────────────────────────────────────────

def render_radar_chart(section_scores: Dict[str, float]) -> None:
    sections = list(section_scores.keys())
    values   = [round(v * 100, 1) for v in section_scores.values()]

    fig = go.Figure(go.Scatterpolar(
        r=values + [values[0]],
        theta=[s.capitalize() for s in sections] + [sections[0].capitalize()],
        fill="toself",
        fillcolor="rgba(99,102,241,0.25)",
        line=dict(color="#6366f1", width=2),
        marker=dict(size=6, color="#a5b4fc"),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#0f172a",
            radialaxis=dict(visible=True, range=[0, 100], color="#475569", gridcolor="#1e293b"),
            angularaxis=dict(color="#94a3b8", gridcolor="#1e293b"),
        ),
        showlegend=False,
        height=320,
        margin=dict(l=40, r=40, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# Section bar breakdown
# ─────────────────────────────────────────────────────────────────────────────

def render_section_bars(section_scores: Dict[str, float]) -> None:
    weights = {"skills": 40, "experience": 30, "projects": 20, "education": 10}
    sections = list(section_scores.keys())
    values   = [round(v * 100, 1) for v in section_scores.values()]
    colors   = [
        "#22c55e" if v >= 65 else "#eab308" if v >= 45 else "#ef4444"
        for v in values
    ]
    labels = [f"{s.capitalize()} ({weights.get(s,0)}%)" for s in sections]

    fig = go.Figure(go.Bar(
        y=labels,
        x=values,
        orientation="h",
        marker_color=colors,
        text=[f"{v}%" for v in values],
        textposition="outside",
        textfont=dict(color="#e2e8f0", size=12),
    ))
    fig.update_layout(
        xaxis=dict(range=[0, 110], showgrid=False, color="#94a3b8"),
        yaxis=dict(color="#e2e8f0"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=220,
        margin=dict(l=10, r=30, t=10, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# Recruiter leaderboard table
# ─────────────────────────────────────────────────────────────────────────────

def render_leaderboard(candidates: List[Dict[str, Any]]) -> None:
    """Render a styled ranked table of candidates."""
    rows = []
    for i, c in enumerate(candidates, 1):
        score = c.get("final_score", 0)
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
        bar_pct = round(score * 100, 1)
        rows.append({
            "Rank":  medal,
            "Name":  c.get("name", "Unknown"),
            "Score": f"{bar_pct}%",
            "Skills":     f"{c['section_scores'].get('skills',0)*100:.0f}%",
            "Experience": f"{c['section_scores'].get('experience',0)*100:.0f}%",
            "Projects":   f"{c['section_scores'].get('projects',0)*100:.0f}%",
            "Education":  f"{c['section_scores'].get('education',0)*100:.0f}%",
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
# Insight pills
# ─────────────────────────────────────────────────────────────────────────────

def render_insight_pills(items: List[str], color: str = "#6366f1", label: str = "") -> None:
    if label:
        st.markdown(f"**{label}**")
    if not items:
        st.markdown("_None detected_")
        return
    pills_html = " ".join(
        f'<span style="background:{color}22;color:{color};border:1px solid {color}55;'
        f'padding:3px 10px;border-radius:99px;font-size:13px;margin:3px;display:inline-block">'
        f'{item}</span>'
        for item in items
    )
    st.markdown(pills_html, unsafe_allow_html=True)
