"""Turn raw generator output into gold-set records, or merge record files.

Assemble: python scripts/assemble.py --grid grid.jsonl --generator codex \
    --model gpt-5.5 --out codex.jsonl raw1.jsonl raw2.jsonl ...
Merge:    python scripts/assemble.py --merge --out merged.v0.jsonl claude.jsonl codex.jsonl
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

PROMPT_VERSION = "v0.1"
META_KEYS = [
    "formality",
    "writing_level",
    "mixed_topic",
    "secondary_route",
    "abstain_alternative_route",
    "safety_case",
    "spam_fake_urgency",
]
LABEL_KEYS = [
    "route",
    "deadline",
    "deadline_date",
    "assignee",
    "safety_flag",
    "abstain",
    "patient",
    "fields",
    "evidence",
]
REVIEW_KEYS = ["edited_by", "edit_note", "review_flag", "review_reason"]


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{n}: invalid JSON: {exc}")
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def assemble(
    raw: dict, spec: dict, generator: str, model: str, generated_at: str
) -> dict:
    label = raw.get("label", {})
    record = {
        "message_id": raw["message_id"],
        "language": raw.get("language"),
        "channel": raw.get("channel"),
        "sender_type": raw.get("sender_type", spec.get("sender_type")),
        "sender": raw.get("sender"),
        "received_at": raw.get("received_at"),
        "subject": raw.get("subject"),
        "body": raw.get("body"),
        "source": "synthetic",
        "generator": generator,
        "generator_model": raw.get("generator_model", model),
        "generated_at": raw.get("generated_at", generated_at),
        "prompt_version": raw.get("prompt_version", PROMPT_VERSION),
        "meta": {k: spec.get(k) for k in META_KEYS},
        "label": {k: label.get(k) for k in LABEL_KEYS},
    }
    record["label"]["patient"] = record["label"]["patient"] or {}
    record["label"]["fields"] = record["label"]["fields"] or {}
    record["label"]["evidence"] = record["label"]["evidence"] or []
    for k in REVIEW_KEYS:
        if raw.get(k) is not None:
            record[k] = raw[k]
    return record


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+", type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--merge", action="store_true")
    ap.add_argument("--grid", type=Path)
    ap.add_argument("--generator", choices=["claude", "codex"])
    ap.add_argument("--model")
    ap.add_argument("--generated-at", default=date.today().isoformat())
    args = ap.parse_args()

    if args.merge:
        rows = [r for p in args.inputs for r in read_jsonl(p)]
        rows.sort(key=lambda r: r["message_id"])
        write_jsonl(args.out, rows)
        print(f"merged {len(rows)} rows into {args.out}")
        return

    if not (args.grid and args.generator and args.model):
        raise SystemExit("--grid, --generator and --model are required unless --merge")
    grid = {s["message_id"]: s for s in read_jsonl(args.grid)}
    out = []
    for p in args.inputs:
        for raw in read_jsonl(p):
            spec = grid.get(raw.get("message_id"))
            if spec is None:
                raise SystemExit(f"{p}: unknown message_id {raw.get('message_id')}")
            out.append(
                assemble(raw, spec, args.generator, args.model, args.generated_at)
            )
    out.sort(key=lambda r: r["message_id"])
    write_jsonl(args.out, out)
    print(f"assembled {len(out)} rows into {args.out}")


if __name__ == "__main__":
    main()
