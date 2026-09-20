"""Client cho Zen gateway (OpenAI Responses API tuong thich).

Key KHONG nam trong code: doc tu bien moi truong ZEN_API_KEY
(hoac OPENAI_API_KEY). Nguoi dung tu tao file .env local tu
.env.example — .env da nam trong .gitignore nen khong bao gio push.
"""
from __future__ import annotations

import json
import os
import urllib.request

ZEN_URL_ENV = "ZEN_RESPONSES_URL"
ZEN_KEY_ENV = "ZEN_API_KEY"
ZEN_MODEL_ENV = "ZEN_MODEL"
DEFAULT_URL = "https://opencode.ai/zen/go/v1/responses"
DEFAULT_MODEL = "muse-spark-1.3-contributor"


class ZenLLM:
    """LLM backend goi Zen Responses API bang stdlib (khong them dependency)."""

    def __init__(self, model: str | None = None, url: str | None = None,
                 api_key: str | None = None, timeout: float = 60.0) -> None:
        self.model = model or os.getenv(ZEN_MODEL_ENV, DEFAULT_MODEL)
        self.url = url or os.getenv(ZEN_URL_ENV, DEFAULT_URL)
        self.api_key = api_key or os.getenv(ZEN_KEY_ENV) or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("Thieu ZEN_API_KEY (them vao file .env local, khong commit).")
        self.timeout = timeout
        self._backend_name = f"zen:{self.model}"

    def __call__(self, prompt: str) -> str:
        payload = json.dumps({"model": self.model, "input": prompt}).encode("utf-8")
        req = urllib.request.Request(
            self.url, data=payload, method="POST",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"},
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            raise RuntimeError(f"Goi Zen API that bai: {exc}") from exc
        return extract_text(data)

    def __repr__(self) -> str:  # pragma: no cover
        return f"ZenLLM(model={self.model!r})"


def extract_text(data: dict) -> str:
    """Rut text tu Responses API payload (output array hoac output_text)."""
    if isinstance(data.get("output_text"), str) and data["output_text"].strip():
        return data["output_text"].strip()
    chunks: list[str] = []
    for item in data.get("output", []) or []:
        if not isinstance(item, dict):
            continue
        for part in item.get("content", []) or []:
            if isinstance(part, dict) and part.get("type") in ("output_text", "text"):
                text = part.get("text", "")
                if isinstance(text, dict):
                    text = text.get("value", "")
                if text:
                    chunks.append(str(text))
    if chunks:
        return "\n".join(chunks).strip()
    return json.dumps(data, ensure_ascii=False)[:1000]
