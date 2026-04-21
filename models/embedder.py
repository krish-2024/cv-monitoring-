"""
models/embedder.py
──────────────────
Singleton wrapper around sentence-transformers.
Caches the model so it loads only once per session.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
import streamlit as st

from config import EMBEDDING_MODEL


@st.cache_resource(show_spinner=False)
def _load_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL)


def embed(texts: list[str]) -> np.ndarray:
    """Return L2-normalised embeddings for a list of strings."""
    model = _load_model()
    vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return np.array(vecs)


def embed_single(text: str) -> np.ndarray:
    return embed([text])[0]
