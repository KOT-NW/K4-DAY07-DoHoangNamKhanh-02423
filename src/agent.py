from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        if not results:
            return "Không tìm thấy thông tin liên quan trong cơ sở tri thức."
        lines = []
        for i, r in enumerate(results, start=1):
            source = r.get("metadata", {}).get("doc_id") or r.get("metadata", {}).get("source") or "unknown"
            lines.append(f"[{i}] (nguon: {source}) {r['content']}")
        context = "\n".join(lines)
        prompt = (
            f"Cau hoi: {question}\n"
            f"Ngu canh truy xuat:\n{context}\n"
            "Yeu cau: chi tra loi dua tren ngu canh tren, trich dan so [1]/[2]/[3] "
            "khi su dung thong tin. Neu ngu canh khong chua dap an, hay noi ro khong tim thay."
        )
        return self.llm_fn(prompt)
