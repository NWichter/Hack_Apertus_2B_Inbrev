"""Gap study: variants that try to reduce errors Apertus lets through unnoticed.

All variants are computed from stored runs (no model call here):
  base          stored 8B p3 run (3 samples, checks, net, vote)
  sym>=k        8B run with the symptom second pass; flag if >= k verified "yes" samples
  70B           stored 70B p3 run
  +70B gate     8B decides; a message runs automatically only if 70B agrees on the route and
                neither model flags or abstains (as a cascade 70B is called only for messages
                8B would automate; the cost column counts those calls)
  +rules gate   abstain when the keyword rules choose a different route than the model
Prompt variants (safety_first, fewshot, n5) are separate stored runs.

python scripts/gap_study.py --set NAME GOLD.jsonl --run NAME:LABEL=PRED.jsonl ... --report out.md
"""

from __future__ import annotations

import argparse
import copy
from pathlib import Path

from gap_metrics import HEADER, by_id, fmt, read_jsonl, score
from inbrev.baselines import keyword_route
from inbrev.evaluate import automatic
from inbrev.extract import source_text
from inbrev.pipeline import Options, replay


def results(rows: dict, gold: list[dict]) -> dict:
    return {g["message_id"]: rows[g["message_id"]]["result"] for g in gold}


def with_symptom(rows: dict, gold: list[dict], k: int | None) -> dict:
    opts = Options(symptom_check=k is not None, symptom_min_votes=k or 1)
    msgs = {g["message_id"]: g for g in gold}
    return {mid: replay(rows[mid], msgs[mid], opts)["result"] for mid in msgs}


def gate_70b(r8: dict, r70: dict) -> tuple[dict, int]:
    out, calls = {}, 0
    for mid, a in r8.items():
        b = r70[mid]
        x = copy.deepcopy(a)
        if automatic(a):
            calls += 1
            if b["safety_flag"]:
                x["safety_flag"] = True
            elif b["abstain"] or b["route"] != a["route"]:
                x["abstain"] = True
        out[mid] = x
    return out, calls


def gate_rules(res: dict, gold: list[dict]) -> dict:
    out = {}
    for g in gold:
        x = copy.deepcopy(res[g["message_id"]])
        if keyword_route(source_text(g.get("subject"), g.get("body"))) != x["route"]:
            x["abstain"] = True
        out[g["message_id"]] = x
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--set", nargs=2, action="append", metavar=("NAME", "GOLD"), required=True
    )
    ap.add_argument("--run", action="append", default=[], help="SET:LABEL=PATH")
    ap.add_argument("--report", type=Path, required=True)
    a = ap.parse_args()

    gold = []
    for _, path in a.set:
        gold += read_jsonl(Path(path))
    runs: dict[str, dict] = {}
    for item in a.run:
        key, path = item.split("=", 1)
        _, label = key.split(":", 1)
        runs.setdefault(label, {}).update(by_id(Path(path)))

    lines = [
        f"# Gap study on {' + '.join(n for n, _ in a.set)} (n = {len(gold)})",
        "",
        HEADER,
    ]
    variants: dict[str, dict] = {}
    if "base" in runs:
        variants["8B p3 (stored)"] = results(runs["base"], gold)
    if "sym" in runs:
        variants["8B p3 (fresh run, no symptom pass)"] = with_symptom(
            runs["sym"], gold, None
        )
        for k in (1, 2, 3):
            variants[f"8B + symptom pass, flag if >= {k} of 3"] = with_symptom(
                runs["sym"], gold, k
            )
    for label in ("safety_first", "fewshot", "n5"):
        if label in runs:
            variants[f"8B {label}"] = results(runs[label], gold)
    calls_note = []
    if "70b" in runs:
        r70 = results(runs["70b"], gold)
        variants["70B p3"] = r70
        if "base" in runs:
            g, c = gate_70b(results(runs["base"], gold), r70)
            variants["8B + 70B gate"] = g
            calls_note.append(f"8B + 70B gate: 70B called for {c}/{len(gold)} messages")
        if "sym" in runs:
            g, c = gate_70b(with_symptom(runs["sym"], gold, 1), r70)
            variants["8B + symptom >= 1 + 70B gate"] = g
            calls_note.append(
                f"8B + symptom + 70B gate: 70B called for {c}/{len(gold)} messages"
            )
    if "base" in runs:
        variants["8B + rules gate"] = gate_rules(results(runs["base"], gold), gold)
    if "sym" in runs:
        variants["8B + symptom >= 1 + rules gate"] = gate_rules(
            with_symptom(runs["sym"], gold, 1), gold
        )
    for name, res in variants.items():
        lines.append(fmt(name, score(gold, res)))
    lines += ["", *calls_note, ""]
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
