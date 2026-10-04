"""Recompute the review statistics of index.html from an exported review_log.jsonl.

Usage: python kappa.py review_log.jsonl [--gold merged.v0.jsonl]

Standard library only. The numbers match the Statistics view of index.html.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime

FIELDS = [
    ("route", "gold_route"),
    ("deadline", "gold_deadline"),
    ("safety_flag", "gold_safety_flag"),
]
CHANGE_FIELDS = FIELDS + [("abstain", "gold_abstain")]
PASS2_SIZE = 60
PASS2_SEED = 2026
MIN_GAP_S = 48 * 3600


def read_jsonl(path: str) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8-sig") as fh:
        for no, line in enumerate(fh, 1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    print(
                        f"warning: {path}:{no} is not valid JSON, skipped",
                        file=sys.stderr,
                    )
    return rows


def val(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


def cohen_kappa(pairs: list[tuple[str, str]]) -> dict:
    n = len(pairs)
    if not n:
        return {"n": 0, "po": None, "kappa": None, "lo": None, "hi": None}
    cats = sorted({c for p in pairs for c in p})
    ca: dict[str, int] = {}
    cb: dict[str, int] = {}
    agree = 0
    for a, b in pairs:
        agree += a == b
        ca[a] = ca.get(a, 0) + 1
        cb[b] = cb.get(b, 0) + 1
    po = agree / n
    pe = 0.0
    for c in cats:
        pe += (ca.get(c, 0) / n) * (cb.get(c, 0) / n)
    if pe >= 1:
        return {"n": n, "po": po, "kappa": None, "lo": None, "hi": None}
    kappa = (po - pe) / (1 - pe)
    se = math.sqrt((po * (1 - po)) / (n * (1 - pe) * (1 - pe)))
    return {
        "n": n,
        "po": po,
        "kappa": kappa,
        "lo": max(-1.0, kappa - 1.96 * se),
        "hi": min(1.0, kappa + 1.96 * se),
    }


def mulberry32(seed: int):
    state = seed & 0xFFFFFFFF

    def imul(a: int, b: int) -> int:
        return (a * b) & 0xFFFFFFFF

    def rnd() -> float:
        nonlocal state
        state = (state + 0x6D2B79F5) & 0xFFFFFFFF
        t = imul(state ^ (state >> 15), 1 | state)
        t = ((t + imul(t ^ (t >> 7), 61 | t)) & 0xFFFFFFFF) ^ t
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296

    return rnd


def shuffle(items: list, rng) -> list:
    for i in range(len(items) - 1, 0, -1):
        j = math.floor(rng() * (i + 1))
        items[i], items[j] = items[j], items[i]
    return items


def select_pass2(gold_rows: list[dict]) -> list[str]:
    rng = mulberry32(PASS2_SEED)
    by_id = {r["message_id"]: r for r in gold_rows}
    ids = sorted(by_id)
    flagged = [
        i for i in ids if (by_id[i].get("label") or {}).get("safety_flag") is True
    ]
    rest = [
        i for i in ids if (by_id[i].get("label") or {}).get("safety_flag") is not True
    ]
    if len(flagged) > PASS2_SIZE:
        chosen = shuffle(flagged, rng)[:PASS2_SIZE]
    else:
        chosen = flagged + shuffle(rest, rng)[: PASS2_SIZE - len(flagged)]
    return shuffle(chosen, rng)


def parse_ts(s: str) -> float:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def compute(log: list[dict]) -> dict:
    ordered = [
        e
        for _, e in sorted(
            enumerate(log), key=lambda x: (x[1].get("labelled_at", ""), x[0])
        )
    ]
    p1: dict[str, dict] = {}
    p2: dict[str, dict] = {}
    for e in ordered:
        if e.get("pass") == 1:
            p1[e["message_id"]] = e
        elif e.get("pass") == 2:
            p2[e["message_id"]] = e
    both = sorted(i for i in p2 if i in p1)
    p1list = [p1[i] for i in sorted(p1)]
    blind = [e for e in p1list if e.get("mode") == "blind"]
    res = {
        "intra": {},
        "gold": {},
        "gold_blind": {},
        "n_intra": len(both),
        "n_p1": len(p1list),
        "n_blind": len(blind),
        "n_check": len(p1list) - len(blind),
        "n_p2": len(p2),
    }
    for h, g in FIELDS:
        res["intra"][h] = cohen_kappa(
            [(val(p1[i].get(h)), val(p2[i].get(h))) for i in both]
        )
        res["gold"][h] = cohen_kappa([(val(e.get(g)), val(e.get(h))) for e in p1list])
        res["gold_blind"][h] = cohen_kappa(
            [(val(e.get(g)), val(e.get(h))) for e in blind]
        )
    res["changed_per_field"] = {}
    res["gold_diffs"] = []
    for e in p1list:
        diffs = [
            (h, val(e.get(g)), val(e.get(h)))
            for h, g in CHANGE_FIELDS
            if val(e.get(h)) != val(e.get(g))
        ]
        for d in diffs:
            res["changed_per_field"][d[0]] = res["changed_per_field"].get(d[0], 0) + 1
        if diffs:
            res["gold_diffs"].append(
                (e["message_id"], e.get("mode"), e.get("note") or "", diffs)
            )
    res["changed"] = len(res["gold_diffs"])
    res["intra_diffs"] = []
    res["short_gap"] = 0
    for i in both:
        a, b = p1[i], p2[i]
        if parse_ts(b["labelled_at"]) - parse_ts(a["labelled_at"]) < MIN_GAP_S:
            res["short_gap"] += 1
        diffs = [
            (h, val(a.get(h)), val(b.get(h)))
            for h, _ in CHANGE_FIELDS
            if val(a.get(h)) != val(b.get(h))
        ]
        if diffs:
            res["intra_diffs"].append((i, diffs))
    return res


def f3(x) -> str:
    return "n/a" if x is None else f"{x:.3f}"


def kappa_table(title: str, block: dict) -> str:
    out = [
        f"### {title}",
        "",
        "| field | n | agreement | κ | 95% CI |",
        "|---|---:|---:|---:|---:|",
    ]
    for h, _ in FIELDS:
        k = block[h]
        ci = "n/a" if k["kappa"] is None else f"[{f3(k['lo'])}, {f3(k['hi'])}]"
        out.append(f"| {h} | {k['n']} | {f3(k['po'])} | {f3(k['kappa'])} | {ci} |")
    return "\n".join(out) + "\n"


def cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("log", help="review_log.jsonl exported from index.html")
    ap.add_argument(
        "--gold", help="gold JSONL; its labels replace the gold_* fields of the log"
    )
    args = ap.parse_args()

    log = [
        e
        for e in read_jsonl(args.log)
        if e.get("message_id") and e.get("pass") in (1, 2)
    ]
    notes = []
    if args.gold:
        with open(args.gold, "rb") as fh:
            sha = hashlib.sha256(fh.read()).hexdigest()
        gold_rows = [
            r for r in read_jsonl(args.gold) if r.get("message_id") and r.get("label")
        ]
        labels = {r["message_id"]: r["label"] for r in gold_rows}
        other = {e.get("source_file_sha256") for e in log} - {sha, None}
        if other:
            notes.append(
                f"Warning: log entries reference another gold file (SHA-256 {', '.join(sorted(other))}); gold file is {sha}."
            )
        missing = 0
        for e in log:
            lab = labels.get(e["message_id"])
            if lab is None:
                missing += 1
                continue
            e["gold_route"] = lab.get("route")
            e["gold_deadline"] = lab.get("deadline")
            e["gold_safety_flag"] = lab.get("safety_flag") is True
            e["gold_abstain"] = lab.get("abstain") is True
        if missing:
            notes.append(
                f"Warning: {missing} log entries have no message in the gold file; their logged gold_* fields are used."
            )
        expected = set(select_pass2(gold_rows))
        p2_ids = {e["message_id"] for e in log if e["pass"] == 2}
        outside = sorted(p2_ids - expected)
        notes.append(
            f"Pass-2 sample check: {len(p2_ids)} pass-2 messages logged, "
            f"{len(outside)} outside the expected seed-{PASS2_SEED} sample"
            + (f" ({', '.join(outside[:10])})" if outside else "")
            + "."
        )

    r = compute(log)
    print("# Inbrev label review statistics\n")
    print(
        f"Log: `{args.log}`"
        + (f", gold: `{args.gold}`" if args.gold else ", gold from log fields")
        + "\n"
    )
    print(
        f"Latest decision per message and pass. Pass 1: {r['n_p1']} labelled ({r['n_blind']} blind, {r['n_check']} check). "
        f"Pass 2: {r['n_p2']} labelled, {r['n_intra']} with a pass-1 pair. CI: κ ± 1.96·SE, clipped to [−1, 1].\n"
    )
    for n in notes:
        print(f"> {n}\n")
    print(kappa_table("Intra-rater: pass 1 vs pass 2", r["intra"]))
    if r["short_gap"]:
        print(
            f"> {r['short_gap']} pass-2 labels were made less than 48 h after the pass-1 label of the same message.\n"
        )
    print(kappa_table("Human pass 1 vs gold (generator label), all modes", r["gold"]))
    if r["n_check"] and r["n_blind"]:
        print(kappa_table("Human pass 1 vs gold, blind mode only", r["gold_blind"]))
    per_field = " · ".join(
        f"{h}: {r['changed_per_field'].get(h, 0)}" for h, _ in CHANGE_FIELDS
    )
    print("### Changed gold labels\n")
    print(
        f"{r['changed']} of {r['n_p1']} pass-1 messages differ from gold in at least one of route, deadline, "
        f"safety_flag, abstain ({per_field}).\n"
    )
    print(f"### Pass 1 vs gold: differences ({len(r['gold_diffs'])})\n")
    if r["gold_diffs"]:
        print("| message | mode | field: gold → human | note |\n|---|---|---|---|")
        for mid, mode, note, diffs in r["gold_diffs"]:
            print(
                f"| {mid} | {mode} | {'; '.join(f'{f}: {g} → {h}' for f, g, h in diffs)} | {cell(note)} |"
            )
        print()
    print(f"### Pass 1 vs pass 2: differences ({len(r['intra_diffs'])})\n")
    if r["intra_diffs"]:
        print("| message | field: pass 1 → pass 2 |\n|---|---|")
        for mid, diffs in r["intra_diffs"]:
            print(f"| {mid} | {'; '.join(f'{f}: {a} → {b}' for f, a, b in diffs)} |")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
