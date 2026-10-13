"""Route study (14 October 2026): variants that try to reduce wrong routes that run automatically.

All variants are computed from stored runs (no model call here). Every 8B run uses the default
symptom pass (INBREV_SYMPTOM_CHECK=1).
  <label>              a stored 8B run (base = p3, p4 = sharper route boundaries, p4fs = p4 + few-shot)
  <label> + 70B SO     70B as second opinion for low-confidence messages only: a message 8B would run
                       automatically counts as low-confidence when the keyword rules choose another
                       route. Then 70B (stored p3 run) is asked; if 70B agrees on the route it runs
                       automatically, otherwise a person decides. 70B is never called for other messages.
  <label> + rules gate reference from the gap study: every low-confidence message goes to a person.
  qwen                 Qwen3.5-9B in the same pipeline (comparison, not part of Inbrev).

python scripts/route_study.py --set NAME GOLD.jsonl ... --run SET:LABEL=PRED.jsonl ... --report out.md
"""

from __future__ import annotations

import argparse
import copy
from pathlib import Path

from gap_metrics import HEADER, by_id, fmt, read_jsonl, score
from inbrev.baselines import keyword_route
from inbrev.evaluate import automatic
from inbrev.extract import source_text


def low_confidence(msg: dict, res: dict) -> bool:
    return (
        keyword_route(source_text(msg.get("subject"), msg.get("body"))) != res["route"]
    )


def second_opinion(gold: list[dict], r8: dict, r70: dict | None) -> tuple[dict, int]:
    out, calls = {}, 0
    for g in gold:
        mid = g["message_id"]
        x = copy.deepcopy(r8[mid])
        if automatic(x) and low_confidence(g, x):
            if r70 is None:
                x["abstain"] = True
            else:
                calls += 1
                b = r70[mid]
                if b["safety_flag"]:
                    x["safety_flag"] = True
                    x["deadline"] = "today"
                elif b["abstain"] or b["route"] != x["route"]:
                    x["abstain"] = True
        out[mid] = x
    return out, calls


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--set", nargs=2, action="append", metavar=("NAME", "GOLD"), required=True
    )
    ap.add_argument("--run", action="append", default=[], help="SET:LABEL=PATH")
    ap.add_argument(
        "--only", help="comma-separated message ids to score (e.g. undisputed subset)"
    )
    ap.add_argument("--title", default="")
    ap.add_argument("--report", type=Path, required=True)
    a = ap.parse_args()

    gold = [r for _, p in a.set for r in read_jsonl(Path(p))]
    if a.only:
        keep = set(Path(a.only).read_text(encoding="utf-8").split())
        gold = [g for g in gold if g["message_id"] in keep]
    runs: dict[str, dict] = {}
    for item in a.run:
        key, path = item.split("=", 1)
        label = key.split(":", 1)[1]
        runs.setdefault(label, {}).update(
            {k: v["result"] for k, v in by_id(Path(path)).items()}
        )

    r70 = runs.get("70b")
    variants, notes = {}, []
    for label in ("base", "p4", "p4fs"):
        if label not in runs:
            continue
        variants[f"8B {label}"] = runs[label]
        if r70 is not None:
            v, c = second_opinion(gold, runs[label], r70)
            variants[f"8B {label} + 70B SO"] = v
            notes.append(
                f"8B {label} + 70B SO: 70B asked for {c} of {len(gold)} messages"
            )
        variants[f"8B {label} + rules gate"] = second_opinion(gold, runs[label], None)[
            0
        ]
    if r70 is not None:
        variants["70B p3 alone"] = r70
    if "qwen" in runs:
        variants["Qwen3.5-9B (comparison)"] = runs["qwen"]

    lines = [
        f"# Route study{': ' + a.title if a.title else ''} (n = {len(gold)})",
        "",
        HEADER,
    ]
    for name, res in variants.items():
        lines.append(fmt(name, score(gold, res)))
    lines += ["", *notes, ""]
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
