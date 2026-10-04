"""Batch triage over a JSONL file with resume; writes one prediction per line."""

from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path

from .config import Settings
from .llm import LLMClient
from .pipeline import Options, triage


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


async def run_batch(
    messages: list[dict],
    out: Path,
    cfg: Settings,
    opts: Options,
    model: str | None = None,
    run_meta: dict | None = None,
) -> list[dict]:
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {}
    if out.exists():
        for row in read_jsonl(out):
            if not row["trace"].get("error"):
                done[row["result"]["message_id"]] = row
    todo = [m for m in messages if m["message_id"] not in done]
    client = LLMClient(cfg, model=model)
    lock = asyncio.Lock()
    t0 = time.time()
    finished = 0
    order = [m["message_id"] for m in messages]

    def flush() -> None:
        out.write_text(
            "".join(
                json.dumps(done[i], ensure_ascii=False) + "\n"
                for i in order
                if i in done
            ),
            encoding="utf-8",
        )

    async def one(m: dict) -> None:
        nonlocal finished
        row = await triage(m, client, opts)
        row["run"] = run_meta or {}
        async with lock:
            done[m["message_id"]] = row
            finished += 1
            flush()
            if finished % 10 == 0 or finished == len(todo):
                print(
                    f"  {finished}/{len(todo)} in {time.time() - t0:.0f}s",
                    file=sys.stderr,
                )

    try:
        await asyncio.gather(*(one(m) for m in todo))
    finally:
        await client.aclose()
        flush()
    return [done[i] for i in order if i in done]
