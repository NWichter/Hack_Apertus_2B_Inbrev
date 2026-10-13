"""Blind second annotation of test messages by an open-weights model (not a person).

The annotator sees only what a practice assistant would see (received time, channel, sender,
subject, body) and the written label guideline; it never sees the grid labels, the generator
or any Inbrev output. Apertus is never used here: it is the system under test.

    python scripts/annotate_open_models.py GOLD.jsonl [GOLD2.jsonl ...] \
        --model nvidia/nemotron-3-super-120b-a12b:free --out runs/annotation/nemotron-super.jsonl \
        --env path/to/.env [--workers 4] [--reasoning low]

Output: one line per message with the annotation, model, provider, tokens and cost. Resumes:
message ids already in --out are skipped. scripts/agreement.py compares the annotations.
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

API = "https://openrouter.ai/api/v1/chat/completions"
GUIDELINE_VERSION = "a1"
ROUTES = [
    "report_received",
    "appointment",
    "prescription_request",
    "insurer",
    "referral_in",
    "certificate_request",
    "billing",
    "spam_marketing",
    "other",
]

# Label definitions copied from the generator prompt (data/generation/PROMPT.md) and
# data/taxonomy.yaml, so annotators and generators work from the same written rules.
GUIDELINE = """You are a careful medical practice assistant (MPA) in a Swiss general practice.
You label one incoming message for an evaluation set. Label only from the text. Do not give
medical advice and do not judge severity.

Routes (exactly one, the main request):
- report_received: lab result, imaging report, discharge letter or specialist report arrives for the doctor.
- appointment: book, move or cancel an appointment.
- prescription_request: repeat prescription or medication request.
- insurer: cost approval (Kostengutsprache), insurer query, IV (disability insurance) report request,
  daily allowance (Krankentaggeld) or accident insurer form.
- referral_in: another physician or hospital refers a patient to THIS practice.
- certificate_request: sick note (Arbeitsunfähigkeitszeugnis / certificat médical / certificato medico)
  or another confirmation.
- billing: invoice, reminder, billing question (from supplier, patient, insurer).
- spam_marketing: advertising, newsletter, pharma marketing, webinars, software offers.
- other: anything else (records request, authority letter, general question ...).
If a message has a main request and a clearly subordinate second request, label the main one.

Deadline (administrative, relative to the time the message was received):
- today: action needed today or tomorrow; also always "today" for report_received and whenever
  clinical_content is true.
- this_week: action needed within 2 to 7 days.
- none: no deadline, or a deadline more than 7 days away. Advertising urgency ("only today") is "none".

clinical_content (true/false): true if the sender describes possibly acute symptoms happening now
(e.g. chest pain, breathing problems, sudden weakness or speech problems, heavy bleeding, severe
allergic reaction, suicidal thoughts, high fever in a small child), also when it is mentioned only
in passing in an otherwise administrative message. false if medical words describe no current acute
situation: a past and treated event, a stable chronic condition, a family history, an insurer asking
about last year's event, a lab report with values, "no emergency".

ambiguous (true/false): true only if a careful assistant could not decide between two routes from
the text alone (two requests with equal weight, or the purpose stays unclear).

route_quote: 2 to 15 words copied verbatim from the message that support the route.

