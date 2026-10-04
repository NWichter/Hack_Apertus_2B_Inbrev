"""Paired comparison of two prediction files on the same gold set (e.g. prompt p2 vs p3).

python scripts/compare_prompts.py --set gold GOLD.jsonl A.jsonl B.jsonl [--set ...] --report out.md
Route correctness and clinical exclusion are compared per message with an exact McNemar test.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from compare_hybrid import mcnemar_exact
from inbrev.evaluate import _ci
from inbrev.runner import read_jsonl


def load(gold_path: Path, pred_path: Path) -> tuple[list[dict], list[dict]]:
    gold = read_jsonl(gold_path)
    rows = {r["result"]["message_id"]: r["result"] for r in read_jsonl(pred_path)}
    missing = [g["message_id"] for g in gold if g["message_id"] not in rows]
    if missing:
        raise SystemExit(f"{pred_path}: {len(missing)} messages missing")
    return gold, [rows[g["message_id"]] for g in gold]


def stats(gold: list[dict], pred: list[dict]) -> dict:
    gl = [g["label"] for g in gold]
    n = len(gl)
    other = [i for i, x in enumerate(gl) if x["route"] == "other"]
    pos = [i for i, x in enumerate(gl) if x["safety_flag"]]
    flagged = [i for i, p in enumerate(pred) if p["safety_flag"]]
    today = [i for i, x in enumerate(gl) if x["deadline"] == "today"]
    return {
        "route": (sum(x["route"] == p["route"] for x, p in zip(gl, pred)), n),
        "other": (sum(pred[i]["route"] == "other" for i in other), len(other)),
        "other_prec": (
            sum(
                gl[i]["route"] == "other"
                for i, p in enumerate(pred)
                if p["route"] == "other"
            ),
            sum(p["route"] == "other" for p in pred),
        ),
        "safety": (sum(pred[i]["safety_flag"] for i in pos), len(pos)),
        "safety_prec": (sum(gl[i]["safety_flag"] for i in flagged), len(flagged)),
        "today": (sum(pred[i]["deadline"] == "today" for i in today), len(today)),
        "deadline": (sum(x["deadline"] == p["deadline"] for x, p in zip(gl, pred)), n),
        "coverage": (sum(not p["abstain"] for p in pred), n),
    }


def paired(
    gold: list[dict], a: list[dict], b: list[dict], key, subset=None
) -> tuple[int, int, float]:
    idx = subset if subset is not None else range(len(gold))
    ok_a = {i: key(gold[i]["label"], a[i]) for i in idx}
    ok_b = {i: key(gold[i]["label"], b[i]) for i in idx}
    only_b = sum(ok_b[i] and not ok_a[i] for i in idx)
    only_a = sum(ok_a[i] and not ok_b[i] for i in idx)
    return only_b, only_a, mcnemar_exact(only_b, only_a)


def route_ok(x: dict, p: dict) -> bool:
    return x["route"] == p["route"]


def safety_ok(x: dict, p: dict) -> bool:
    return bool(p["safety_flag"])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--set",
        nargs=4,
        action="append",
        metavar=("NAME", "GOLD", "A", "B"),
        required=True,
    )
    ap.add_argument("--labels", nargs=2, default=("A", "B"))
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    la, lb = args.labels

    rows = []
    pairs = []
    for name, gold_p, a_p, b_p in args.set:
        gold, a = load(Path(gold_p), Path(a_p))
        _, b = load(Path(gold_p), Path(b_p))
        sa, sb = stats(gold, a), stats(gold, b)
        for metric, label in (
            ("route", "Route accuracy"),
            ("other", "Recall of route other"),
            ("other_prec", "Precision of route other"),
            ("safety", "Clinical exclusion recall"),
            ("safety_prec", "Clinical exclusion precision"),
            ("today", "Today recall"),
            ("deadline", "Deadline accuracy"),
            ("coverage", "Coverage"),
        ):
            rows.append(
                f"| {name} | {label} | {_ci(*sa[metric])} | {_ci(*sb[metric])} |"
            )
        pos = [i for i, g in enumerate(gold) if g["label"]["safety_flag"]]
        r_b, r_a, r_p = paired(gold, a, b, route_ok)
        s_b, s_a, s_p = paired(gold, a, b, safety_ok, pos)
        changed = sum(x["route"] != y["route"] for x, y in zip(a, b))
        pairs.append(
            f"| {name} | {len(gold)} | {changed} | {r_b} | {r_a} | {r_p:.3g} | {s_b} | {s_a} | {s_p:.3g} |"
        )

    lines = [
        f"# Paired comparison: {la} vs. {lb}",
        "",
        "95 % Wilson intervals, k/n [low, high].",
        "",
        f"| Set | Metric | {la} | {lb} |",
        "| --- | --- | --- | --- |",
        *rows,
        "",
        "Paired per message (exact two-sided McNemar test on the discordant pairs):",
        "",
        f"| Set | n | route changed | route right only with {lb} | route right only with {la} | p | clinical caught only with {lb} | clinical caught only with {la} | p |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        *pairs,
        "",
    ]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
