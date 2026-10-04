"""OpenAI-compatible chat client (Apertus via vLLM, llama.cpp or the hackathon endpoint)."""

from __future__ import annotations

import asyncio
import random
import re
import time
from dataclasses import dataclass, field

import httpx

from .config import Settings


@dataclass
class Completion:
    contents: list[str]
    finish_reasons: list[str]
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_s: float = 0.0
    retries: int = 0
    raw_model: str = ""
    errors: list[str] = field(default_factory=list)
    split: bool = False


class LLMError(RuntimeError):
    pass


def redact(text: str) -> str:
    """429 bodies name a hash of the API key; never store it."""
    return re.sub(r"(api_key:?\s*)\S+", lambda m: m.group(1) + "<redacted>", text)


class LLMClient:
    def __init__(self, cfg: Settings, model: str | None = None):
        self.cfg = cfg
        self.model = model or cfg.llm_name
        self._client = httpx.AsyncClient(
            base_url=cfg.llm_base_url,
            headers={"Authorization": f"Bearer {cfg.llm_api_key}"},
            timeout=cfg.timeout,
        )
        self._sem = asyncio.Semaphore(cfg.concurrency)
        self.split_samples = {"on": True, "off": False}.get(cfg.split_samples)

    async def chat(self, messages: list[dict], *, n: int = 1, **kw) -> Completion:
        """n samples in one request; servers without `n` (llama.cpp) get n single requests."""
        if n > 1 and self.split_samples is not True:
            try:
                comp = await self._chat(messages, n=n, **kw)
            except LLMError as e:
                if self.split_samples is False or "HTTP 400" not in str(e):
                    raise
                self.split_samples = True
            else:
                if len(comp.contents) >= n or self.split_samples is False:
                    return comp
                self.split_samples = True
        if n == 1 or not self.split_samples:
            return await self._chat(messages, n=n, **kw)
        parts = []
        for i in range(n):
            extra = dict(kw.pop("extra", None) or {})
            extra.setdefault("seed", 1000 + i)
            parts.append(await self._chat(messages, n=1, extra=extra, **kw))
            kw["extra"] = {k: v for k, v in extra.items() if k != "seed"} or None
        return Completion(
            contents=[c for p in parts for c in p.contents],
            finish_reasons=[f for p in parts for f in p.finish_reasons],
            prompt_tokens=sum(p.prompt_tokens for p in parts),
            completion_tokens=sum(p.completion_tokens for p in parts),
            latency_s=sum(p.latency_s for p in parts),
            retries=sum(p.retries for p in parts),
            raw_model=parts[0].raw_model,
            split=True,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _chat(
        self,
        messages: list[dict],
        *,
        schema: dict | None = None,
        n: int = 1,
        temperature: float = 0.0,
        max_tokens: int | None = None,
        max_retries: int = 6,
        extra: dict | None = None,
    ) -> Completion:
        body: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens or self.cfg.max_tokens,
            "n": n,
        }
        if extra:
            body.update(extra)
        if schema is not None:
            body["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "inbrev_triage",
                    "schema": schema,
                    "strict": True,
                },
            }
        retries = 0
        async with self._sem:
            while True:
                t0 = time.perf_counter()
                try:
                    r = await self._client.post("/chat/completions", json=body)
                except (httpx.TimeoutException, httpx.TransportError) as e:
                    err = f"{type(e).__name__}"
                    status = None
                else:
                    status = r.status_code
                    err = redact(r.text[:300])
                    if status == 200:
                        j = r.json()
                        usage = j.get("usage") or {}
                        return Completion(
                            contents=[
                                c["message"].get("content") or "" for c in j["choices"]
                            ],
                            finish_reasons=[
                                c.get("finish_reason") or "" for c in j["choices"]
                            ],
                            prompt_tokens=usage.get("prompt_tokens", 0),
                            completion_tokens=usage.get("completion_tokens", 0),
                            latency_s=time.perf_counter() - t0,
                            retries=retries,
                            raw_model=j.get("model", self.model),
                        )
                    if status not in (408, 409, 429, 500, 502, 503, 504):
                        raise LLMError(f"HTTP {status}: {err}")
                retries += 1
                if retries > max_retries:
                    raise LLMError(
                        f"giving up after {retries - 1} retries: {status} {err}"
                    )
                await asyncio.sleep(
                    min(30.0, 1.5 * 2 ** (retries - 1)) + random.random()
                )
