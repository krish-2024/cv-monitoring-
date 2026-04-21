# ⚡ HIREX AI — Smarter Hiring. Clearer Decisions.

> Explainable AI for Hiring & Career Growth

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone <your-repo>
cd hirex_ai
pip install -r requirements.txt
```

### 2. Set Groq API Key (backend only — never in UI)

```bash
export GROQ_API_KEY="your_groq_api_key_here"
```

Or on **Streamlit Cloud**: add it in **Settings → Secrets**:
```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

### 3. Run

```bash
streamlit run app.py
```

---

## 🏗️ Project Structure

```
hirex_ai/
├── app.py                  # Main Streamlit application
├── config.py               # Brand + model + scoring config
├── requirements.txt
├── .streamlit/
│   └── config.toml         # Dark theme
├── utils/
│   └── parser.py           # PDF extraction + section segmentation
├── models/
│   └── embedder.py         # sentence-transformers wrapper (cached)
├── scoring/
│   ├── scorer.py           # Cosine similarity + XAI explainability
│   └── improver.py         # Improvement suggestion engine
├── chatbot/
│   └── groq_chat.py        # Groq LLaMA-3 backend chatbot
└── reports/
    └── generator.py        # ReportLab PDF report generation
```

---

## 🎯 Features

| Feature | Details |
|---|---|
| **Recruiter Mode** | Upload N resumes, batch score, ranked table, per-candidate PDF |
| **Candidate Mode** | Upload resume + JD, full XAI breakdown, improvement tips |
| **Semantic Scoring** | all-MiniLM-L6-v2 embeddings + cosine similarity |
| **Explainability** | Strong/weak areas, missing keywords, gap detection |
| **Improvement Engine** | Section-wise tips + targeted skill recommendations |
| **PDF Reports** | Branded, formatted, downloadable with full analysis |
| **AI Chatbot** | Groq LLaMA-3 with resume + JD + analysis context |

---

## 🔐 Security

- The `GROQ_API_KEY` is **read from environment variables only**
- It is **never shown, requested, or stored** in the UI
- All AI processing happens server-side

---

## ☁️ Streamlit Cloud Deployment

1. Push to GitHub
2. Connect repo on [share.streamlit.io](https://share.streamlit.io)
3. Set `GROQ_API_KEY` in Secrets
4. Deploy — done!

---

*HIREX AI — Built with sentence-transformers, Groq LLaMA-3, ReportLab & Streamlit*
