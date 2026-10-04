"""Third, open-weights generator set for the synthetic gold set (via OpenRouter).

Grid:     python scripts/generate_openrouter.py grid --seed 2027 --out grid-nemotron.jsonl
Generate: python scripts/generate_openrouter.py generate --grid grid-nemotron.jsonl \
              --model nvidia/nemotron-3-ultra-550b-a55b --raw-dir rohfassungen/nemotron \
              --out nemotron.jsonl --env path/to/.env

The grid reuses make_grid.build() with the counts scaled to 45 specs (see GRID_45).
The prompt is the generator prompt from data/generation/PROMPT.md with the concrete
example values removed (PROMPT_EDITS). Each returned line is checked with
validate.check_row; failing specs are re-requested at most MAX_RETRIES times with the
validator messages, then dropped. Apertus is never used here.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

sys.path.insert(0, str(Path(__file__).resolve().parent))
import assemble  # noqa: E402
import make_grid  # noqa: E402
import validate  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PROMPT_MD = ROOT / "data" / "generation" / "PROMPT.md"
API = "https://openrouter.ai/api/v1/chat/completions"
PROMPT_VERSION = "v0.2-nemotron"
GENERATOR = "nemotron"
MAX_RETRIES = 2

GRID_45 = {
    "ROUTE_COUNTS": {
        "report_received": 6,
        "appointment": 7,
        "prescription_request": 6,
        "insurer": 6,
        "referral_in": 4,
        "certificate_request": 5,
        "billing": 4,
        "spam_marketing": 3,
        "other": 4,
    },
    "SAFETY_SLOTS": {
        "acute_explicit": {"other": 2, "appointment": 2},
        "acute_incidental": {
            "appointment": 1,
            "prescription_request": 2,
            "certificate_request": 1,
            "billing": 1,
        },
        "medical_trap": {
            "report_received": 2,
            "appointment": 1,
            "prescription_request": 1,
            "insurer": 1,
            "certificate_request": 1,
            "other": 1,
        },
    },
    "LANG_COUNTS": {"de": 25, "fr": 11, "it": 7, "en": 2},
    "MIXED_N": 5,
    "ABSTAIN_N": 2,
}

# Development set for prompt work (seed 4049, prefix "dev"): "other" oversampled.
# Never used for reported test numbers; test sets stay gold v0, Swiss, Nemotron, GraSCCo.
GRID_DEV = {
    "ROUTE_COUNTS": {
        "report_received": 6,
        "appointment": 6,
        "prescription_request": 5,
        "insurer": 6,
        "referral_in": 4,
        "certificate_request": 6,
        "billing": 4,
        "spam_marketing": 3,
        "other": 20,
    },
    "SAFETY_SLOTS": {
        "acute_explicit": {"other": 3, "appointment": 2},
        "acute_incidental": {
            "appointment": 1,
            "prescription_request": 1,
            "certificate_request": 1,
            "other": 1,
        },
        "medical_trap": {
            "report_received": 1,
            "insurer": 1,
            "certificate_request": 1,
            "other": 2,
        },
    },
    "LANG_COUNTS": {"de": 33, "fr": 15, "it": 9, "en": 3},
    "MIXED_N": 6,
    "ABSTAIN_N": 3,
}
PRESETS = {"45": GRID_45, "dev": GRID_DEV}

PROMPT_EDITS = [
    (
        '("PS: since this morning my chest\n  feels tight, probably nothing")',
        "(for example in a closing remark)",
    ),
    (
        'amounts "CHF 1\'240.50" or "CHF 418.60"',
        "amounts as CHF with an apostrophe as thousands separator and two\n  decimals (choose your own values)",
    ),
    (
        'Use invented names such as "Labor Aaretal AG", "Spital Unterseetal",\n'
        '  "Krankenkasse Alpina (fiktiv)", "Caisse-maladie Lémanis".',
        "Invent your own names for them.",
    ),
    (
        '(e.g. "a.muster@mail.example",\n  "befunde@labor-aaretal.hin.example")',
        '(secured professional mail: ".hin.example")',
    ),
    (
        '"000": "079 000 12 34", "044 000 56 78", "+41 91 000 22 11".',
        '"000": a Swiss area or mobile prefix, then the group 000, then two\n'
        "  pairs of digits of your choice (also valid in the +41 form).",
    ),
]

WRAPPER = """
=== Delivery ===
Return exactly one JSON object and nothing else: {"messages": [ ... ]} with one
message object per spec, in spec order. Every message object has all keys from
"Output format" above, including "sender".
The last label of every e-mail domain is exactly "example" (".ch", ".com" or
"example.ch" are wrong). Evidence quotes are copied character by character.
"""


def build_prompt() -> str:
    md = PROMPT_MD.read_text(encoding="utf-8")
    m = re.search(r"## Generator prompt\s+```text\n(.*?)```", md, re.S)
    if not m:
        raise SystemExit("generator prompt block not found in PROMPT.md")
    text = m.group(1)
    for old, new in PROMPT_EDITS:
        if old not in text:
            raise SystemExit(f"prompt edit does not apply: {old[:50]!r}")
        text = text.replace(old, new)
    return text.rstrip() + "\n" + WRAPPER


def cmd_grid(args: argparse.Namespace) -> None:
    for k, v in PRESETS[args.preset].items():
        setattr(make_grid, k, v)
    specs = make_grid.build(args.seed)
    for s in specs:
        s["message_id"] = s["message_id"].replace("syn-", f"{args.prefix}-")
        s["generator"] = GENERATOR
    specs.sort(key=lambda s: s["message_id"])
    assemble.write_jsonl(Path(args.out), specs)
    print(f"wrote {len(specs)} specs to {args.out}")


def load_key(env_path: Path) -> str:
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("OPENROUTER_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("OPENROUTER_API_KEY not found")


def call(key: str, model: str, messages: list[dict], max_tokens: int) -> dict:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.8,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
        "usage": {"include": True},
    }
    req = urllib.request.Request(
        API,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "X-Title": "Inbrev gold-set generation",
        },
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                return json.loads(r.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            body = exc.read().decode("utf-8", "replace") if hasattr(exc, "read") else ""
            print(f"  http error ({attempt}): {exc} {body[:300]}")
            time.sleep(10 * (attempt + 1))
    raise SystemExit("API failed repeatedly")


def parse_messages(content: str) -> list[dict]:
    content = content.strip()
    content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content)
    try:
        obj = json.loads(content)
        if isinstance(obj, dict):
            obj = obj.get("messages", [obj])
        return [o for o in obj if isinstance(o, dict)]
    except json.JSONDecodeError:
        out = []
        for line in content.splitlines():
            line = line.strip().rstrip(",")
            if line.startswith("{"):
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return out


def normalize(raw: dict) -> list[str]:
    notes = []
    label = raw.get("label") or {}
    for group in ("fields", "patient"):
        for k, v in list((label.get(group) or {}).items()):
            if isinstance(v, list):
                label[group][k] = ", ".join(map(str, v))
                notes.append(f"{group}.{k}: list joined to string")
            elif isinstance(v, (int, float)) and not isinstance(v, bool):
                label[group][k] = str(v)
                notes.append(f"{group}.{k}: number to string")
    return notes


def check(record: dict, spec: dict, validator, strict: bool = False) -> list[str]:
    rep = validate.Report()
    validate.check_row(record, spec, validator, rep)
    found = rep.errors + (rep.warnings if strict else [])
    return [f"{c}: {m}" for _, c, m in found]


def cmd_generate(args: argparse.Namespace) -> None:
    key = load_key(Path(args.env))
    grid = [
        json.loads(l)
        for l in Path(args.grid).read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]
    if args.only:
        grid = [s for s in grid if s["message_id"] in set(args.only.split(","))]
    by_id = {s["message_id"]: s for s in grid}
    schema = json.loads(validate.SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    raw_dir = Path(args.raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    system = build_prompt()
    (raw_dir / f"PROMPT-{PROMPT_VERSION}.txt").write_text(system, encoding="utf-8")
    today = date.today().isoformat()

    accepted: dict[str, dict] = {}
    log = []
    batches = [
        grid[i : i + args.batch_size] for i in range(0, len(grid), args.batch_size)
    ]
    for bi, batch in enumerate(batches, start=1):
        pending = [s["message_id"] for s in batch]
        feedback: dict[str, list[str]] = {}
        for attempt in range(MAX_RETRIES + 1):
            if not pending:
                break
            specs = [by_id[m] for m in pending]
            user = "SPECS (JSONL):\n" + "\n".join(
                json.dumps(s, ensure_ascii=False) for s in specs
            )
            if feedback:
                user += "\n\nYour previous output for these specs failed the automatic checks. "
                user += (
                    "Write each message again from scratch as a complete object "
                    "with all keys and fix these problems:\n"
                )
                user += "\n".join(
                    f"- {m}: {'; '.join(e)}"
                    for m, e in feedback.items()
                    if m in pending
                )
            tag = f"b{bi:02d}.try{attempt}"
            (raw_dir / f"{tag}.prompt.txt").write_text(user, encoding="utf-8")
            t0 = time.time()
            resp = call(
                key,
                args.model,
                [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                args.max_tokens,
            )
            dt = time.time() - t0
            (raw_dir / f"{tag}.response.json").write_text(
                json.dumps(resp, ensure_ascii=False, indent=1), encoding="utf-8"
            )
            choice = (resp.get("choices") or [{}])[0]
            content = (choice.get("message") or {}).get("content") or ""
            usage = resp.get("usage") or {}
            msgs = parse_messages(content)
            entry = {
                "batch": bi,
                "attempt": attempt,
                "specs": pending[:],
                "model": resp.get("model"),
                "provider": resp.get("provider"),
                "finish_reason": choice.get("finish_reason"),
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "reasoning_tokens": (usage.get("completion_tokens_details") or {}).get(
                    "reasoning_tokens"
                ),
                "cost": usage.get("cost"),
                "seconds": round(dt, 1),
                "returned": len(msgs),
                "failed": {},
            }
            got = {}
            for raw in msgs:
                mid = raw.get("message_id")
                if mid in pending and mid not in got:
                    got[mid] = raw
            feedback = {}
            for mid in pending:
                raw = got.get(mid)
                if raw is None:
                    feedback[mid] = ["message missing or not valid JSON in the output"]
                    continue
                notes = normalize(raw)
                if notes:
                    raw["edited_by"] = "generate_openrouter.py"
                    raw["edit_note"] = "; ".join(notes)
                raw["generator_model"] = args.model
                raw["generated_at"] = today
                raw["prompt_version"] = PROMPT_VERSION
                rec = assemble.assemble(raw, by_id[mid], GENERATOR, args.model, today)
                errs = check(rec, by_id[mid], validator, args.strict)
                if errs:
                    feedback[mid] = errs
                else:
                    accepted[mid] = rec
            entry["failed"] = feedback
            log.append(entry)
            pending = [m for m in pending if m not in accepted]
            print(
                f"{tag}: {len(msgs)} returned, {len(specs) - len(pending)} ok, {len(pending)} failing, cost {entry['cost']}, {dt:.0f}s"
            )
        for mid in pending:
            log.append({"batch": bi, "dropped": mid, "errors": feedback.get(mid)})

    rows = [accepted[m] for m in sorted(accepted)]
    assemble.write_jsonl(Path(args.out), rows)
    (raw_dir / "run-log.json").write_text(
        json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    cost = sum(e.get("cost") or 0 for e in log)
    print(f"accepted {len(rows)}/{len(grid)}, total cost {cost:.4f} USD -> {args.out}")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("grid")
    g.add_argument("--seed", type=int, default=2027)
    g.add_argument("--prefix", default="nem")
    g.add_argument("--preset", choices=sorted(PRESETS), default="45")
    g.add_argument("--out", required=True)
    r = sub.add_parser("generate")
    r.add_argument("--grid", required=True)
    r.add_argument("--model", required=True)
    r.add_argument("--raw-dir", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--env", required=True)
    r.add_argument("--batch-size", type=int, default=5)
    r.add_argument("--max-tokens", type=int, default=40000)
    r.add_argument("--only", help="comma-separated message_ids to (re)generate")
    r.add_argument("--strict", action="store_true", help="treat validator warnings as errors")
    args = ap.parse_args()
    {"grid": cmd_grid, "generate": cmd_generate}[args.cmd](args)


if __name__ == "__main__":
    main()
