"""Replay stored runs with only the first k samples (checks, net and vote unchanged). No model call."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from inbrev.pipeline import Options, replay
from inbrev.runner import read_jsonl


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("messages", type=Path)
    ap.add_argument("predictions", type=Path)
    ap.add_argument("--k", type=int, default=1)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    msgs = {m["message_id"]: m for m in read_jsonl(a.messages)}
    opts = Options(samples=a.k)
    rows = []
    for row in read_jsonl(a.predictions):
        row["trace"]["raw"] = (row["trace"].get("raw") or [])[: a.k]
        row["trace"]["finish"] = (row["trace"].get("finish") or [])[: a.k]
        rows.append(replay(row, msgs[row["result"]["message_id"]], opts))
    a.out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    print(json.dumps({"replayed": len(rows), "k": a.k, "out": str(a.out)}))


if __name__ == "__main__":
    main()