Answer with one JSON object only:
{"route": "...", "deadline": "...", "clinical_content": true|false, "ambiguous": true|false, "route_quote": "..."}"""

SCHEMA = {
    "type": "object",
    "properties": {
        "route": {"type": "string", "enum": ROUTES},
        "deadline": {"type": "string", "enum": ["today", "this_week", "none"]},
        "clinical_content": {"type": "boolean"},
        "ambiguous": {"type": "boolean"},
        "route_quote": {"type": "string"},
    },
    "required": ["route", "deadline", "clinical_content", "ambiguous", "route_quote"],
    "additionalProperties": False,
}

WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def load_key(env_path: Path) -> str:
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("OPENROUTER_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("OPENROUTER_API_KEY not found")


def message_text(row: dict) -> str:
    rec = row.get("received_at") or ""
    try:
        wd = WEEKDAYS[datetime.fromisoformat(rec).weekday()]
    except ValueError:
        wd = "unknown weekday"
    return (
        f"Received: {rec} ({wd})\nChannel: {row.get('channel')}\nFrom: {row.get('sender')}\n"
        f"Subject: {row.get('subject')}\n\n{row.get('body')}"
    )


def parse(content: str) -> dict | None:
    content = content.strip()
    if content.startswith("```"):
        content = content.strip("`")
        content = content[content.find("{") :]
    start, end = content.find("{"), content.rfind("}")
    if start < 0 or end < 0:
        return None
    try:
        obj = json.loads(content[start : end + 1])
    except json.JSONDecodeError:
        return None
    if obj.get("route") not in ROUTES or obj.get("deadline") not in (
        "today",
        "this_week",
        "none",
    ):
        return None
    if not isinstance(obj.get("clinical_content"), bool) or not isinstance(
        obj.get("ambiguous"), bool
    ):
        return None
    return obj


def call(key: str, body: dict) -> dict:
    req = urllib.request.Request(
        API,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "X-Title": "Inbrev second annotation",
        },
    )
    last = ""
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                resp = json.loads(r.read().decode("utf-8"))
            if resp.get("error") and not resp.get("choices"):
                last = str(resp["error"])[:200]
            else:
                return resp
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            last = f"{exc}"
        time.sleep(min(120, 15 * (attempt + 1)))
    raise RuntimeError(f"API failed repeatedly: {last}")


def annotate(key: str, args: argparse.Namespace, row: dict) -> dict:
    body = {
        "model": args.model,
        "messages": [
            {"role": "system", "content": GUIDELINE},
            {"role": "user", "content": message_text(row)},
        ],
        "temperature": 0,
        "max_tokens": args.max_tokens,
        "usage": {"include": True},
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "annotation", "schema": SCHEMA, "strict": True},
        },
    }
    if args.reasoning:
        body["reasoning"] = {"effort": args.reasoning}
    out = {
        "message_id": row["message_id"],
        "annotator_model": args.model,
        "guideline": GUIDELINE_VERSION,
        "annotation": None,
        "cost": 0.0,
        "attempts": 0,
    }
    for attempt in range(3):
        out["attempts"] = attempt + 1
        try:
            resp = call(key, body)
        except RuntimeError as exc:
            out["error"] = str(exc)
            return out
        usage = resp.get("usage") or {}
        out["cost"] += usage.get("cost") or 0.0
        out["prompt_tokens"] = usage.get("prompt_tokens")
        out["completion_tokens"] = usage.get("completion_tokens")
        out["provider"] = resp.get("provider")
        out["model"] = resp.get("model")
        choice = (resp.get("choices") or [{}])[0]
        content = (choice.get("message") or {}).get("content") or ""
        ann = parse(content)
        if ann is not None:
            out["annotation"] = ann
            out.pop("error", None)
            return out
        out["error"] = f"unparsable ({choice.get('finish_reason')}): {content[:200]}"
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+", type=Path)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--env", required=True, type=Path)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--max-tokens", type=int, default=4000)
    ap.add_argument("--reasoning", choices=["low", "medium", "high"])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--budget-usd", type=float, default=0.25)
    args = ap.parse_args()

    key = load_key(args.env)
    rows = []
    for p in args.inputs:
        rows += [
            json.loads(x)
            for x in p.read_text(encoding="utf-8").splitlines()
            if x.strip()
        ]
    done = set()
    spent = 0.0
    if args.out.exists():
        for line in args.out.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                spent += r.get("cost") or 0.0
                if r.get("annotation"):
                    done.add(r["message_id"])
    todo = [r for r in rows if r["message_id"] not in done][: args.limit]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    lock = threading.Lock()
    print(f"{len(todo)} to annotate, {len(done)} done, {spent:.4f} USD spent so far")

    def work(row: dict) -> None:
        nonlocal spent
        if spent >= args.budget_usd:
            return
        res = annotate(key, args, row)
        with lock:
            spent += res.get("cost") or 0.0
            with args.out.open("a", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(res, ensure_ascii=False) + "\n")
            a = res.get("annotation") or {}
            print(
                f"{res['message_id']}: {a.get('route')} {a.get('deadline')} clin={a.get('clinical_content')} cost={spent:.4f} {res.get('error', '')[:80]}"
            )

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(work, todo))
    print(f"total spent {spent:.4f} USD")


if __name__ == "__main__":
    sys.exit(main())
