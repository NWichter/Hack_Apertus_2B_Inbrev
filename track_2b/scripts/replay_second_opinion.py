"""Reproduce the second-opinion numbers through the built-in code path, without model calls.

The stored 70B run supplies the raw samples the second model would have returned; `pipeline.replay`
then applies `needs_second_opinion` and `apply_second_opinion` exactly as `triage` does live.

python scripts/replay_second_opinion.py GOLD.jsonl FIRST.jsonl SECOND.jsonl --out out.jsonl
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from gap_metrics import HEADER, fmt, read_jsonl, score
from inbrev.pipeline import Options, replay


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("gold", type=Path)
    ap.add_argument("first", type=Path)
    ap.add_argument("second", type=Path)
    ap.add_argument("--model", default="apertus-v1.5-70b")
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    gold = read_jsonl(a.gold)
    first = {r["result"]["message_id"]: r for r in read_jsonl(a.first)}
    second = {r["result"]["message_id"]: r for r in read_jsonl(a.second)}
    opts = Options(symptom_check=True, second_opinion_model=a.model)
    rows, asked = [], 0
    for g in gold:
        row = json.loads(json.dumps(first[g["message_id"]]))
        t2 = second[g["message_id"]]["trace"]
        row["trace"]["second_opinion"] = {
            "model": a.model,
            "prompt_version": "p3",
            "raw": t2.get("raw") or [],
            "finish": t2.get("finish") or [],
        }
        out = replay(row, g, opts)
        asked += "second_opinion" in out["trace"]
        rows.append(out)
    res = {r["result"]["message_id"]: r["result"] for r in rows}
    print(HEADER)
    print(fmt(f"{a.first.stem} + second opinion (built-in path)", score(gold, res)))
    print(f"\nsecond model asked for {asked} of {len(gold)} messages")
    if a.out:
        a.out.write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
