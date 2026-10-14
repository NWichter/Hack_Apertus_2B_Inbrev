"""Web app: sorted inbox, detail view with highlighted evidence, JSON API under /v1/."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import __version__, ingest, prompt
from .config import REPO_DATA, settings
from .llm import LLMClient
from .pipeline import Options, triage
from .runner import read_jsonl

STATIC = Path(__file__).parent / "static"
DEADLINE_ORDER = {"today": 0, "this_week": 1, "none": 2}

app = FastAPI(title="Inbrev", version=__version__)
app.mount("/static", StaticFiles(directory=STATIC), name="static")

cfg = settings()
opts = Options.from_env(cfg)
inbox: dict[str, dict] = {}
_tasks: set[asyncio.Task] = set()
_client: LLMClient | None = None


class MessageIn(BaseModel):
    message_id: str | None = None
    channel: str = "email"
    sender: str = ""
    subject: str = ""
    body: str
    received_at: str | None = None
    language: str | None = None
    mode: Literal["admin", "clinical-triage"] | None = None


NO_ENDPOINT = (
    "No model endpoint is configured. Set LLM_BASE_URL, LLM_API_KEY and LLM_NAME "
    "(for example in track_2b/.env, then run `make run` again), or start the offline stack "
    "with `make run-local`."
)


def endpoint_configured() -> bool:
    return bool(cfg.llm_base_url.strip())


def _stored_results() -> dict[str, dict]:
    pre = os.getenv("INBREV_PRECOMPUTED")
    if not pre or not Path(pre).exists():
        return {}
    return {r["result"]["message_id"]: r for r in read_jsonl(Path(pre))}


def client() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient(cfg)
    return _client


def _sort_key(item: dict):
    r = item.get("result")
    if not r:
        return (5, 0, item["message"].get("received_at") or "")
    if r["safety_flag"] or r["abstain"]:
        group = 0
    else:
        group = 1 + DEADLINE_ORDER.get(r["deadline"], 2)
    return (group, 0, item["message"].get("received_at") or "")


def _audit(message: dict, row: dict) -> None:
    path = cfg.audit_log
    path.parent.mkdir(parents=True, exist_ok=True)
    r, t = row["result"], row["trace"]
    entry = {
        "at": datetime.now().isoformat(timespec="seconds"),
        "message_id": r["message_id"],
        "text_sha256": hashlib.sha256(
            (message.get("subject", "") + "\n" + message.get("body", "")).encode()
        ).hexdigest(),
        "model": t.get("model"),
        "prompt_version": t.get("prompt_version"),
        "route": r["route"],
        "deadline": r["deadline"],
        "safety_flag": r["safety_flag"],
        "abstain": r["abstain"],
        "abstain_reasons": t.get("abstain_reasons"),
        "route_votes": t.get("route_votes"),
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


async def _triage_item(item: dict) -> None:
    item["status"] = "running"
    row = await triage(item["message"], client(), opts)
    item["result"], item["trace"] = row["result"], _trace_view(row["trace"])
    item["status"] = "error" if row["trace"].get("error") else "done"
    _audit(item["message"], row)


def _trace_view(trace: dict) -> dict:
    keep = (
        "model",
        "prompt_version",
        "route_votes",
        "llm_safety_votes",
        "lexical_safety_hits",
        "ambiguous_votes",
        "abstain_reasons",
        "valid_samples",
        "samples",
        "sample_errors",
        "prompt_tokens",
        "completion_tokens",
        "latency_s",
        "error",
        "dropped",
    )
    return {k: trace.get(k) for k in keep}


def _demo_sets() -> dict[str, Path]:
    sets = {"seed": REPO_DATA / "seed" / "messages.seed.jsonl"}
    demo = REPO_DATA / "demo" / "inbox.jsonl"
    if demo.exists():
        sets["demo"] = demo
    gold = cfg.data_dir / "gold-set" / "merged.v0.jsonl"
    if gold.exists():
        sets["gold"] = gold
    return sets


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/v1/health")
def health() -> dict:
    host = urlparse(cfg.llm_base_url).hostname or ""
    return {
        "version": __version__,
        "model": cfg.llm_name,
        "mode": opts.mode,
        "prompt_version": prompt.PROMPT_VERSION,
        "mailbox": bool(os.getenv("INBREV_IMAP_HOST")),
        "endpoint_configured": endpoint_configured(),
        "endpoint_host": host,
        "endpoint_local": endpoint_configured()
        and (
            host in ("localhost", "127.0.0.1", "llm")
            or host.endswith(".local")
            or "." not in host
        ),
        "samples": opts.samples,
        "safety_mode": opts.safety_mode,
        "symptom_check": opts.symptom_check,
        "rules_gate": opts.rules_gate,
        "second_opinion_model": opts.second_opinion_model or None,
        "demo_sets": list(_demo_sets()),
        "precomputed": os.getenv("INBREV_PRECOMPUTED", ""),
    }


@app.get("/v1/inbox")
def get_inbox() -> dict:
    items = sorted(inbox.values(), key=_sort_key)
    counts = {
        "total": len(items),
        "pending": sum(i["status"] == "pending" for i in items),
        "running": sum(i["status"] == "running" for i in items),
    }
    return {"items": items, "counts": counts}


@app.post("/v1/inbox/load/{name}")
def load_demo(name: str, limit: int = 30, with_predictions: bool = False) -> dict:
    sets = _demo_sets()
    if name not in sets:
        raise HTTPException(404, f"unknown demo set {name}")
    inbox.clear()
    msgs = read_jsonl(sets[name])[:limit]
    for m in msgs:
        m = {k: v for k, v in m.items() if k not in ("label", "meta")}
        inbox[m["message_id"]] = {
            "message": m,
            "result": None,
            "trace": None,
            "status": "pending",
        }
    pre = os.getenv("INBREV_PRECOMPUTED")
    if with_predictions and pre and Path(pre).exists():
        for row in read_jsonl(Path(pre)):
            item = inbox.get(row["result"]["message_id"])
            if item:
                item.update(
                    result=row["result"],
                    trace=_trace_view(row["trace"]),
                    status="done",
                    stored=True,
                )
    return {"loaded": len(msgs)}


@app.post("/v1/inbox/fetch")
def fetch_mail() -> dict:
    from .mailbox import ImapConfig, fetch

    imap = ImapConfig.from_env()
    if imap is None:
        raise HTTPException(404, "no mailbox configured (INBREV_IMAP_HOST)")
    try:
        msgs = fetch(imap)
    except Exception as e:  # noqa: BLE001 - shown to the user as a failed fetch
        raise HTTPException(502, f"mailbox: {type(e).__name__}") from e
    new = 0
    for m in msgs:
        if m["message_id"] not in inbox:
            inbox[m["message_id"]] = {
                "message": m,
                "result": None,
                "trace": None,
                "status": "pending",
            }
            new += 1
    return {"fetched": len(msgs), "new": new}


@app.post("/v1/inbox/sort")
async def sort_inbox() -> dict:
    pending = [i for i in inbox.values() if i["status"] in ("pending", "error")]
    if not endpoint_configured():
        stored = _stored_results()
        used = 0
        for i in pending:
            row = stored.get(i["message"]["message_id"])
            if row:
                i.update(
                    result=row["result"],
                    trace=_trace_view(row["trace"]),
                    status="done",
                    stored=True,
                )
                used += 1
        return {
            "queued": 0,
            "stored": used,
            "not_sorted": len(pending) - used,
            "endpoint_configured": False,
            "message": NO_ENDPOINT
            + (
                f" Showing {used} stored results instead (marked as stored)."
                if used
                else ""
            ),
        }
    for i in pending:
        i["status"] = "queued"

    async def run() -> None:
        await asyncio.gather(*(_triage_item(i) for i in pending))

    task = asyncio.create_task(run())
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)
    return {"queued": len(pending)}


@app.post("/v1/inbox/clear")
def clear_inbox() -> dict:
    inbox.clear()
    return {"ok": True}


@app.post("/v1/triage")
async def triage_one(msg: MessageIn) -> dict:
    if not endpoint_configured():
        raise HTTPException(503, NO_ENDPOINT)
    m = msg.model_dump()
    m["message_id"] = m["message_id"] or ingest._new_id("api")
    req_opts = replace(opts, mode=m["mode"]) if m.get("mode") else opts
    row = await triage(m, client(), req_opts)
    _audit(m, row)
    return row["result"]


@app.post("/v1/upload")
async def upload(file: UploadFile = File(...)) -> dict:
    data = await file.read()
    try:
        m = ingest.from_upload(data, file.filename or "upload.txt")
    except Exception as e:  # noqa: BLE001 - shown to the user as a failed import
        raise HTTPException(422, f"could not read {file.filename}: {e}") from e
    item = {"message": m, "result": None, "trace": None, "status": "queued"}
    inbox[m["message_id"]] = item
    if not endpoint_configured():
        item["status"] = "pending"
        return {**item, "message": NO_ENDPOINT}
    await _triage_item(item)
    return item
