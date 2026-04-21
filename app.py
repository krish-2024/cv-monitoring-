"""
app.py  –  HIREX AI  |  Smarter Hiring. Clearer Decisions.
───────────────────────────────────────────────────────────
Entry point for the Streamlit application.
"""

import io
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from config import APP_NAME, TAGLINE, DESCRIPTION, WEIGHTS
from utils.parser import parse_resume
from scoring.scorer import score_resume
from scoring.improver import generate_improvements
from reports.generator import generate_pdf_report

# ── Lazy chatbot import (only fails if groq is missing, not on startup) ───
def _chat_fn(messages, resume_text, jd_text, analysis):
    from chatbot.groq_chat import chat
    return chat(messages, resume_text, jd_text, analysis)


# ═══════════════════════════════════════════════════════════════════════════
#  Page config + global CSS
# ═══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="HIREX AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ─── Background ─────────────────────────────── */
.stApp { background: #0D1117; color: #E2E8F0; }

/* ─── Sidebar ────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#0F172A 0%,#1E293B 100%);
    border-right: 1px solid #1E3A5F;
}
[data-testid="stSidebar"] * { color: #CBD5E1 !important; }

/* ─── Hero ───────────────────────────────────── */
.hero-wrap {
    background: linear-gradient(135deg,#0F172A 0%,#1E293B 50%,#0F2847 100%);
    border: 1px solid #1E3A5F;
    border-radius: 20px;
    padding: 48px 40px 36px;
    text-align: center;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
}
.hero-wrap::before {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse 80% 60% at 50% -10%, rgba(37,99,235,.25) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 3.8rem;
    font-weight: 800;
    letter-spacing: -1px;
    background: linear-gradient(90deg,#60A5FA,#06B6D4,#818CF8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 8px;
}
.hero-tag {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    color: #94A3B8;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 16px;
}
.hero-desc {
    max-width: 720px;
    margin: 0 auto;
    color: #94A3B8;
    font-size: 0.97rem;
    line-height: 1.7;
}
.badge {
    display: inline-block;
    background: rgba(37,99,235,.15);
    border: 1px solid rgba(37,99,235,.4);
    color: #60A5FA;
    padding: 4px 14px;
    border-radius: 999px;
    font-size: 0.75rem;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 18px;
}

/* ─── Cards ──────────────────────────────────── */
.card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 18px;
}
.card-title {
    font-family:'Syne',sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #60A5FA;
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ─── Score circle ───────────────────────────── */
.score-circle-wrap { text-align: center; padding: 16px 0; }
.score-number {
    font-family: 'Syne', sans-serif;
    font-size: 4rem;
    font-weight: 800;
    line-height: 1;
}
.score-label { font-size: 0.8rem; color: #64748B; margin-top: 4px; text-transform: uppercase; letter-spacing: 1px; }

/* ─── Section score rows ─────────────────────── */
.sec-row { display:flex; align-items:center; gap:12px; margin-bottom:10px; }
.sec-name { width: 100px; font-size:0.85rem; color:#94A3B8; text-transform:capitalize; }
.sec-bar-bg { flex:1; background:#1E293B; border-radius:999px; height:8px; overflow:hidden; }
.sec-bar { height:100%; border-radius:999px; background:linear-gradient(90deg,#2563EB,#06B6D4); }
.sec-val { width:46px; text-align:right; font-size:0.85rem; color:#CBD5E1; font-weight:600; }

/* ─── Tag chips ──────────────────────────────── */
.chip {
    display:inline-block;
    padding:3px 10px;
    border-radius:999px;
    font-size:0.75rem;
    margin:2px;
}
.chip-green  { background:rgba(22,163,74,.2);  border:1px solid rgba(22,163,74,.4);  color:#4ADE80; }
.chip-red    { background:rgba(220,38,38,.15); border:1px solid rgba(220,38,38,.35); color:#F87171; }
.chip-amber  { background:rgba(217,119,6,.15); border:1px solid rgba(217,119,6,.35); color:#FBB850; }

/* ─── Chat ───────────────────────────────────── */
.chat-user { background:#1E3A5F; border-radius:14px 14px 4px 14px; padding:10px 14px; margin:8px 0; color:#E2E8F0; }
.chat-bot  { background:#1E293B; border-radius:14px 14px 14px 4px; padding:10px 14px; margin:8px 0; color:#CBD5E1; }
.chat-name { font-size:0.7rem; color:#64748B; margin-bottom:4px; font-weight:600; letter-spacing:.5px; }

/* ─── Streamlit overrides ────────────────────── */
div[data-testid="stFileUploader"] { background:#1E293B; border:1px dashed #334155; border-radius:12px; }
.stButton button {
    background: linear-gradient(135deg,#2563EB,#1D4ED8);
    color: white; border:none; border-radius:8px;
    font-weight:600; padding:8px 24px;
    transition: opacity .2s;
}
.stButton button:hover { opacity:.85; }
.stTextArea textarea { background:#1E293B; color:#E2E8F0; border-color:#334155; border-radius:10px; }
.stTextInput input   { background:#1E293B; color:#E2E8F0; border-color:#334155; }
div[data-testid="stExpander"] { background:#1E293B; border:1px solid #334155; border-radius:12px; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
#  Helpers
# ═══════════════════════════════════════════════════════════════════════════

def score_color(s):
    if s >= 70: return "#4ADE80"
    if s >= 45: return "#FBB850"
    return "#F87171"


def render_score_circle(score: float):
    color = score_color(score)
    st.markdown(f"""
    <div class="score-circle-wrap">
      <div class="score-number" style="color:{color}">{score}</div>
      <div class="score-label">Overall Match Score / 100</div>
    </div>""", unsafe_allow_html=True)


def render_section_bars(section_scores: dict):
    html = ""
    for sec, val in section_scores.items():
        w = WEIGHTS.get(sec, 0)
        html += f"""
        <div class="sec-row">
          <div class="sec-name">{sec.capitalize()}</div>
          <div class="sec-bar-bg"><div class="sec-bar" style="width:{val}%"></div></div>
          <div class="sec-val">{val}</div>
          <div style="width:36px;font-size:.7rem;color:#475569">{int(w*100)}%</div>
        </div>"""
    st.markdown(html, unsafe_allow_html=True)


def render_chips(items, style="chip-green"):
    if not items:
        st.markdown('<span style="color:#475569;font-size:.85rem">None detected</span>', unsafe_allow_html=True)
        return
    chips = " ".join(f'<span class="chip {style}">{i}</span>' for i in items)
    st.markdown(chips, unsafe_allow_html=True)


def radar_chart(section_scores: dict):
    cats   = list(section_scores.keys())
    vals   = list(section_scores.values())
    cats  += [cats[0]]   # close loop
    vals  += [vals[0]]
    fig = go.Figure(go.Scatterpolar(
        r=vals, theta=[c.capitalize() for c in cats],
        fill="toself",
        fillcolor="rgba(37,99,235,0.25)",
        line=dict(color="#2563EB", width=2.5),
        marker=dict(size=6, color="#06B6D4"),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#1E293B",
            radialaxis=dict(visible=True, range=[0,100], tickfont=dict(color="#64748B",size=9), gridcolor="#334155"),
            angularaxis=dict(tickfont=dict(color="#94A3B8",size=11), gridcolor="#334155"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=30,r=30,t=30,b=30),
        height=280,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_explanation(explanation: dict):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card-title">✅ Strong Areas</div>', unsafe_allow_html=True)
        render_chips(explanation.get("strong", []), "chip-green")
    with col2:
        st.markdown('<div class="card-title">⚠️ Weak Areas</div>', unsafe_allow_html=True)
        render_chips(explanation.get("weak", []), "chip-amber")

    st.markdown('<div style="margin-top:14px"><div class="card-title">🔍 Missing Keywords</div></div>', unsafe_allow_html=True)
    render_chips(explanation.get("missing_keywords", []), "chip-red")


def process_single_resume(file_obj, jd_text: str, mode="candidate"):
    """Parse → score → improve → return full result dict."""
    parsed   = parse_resume(file_obj)
    result   = score_resume(parsed["sections"], jd_text)
    improve  = generate_improvements(result)
    return {
        "parsed":      parsed,
        "score_result": result,
        "improvements": improve,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  Sidebar
# ═══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:16px 0 8px">
      <span style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;
                   background:linear-gradient(90deg,#60A5FA,#06B6D4);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent">
        ⚡ {APP_NAME}
      </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    mode = st.radio(
        "**Select Mode**",
        ["🎯  Recruiter Mode", "👤  Candidate Mode"],
        label_visibility="visible",
    )
    is_recruiter = mode.startswith("🎯")

    st.markdown("---")
    st.markdown("""
    <div style="font-size:.78rem;color:#475569;line-height:1.7">
    <b style="color:#64748B">Scoring Weights</b><br>
    Skills &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→ 40%<br>
    Experience → 30%<br>
    Projects &nbsp;&nbsp;&nbsp;→ 20%<br>
    Education → 10%
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:.75rem;color:#334155;text-align:center">
    Powered by sentence-transformers<br>& Groq LLaMA-3
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
#  Hero
# ═══════════════════════════════════════════════════════════════════════════

st.markdown(f"""
<div class="hero-wrap">
  <div class="badge">Explainable AI for Hiring &amp; Career Growth</div>
  <div class="hero-title">{APP_NAME}</div>
  <div class="hero-tag">{TAGLINE}</div>
  <div class="hero-desc">{DESCRIPTION}</div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
#  RECRUITER MODE
# ═══════════════════════════════════════════════════════════════════════════

if is_recruiter:
    st.markdown("## 🎯 Recruiter Mode — Batch Screening")

    col_upload, col_jd = st.columns([1, 1], gap="large")

    with col_upload:
        st.markdown('<div class="card-title">📄 Upload Resumes (PDF)</div>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Drop multiple PDF resumes",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )

    with col_jd:
        st.markdown('<div class="card-title">📋 Job Description</div>', unsafe_allow_html=True)
        jd_text = st.text_area(
            "Paste the JD here",
            height=170,
            placeholder="Paste the full job description...",
            label_visibility="collapsed",
        )

    if st.button("⚡  Screen All Candidates", use_container_width=True):
        if not uploaded_files:
            st.warning("Please upload at least one resume.")
        elif not jd_text.strip():
            st.warning("Please enter a job description.")
        else:
            results = []
            prog = st.progress(0, text="Analysing resumes…")
            for i, f in enumerate(uploaded_files):
                with st.spinner(f"Processing {f.name}…"):
                    data = process_single_resume(f, jd_text, mode="recruiter")
                    data["filename"] = f.name
                    results.append(data)
                prog.progress((i + 1) / len(uploaded_files), text=f"Processed {i+1}/{len(uploaded_files)}")
            prog.empty()
            st.session_state["recruiter_results"] = results

    # ── Results ────────────────────────────────────────────────────────────
    if "recruiter_results" in st.session_state:
        results = st.session_state["recruiter_results"]
        # sort by score
        results.sort(key=lambda x: x["score_result"]["final_score"], reverse=True)

        st.markdown("---")
        st.markdown("### 🏆 Candidate Rankings")

        # Summary table
        table_rows = []
        for rank, r in enumerate(results, 1):
            sc = r["score_result"]["final_score"]
            table_rows.append({
                "Rank":  rank,
                "Candidate": r["parsed"]["name"],
                "Email": r["parsed"]["email"],
                "Score": f"{sc}/100",
                "Skills": f"{r['score_result']['section_scores']['skills']}/100",
                "Experience": f"{r['score_result']['section_scores']['experience']}/100",
                "Projects": f"{r['score_result']['section_scores']['projects']}/100",
                "Status": "✅ Strong" if sc >= 70 else "⚠️ Average" if sc >= 45 else "❌ Weak",
            })

        df = pd.DataFrame(table_rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("### 🔍 Detailed Candidate Insights")

        for rank, r in enumerate(results, 1):
            sc  = r["score_result"]["final_score"]
            col = score_color(sc)
            with st.expander(
                f"#{rank}  {r['parsed']['name']}  —  "
                f"Score: {sc}/100  {'✅' if sc>=70 else '⚠️' if sc>=45 else '❌'}",
                expanded=(rank == 1),
            ):
                c1, c2 = st.columns([1, 1], gap="large")
                with c1:
                    render_score_circle(sc)
                    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
                    render_section_bars(r["score_result"]["section_scores"])
                with c2:
                    radar_chart(r["score_result"]["section_scores"])

                render_explanation(r["score_result"]["explanation"])

                # Per-candidate report download
                pdf_bytes = generate_pdf_report(
                    r["parsed"]["name"],
                    r["score_result"],
                    r["improvements"],
                    jd_snippet=jd_text[:300],
                    mode="recruiter",
                )
                st.download_button(
                    "⬇️  Download Report",
                    data=pdf_bytes,
                    file_name=f"HIREX_{r['parsed']['name'].replace(' ','_')}_report.pdf",
                    mime="application/pdf",
                    key=f"dl_{rank}",
                )

        # ── Recruiter Chatbot ──────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 🤖 HIREX AI Recruiter Assistant")
        st.markdown(
            "<div style='color:#64748B;font-size:.85rem;margin-bottom:16px'>"
            "Ask about any candidate, compare them, or get hiring recommendations.</div>",
            unsafe_allow_html=True,
        )

        # Build combined context from all candidates for the recruiter
        all_resumes_summary = "\n\n".join(
            f"=== Candidate #{i+1}: {r['parsed']['name']} ===\n"
            f"Score: {r['score_result']['final_score']}/100\n"
            f"Sections: {r['score_result']['section_scores']}\n"
            f"Strong: {r['score_result']['explanation'].get('strong', [])}\n"
            f"Weak:   {r['score_result']['explanation'].get('weak', [])}\n"
            f"Missing keywords: {r['score_result']['explanation'].get('missing_keywords', [])}"
            for i, r in enumerate(results)
        )

        rec_history = st.session_state.get("rec_chat_history", [])

        rec_chat_container = st.container()
        with rec_chat_container:
            for msg in rec_history:
                if msg["role"] == "user":
                    st.markdown(
                        f'<div class="chat-user"><div class="chat-name">YOU</div>{msg["content"]}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div class="chat-bot"><div class="chat-name">HIREX AI</div>{msg["content"]}</div>',
                        unsafe_allow_html=True,
                    )

        rec_input = st.chat_input("Ask about candidates…", key="rec_chat_input")
        if rec_input:
            rec_history.append({"role": "user", "content": rec_input})
            with st.spinner("Thinking…"):
                reply = _chat_fn(
                    rec_history,
                    all_resumes_summary,   # resume context = all candidates summary
                    jd_text,
                    results[0]["score_result"],  # top candidate as primary analysis context
                )
            rec_history.append({"role": "assistant", "content": reply})
            st.session_state["rec_chat_history"] = rec_history
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
#  CANDIDATE MODE
# ═══════════════════════════════════════════════════════════════════════════

else:
    st.markdown("## 👤 Candidate Mode — Career Insights")

    col_a, col_b = st.columns([1, 1], gap="large")

    with col_a:
        st.markdown('<div class="card-title">📄 Upload Your Resume (PDF)</div>', unsafe_allow_html=True)
        resume_file = st.file_uploader(
            "Your resume PDF",
            type=["pdf"],
            label_visibility="collapsed",
        )

    with col_b:
        st.markdown('<div class="card-title">🎯 Target Job Description</div>', unsafe_allow_html=True)
        jd_text = st.text_area(
            "Paste JD",
            height=170,
            placeholder="Paste the job description or role you're targeting…",
            label_visibility="collapsed",
        )

    if st.button("🔍  Analyse My Resume", use_container_width=True):
        if not resume_file:
            st.warning("Please upload your resume.")
        elif not jd_text.strip():
            st.warning("Please enter a job description.")
        else:
            with st.spinner("Analysing your resume with semantic AI…"):
                data = process_single_resume(resume_file, jd_text, mode="candidate")
            st.session_state["candidate_data"] = data
            st.session_state["chat_history"]   = []

    # ── Analysis output ────────────────────────────────────────────────────
    if "candidate_data" in st.session_state:
        data    = st.session_state["candidate_data"]
        result  = data["score_result"]
        improve = data["improvements"]
        parsed  = data["parsed"]
        sc      = result["final_score"]

        st.markdown("---")

        # ── Top row: score + radar ─────────────────────────────────────────
        left, mid, right = st.columns([1, 1.4, 1], gap="medium")

        with left:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            render_score_circle(sc)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">👤 Parsed Info</div>', unsafe_allow_html=True)
            st.markdown(f"**Name:** {parsed['name']}")
            st.markdown(f"**Email:** {parsed['email']}")
            st.markdown(f"**Phone:** {parsed['phone']}")
            st.markdown('</div>', unsafe_allow_html=True)

        with mid:
            radar_chart(result["section_scores"])
            render_section_bars(result["section_scores"])

        with right:
            # Improvement engine
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">💡 Top Actions</div>', unsafe_allow_html=True)
            tips = improve.get("skill_tips", [])
            for t in tips[:4]:
                st.markdown(f"<div style='font-size:.82rem;color:#94A3B8;margin-bottom:8px'>→ {t}</div>",
                            unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Explanation row ───────────────────────────────────────────────
        st.markdown('<div class="card">', unsafe_allow_html=True)
        render_explanation(result["explanation"])
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Section improvement tips ──────────────────────────────────────
        sec_tips = improve.get("section_tips", {})
        if sec_tips:
            st.markdown("### 📈 Section Improvement Recommendations")
            cols = st.columns(min(len(sec_tips), 3))
            for idx, (sec, tips) in enumerate(sec_tips.items()):
                with cols[idx % len(cols)]:
                    st.markdown(f'<div class="card">', unsafe_allow_html=True)
                    st.markdown(f'<div class="card-title">{sec.capitalize()}</div>', unsafe_allow_html=True)
                    for t in tips:
                        st.markdown(f"<div style='font-size:.82rem;color:#94A3B8;margin-bottom:6px'>• {t}</div>",
                                    unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

        # ── Report download ───────────────────────────────────────────────
        st.markdown("---")
        pdf_bytes = generate_pdf_report(
            parsed["name"], result, improve,
            jd_snippet=jd_text[:300], mode="candidate",
        )
        st.download_button(
            "⬇️  Download Full PDF Report",
            data=pdf_bytes,
            file_name=f"HIREX_{parsed['name'].replace(' ','_')}_report.pdf",
            mime="application/pdf",
        )

        # ─────────────────────────────────────────────────────────────────
        #  CHATBOT
        # ─────────────────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 🤖 HIREX AI Career Advisor")
        st.markdown(
            "<div style='color:#64748B;font-size:.85rem;margin-bottom:16px'>"
            "Ask me anything about your resume, the job, or how to improve.</div>",
            unsafe_allow_html=True
        )

        chat_container = st.container()

        history = st.session_state.get("chat_history", [])

        with chat_container:
            for msg in history:
                if msg["role"] == "user":
                    st.markdown(
                        f'<div class="chat-user"><div class="chat-name">YOU</div>{msg["content"]}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div class="chat-bot"><div class="chat-name">HIREX AI</div>{msg["content"]}</div>',
                        unsafe_allow_html=True,
                    )

        user_input = st.chat_input("Ask HIREX AI…")

        if user_input:
            history.append({"role": "user", "content": user_input})
            with st.spinner("Thinking…"):
                reply = _chat_fn(
                    history,
                    parsed["raw_text"],
                    jd_text,
                    result,
                )
            history.append({"role": "assistant", "content": reply})
            st.session_state["chat_history"] = history
            st.rerun()
