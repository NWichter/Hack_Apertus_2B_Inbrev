"""Ablation without new model calls: score only the first stored raw sample of a run,
taken at face value (no quote checks, no lexical safety net, no vote, no abstention).

    python scripts/ablation_first_sample.py runs/gold-8b.jsonl runs/gold-8b-first-sample.jsonl
    python -m inbrev eval <gold.jsonl> runs/gold-8b-first-sample.jsonl
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from inbrev import taxonomy  # noqa: E402


def first_sample(row: dict) -> dict:
    raw = (row["trace"].get("raw") or [""])[0]
    try:
        obj = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        obj = {}
    route = obj.get("route") if obj.get("route") in taxonomy.routes() else "other"
    deadline = (
        obj.get("deadline") if obj.get("deadline") in taxonomy.DEADLINES else "none"
    )
    safety = obj.get("safety_flag") is True
    patient = {k: None for k in taxonomy.PATIENT_KEYS}
    fields = {}
    for item in obj.get("extracted") or []:
        name, value = str(item.get("field", "")), item.get("value")
        if "." not in name or value in (None, "", "null"):
            continue
        group, key = name.split(".", 1)
        if group == "patient" and key in patient:
            patient[key] = value
        elif group == "fields":
            fields[key] = value
    result = {
        **row["result"],
        "route": route,
        "deadline": deadline,
        "deadline_date": obj.get("deadline_date"),
        "assignee": taxonomy.assignee_for(route, safety),
        "safety_flag": safety,
        "abstain": False,
        "confidence": 1.0,
        "patient": patient,
        "fields": fields,
        "evidence": [],
    }
    trace = {
        k: row["trace"].get(k)
        for k in ("model", "prompt_version", "prompt_tokens", "latency_s")
    }
    trace.update(
        error=None,
        samples=1,
        valid_samples=1 if obj else 0,
        ablation="first_sample_no_checks",
    )
    return {"result": result, "trace": trace, "run": row.get("run", {})}


def main(src: Path, dst: Path) -> None:
    rows = [
        json.loads(line)
        for line in src.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    dst.write_text(
        "".join(json.dumps(first_sample(r), ensure_ascii=False) + "\n" for r in rows),
        encoding="utf-8",
    )
    print(json.dumps({"rows": len(rows), "out": str(dst)}))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
