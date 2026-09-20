"""UI chat RAG mini cho Lab 7 (Streamlit). Chay: pip install streamlit; streamlit run app.py"""
from __future__ import annotations

import re
from pathlib import Path

import streamlit as st

from src.agent import KnowledgeBaseAgent
from src.chunking import FixedSizeChunker, RecursiveChunker, SentenceChunker
from src.models import Document
from src.store import EmbeddingStore
from src.zen import ZenLLM

DATA_DIR = Path("data/university")


def parse_md(path: Path) -> tuple[dict, str]:
    parts = path.read_text(encoding="utf-8").split("---")
    front, body = (parts[1], "---".join(parts[2:]).strip()) if len(parts) >= 3 else ("", path.read_text(encoding="utf-8"))
    meta: dict = {}
    for line in front.splitlines():
        m = re.match(r"^(\w+):\s*(.+)$", line.strip())
        if m:
            meta[m.group(1)] = m.group(2).strip().strip('"')
    body = "\n".join(l for l in body.splitlines() if not l.strip().startswith(">")).strip()
    return meta, body


def chunk_heading(text: str, max_len: int = 600) -> list[str]:
    if not text or not text.strip():
        return []
    sections, cur = [], []
    for line in text.strip().splitlines():
        if re.match(r"^#{1,4}\s+", line.strip()) and cur:
            sections.append("\n".join(cur).strip())
            cur = [line]
        else:
            cur.append(line)
    if cur:
        sections.append("\n".join(cur).strip())
    out: list[str] = []
    fb = RecursiveChunker(chunk_size=max_len)
    for sec in [s for s in sections if s]:
        if len(sec) <= max_len:
            out.append(sec)
            continue
        m = re.match(r"^(#{1,4}\s+[^\n]+)\n?(.*)$", sec, re.S)
        title, body_text = (m.group(1), m.group(2)) if m else ("", sec)
        out += [f"{title}\n{p}".strip() if title else p for p in fb.chunk(body_text)]
    return out


CHUNKERS = {
    "heading": lambda t: chunk_heading(t),
    "fixed": lambda t: FixedSizeChunker(chunk_size=500, overlap=50).chunk(t),
    "sentence": lambda t: SentenceChunker(max_sentences_per_chunk=2).chunk(t),
    "recursive": lambda t: RecursiveChunker(chunk_size=500).chunk(t),
}


def resolve_llm():
    """Dung Zen LLM that neu co ZEN_API_KEY, nguoc lai fallback mock (mien phi)."""
    try:
        return ZenLLM()
    except RuntimeError:
        return lambda p: "(LLM mock — chua co ZEN_API_KEY trong .env) " + p[:300] + "..."


@st.cache_resource
def load_store(strategy: str) -> EmbeddingStore:
    store = EmbeddingStore(collection_name="ui")
    for path in sorted(DATA_DIR.glob("*.md")):
        front, body = parse_md(path)
        for i, ch in enumerate(CHUNKERS[strategy](body)):
            store.add_documents([Document(id=f"{path.stem}#{i}", content=ch, metadata={**front, "doc_id": path.stem})])
    return store


st.title("Lab 7 — RAG Chat (mock embedder)")
strategy = st.sidebar.selectbox("Chien luoc chunking", list(CHUNKERS), index=0)
audience = st.sidebar.selectbox("Loc audience", ["(khong loc)", "student", "faculty", "all"])
top_k = st.sidebar.slider("top_k", 1, 5, 3)
store = load_store(strategy)
st.caption(f"Da nap {store.get_collection_size()} chunks tu {len(list(DATA_DIR.glob('*.md')))} files.")

q = st.text_input("Cau hoi:", "Toi la sinh vien, muon sach duoc may cuon, bao lau?")
if st.button("Hoi") and q.strip():
    filt = None if audience == "(khong loc)" else {"audience": audience}
    results = store.search_with_filter(q, top_k=top_k, metadata_filter=filt)
    st.subheader(f"Top-{len(results)} truy xuat")
    for i, r in enumerate(results, 1):
        st.markdown(f"**[{i}] score={r['score']:.3f} doc=`{r['metadata'].get('doc_id')}`**")
        st.write(r["content"][:600])
    agent = KnowledgeBaseAgent(store=store, llm_fn=resolve_llm())
    st.subheader("Agent tra loi")
    st.caption(f"LLM backend: {getattr(agent.llm_fn, '_backend_name', 'mock')}")
    st.write(agent.answer(q, top_k=top_k))
