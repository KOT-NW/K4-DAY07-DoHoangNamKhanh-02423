"""Benchmark rieng: nap corpus data/university, chunk theo heading, chay 5 query.

Chien luoc: HeadingChunker (tach theo tieu de Markdown, giu tieu de o
moi manh con; section dai thi roi xuong RecursiveChunker).
Doi chien luoc khac chi can sua 1 dong STRATEGRY o duoi.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from src.agent import KnowledgeBaseAgent
from src.chunking import (
    ChunkingStrategyComparator,
    FixedSizeChunker,
    RecursiveChunker,
    SentenceChunker,
)
from src.models import Document
from src.store import EmbeddingStore

DATA_DIR = Path("data/university")

# DOI CHIEN LUOC O DAY: "heading" | "fixed" | "sentence" | "recursive"
STRATEGY = "heading"


class HeadingChunker:
    """Chunk theo tieu de/muc cua van ban quy dinh.

    Ly do: tai lieu quy dinh/so tay duoc bien soan theo muc (## ...),
    moi muc la mot don vi ngu nghia tron ven do nguoi soan chia san.
    """

    def __init__(self, max_len: int = 600) -> None:
        self.max_len = max_len
        self._fallback = RecursiveChunker(chunk_size=max_len)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        lines = text.strip().splitlines()
        sections: list[str] = []
        current: list[str] = []
        for line in lines:
            if re.match(r"^#{1,4}\s+", line.strip()) and current:
                sections.append("\n".join(current).strip())
                current = [line]
            else:
                current.append(line)
        if current:
            sections.append("\n".join(current).strip())
        sections = [s for s in sections if s]
        if not sections:
            return []
        chunks: list[str] = []
        for sec in sections:
            if len(sec) <= self.max_len:
                chunks.append(sec)
                continue
            m = re.match(r"^(#{1,4}\s+[^\n]+)\n?(.*)$", sec, re.S)
            title, body = (m.group(1), m.group(2)) if m else ("", sec)
            for piece in self._fallback.chunk(body):
                chunks.append(f"{title}\n{piece}".strip() if title else piece)
        return chunks


def get_chunker(name: str):
    if name == "fixed":
        return FixedSizeChunker(chunk_size=500, overlap=50)
    if name == "sentence":
        return SentenceChunker(max_sentences_per_chunk=2)
    if name == "recursive":
        return RecursiveChunker(chunk_size=500)
    return HeadingChunker(max_len=600)


def parse_md(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---")
    front = parts[1] if len(parts) >= 3 else ""
    body = "---".join(parts[2:]).strip() if len(parts) >= 3 else text.strip()
    meta: dict = {}
    for line in front.splitlines():
        m = re.match(r"^(\w+):\s*(.+)$", line.strip())
        if m:
            meta[m.group(1)] = m.group(2).strip().strip('"')
    # Bo dong template quote ">" o dau body (neu con sot)
    body = "\n".join(l for l in body.splitlines() if not l.strip().startswith(">")).strip()
    return meta, body


QUERIES = [
    {
        "q": "Toi la sinh vien, muon sach thu vien duoc may cuon, bao lau, gia han the nao?",
        "gold": "Sinh vien dai hoc: toi da 3 cuon, moi cuon 2 tuan, gia han 1 lan them 1 tuan.",
        "keywords": ["3 cuon", "2 tuan", "gia han"],
        "filter": {"audience": "student"},
        "doc": "library-borrow-student",
    },
    {
        "q": "Giang vien VinUni muon sach duoc may cuon va bao lau?",
        "gold": "Giang vien VinUni: toi da 5 cuon, toi da 6 thang.",
        "keywords": ["5 cuon", "6 thang"],
        "filter": None,
        "doc": "library-borrow-faculty",
    },
    {
        "q": "Hoc phi nam 2026-2027 cua Dieu duong va cac nganh cu nhan khac, co tro cap gi?",
        "gold": "Dieu duong 349.650.000/nam; cac cu nhan khac 815.850.000/nam; tro cap 35% Vingroup.",
        "keywords": ["349.650.000", "815.850.000", "35%"],
        "filter": None,
        "doc": "tuition-fees-2026",
    },
    {
        "q": "Duy tri hoc bong Full/100% can GPA bao nhieu, hoc bong 50-90% can bao nhieu?",
        "gold": "Full/100%: GPA nam tu 3.2; 50-90%: GPA nam tu 2.5; kem E.X.C.E.L va ky luat tot.",
        "keywords": ["3.2", "2.5", "E.X.C.E.L"],
        "filter": None,
        "doc": "scholarship-maintain",
    },
    {
        "q": "KTX NEU phong 4 nguoi co dieu hoa gia bao nhieu, gio gioi nghiem va dang ky the nao?",
        "gold": "Phong 4 nguoi dieu hoa 1.500.000/nguoi/thang; gioi nghiem 23h (T7-CN 23h30); 2 anh 3x4 + coc 5 thang tai nha 5.",
        "keywords": ["1.500.000", "23h", "coc 5 thang"],
        "filter": None,
        "doc": "neu-ktx-1001",
    },
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategy", default=STRATEGY,
                    choices=["heading", "fixed", "sentence", "recursive"])
    args = ap.parse_args()
    chunker = get_chunker(args.strategy)
    print(f"Chien luoc chunking: {args.strategy} ({type(chunker).__name__})")

    store = EmbeddingStore(collection_name="bench", embedding_fn=None)
    files = sorted(DATA_DIR.glob("*.md"))
    n_chunks = 0
    for path in files:
        front, body = parse_md(path)
        if not body:
            continue
        for i, ch in enumerate(chunker.chunk(body)):
            store.add_documents([Document(
                id=f"{path.stem}#{i}", content=ch,
                metadata={**front, "doc_id": path.stem},
            )])
            n_chunks += 1
    print(f"Da nap {len(files)} files, {n_chunks} chunks (mock embedder, khong co ngu nghia).")

    # Baseline tren 2 tai lieu
    comp = ChunkingStrategyComparator()
    for name in ["library-policy-access.md", "neu-ktx-1001.md"]:
        p = DATA_DIR / name
        if p.exists():
            _, body = parse_md(p)
            r = comp.compare(body, chunk_size=500)
            print(f"\nBaseline {name}:")
            for k, v in r.items():
                print(f"  {k}: count={v['count']}, avg_length={v['avg_length']:.1f}")

    agent = KnowledgeBaseAgent(store=store, llm_fn=lambda prompt: "[agent-mock] " + prompt[:200])
    for idx, item in enumerate(QUERIES, start=1):
        print(f"\n=== Q{idx}: {item['q']}")
        print(f"Gold: {item['gold']} (doc: {item['doc']})")
        # A/B cho cau can filter: chay kem va khong kem filter
        runs = [("co filter", item["filter"])]
        if idx == 1:
            runs.append(("khong filter (A/B)", None))
        for label, f in runs:
            res = store.search_with_filter(item["q"], top_k=3, metadata_filter=f)
            print(f"-- {label} filter={f}:")
            for r in res:
                doc_id = r["metadata"].get("doc_id")
                preview = r["content"][:110].replace("\n", " ")
                print(f"   score={r['score']:.3f} doc={doc_id} | {preview}...")
            hits = [k for k in item["keywords"]
                    if any(k in r["content"] for r in res)]
            print(f"   keyword hit: {len(hits)}/{len(item['keywords'])} {hits}")
    print(f"\nAgent demo Q1: {agent.answer(QUERIES[0]['q'])[:220]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
