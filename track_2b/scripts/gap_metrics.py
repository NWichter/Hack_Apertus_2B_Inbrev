"""Shared metrics for the gap study: what passes automation unnoticed, and what goes to a person.

Unnoticed route error = handled automatically (neither abstained nor flagged) and wrong route.
Unnoticed clinical    = clinical message (gold safety_flag) that is handled automatically.
To a person           = flagged or abstained.
"""

from __future__ import annotations

import json
from pathlib import Path

from inbrev.evaluate import automatic


def read_jsonl(p: Path) -> list[dict]:
    return [
        json.loads(x)
        for x in Path(p).read_text(encoding="utf-8").splitlines()
        if x.strip()
    ]


def by_id(path: Path) -> dict[str, dict]:
    return {r["result"]["message_id"]: r for r in read_jsonl(path)}


def score(gold: list[dict], res: dict[str, dict]) -> dict:
    n = len(gold)
    out = {
        "n": n,
        "route_ok": 0,
        "auto_ok": 0,
        "clin": 0,
        "clin_flag": 0,
        "clin_out": 0,
        "unnoticed_route": 0,
        "unnoticed_clin": 0,
        "to_person": 0,
        "false_flags": 0,
    }
    for g in gold:
        r = res[g["message_id"]]
        lab = g["label"]
        auto = automatic(r)
        out["route_ok"] += r["route"] == lab["route"]
        out["to_person"] += not auto
        out["auto_ok"] += auto and r["route"] == lab["route"]
        out["false_flags"] += bool(r["safety_flag"]) and not lab["safety_flag"]
        if lab["safety_flag"]:
            out["clin"] += 1
            out["clin_flag"] += bool(r["safety_flag"])
            out["clin_out"] += not auto
            out["unnoticed_clin"] += auto
        if auto and r["route"] != lab["route"]:
            out["unnoticed_route"] += 1
    return out


def fmt(name: str, s: dict) -> str:
    return (
        f"| {name} | {s['route_ok']}/{s['n']} | {s['auto_ok']} | {s['clin_flag']}/{s['clin']} | {s['clin_out']}/{s['clin']} | "
        f"{s['unnoticed_route']} | {s['unnoticed_clin']} | {s['to_person']}/{s['n']} | {s['false_flags']} |"
    )


HEADER = (
    "| Variant | Route (model) | Automatic and right | Clinical flagged | Clinical out of automation | Unnoticed wrong route | "
    "Unnoticed clinical | To a person | False flags |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- |"
)
