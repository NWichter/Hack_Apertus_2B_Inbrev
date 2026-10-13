"""Staff time and money per practice: a transparent model, not a measurement.

Measured inputs come from a stored run (share handled without a person, share of false clinical
flags). Everything else is an ASSUMPTION with a low / base / high value; the interviews and the
time trial in the interview guide are meant to replace them. No model call.

    python scripts/value_model.py <gold.jsonl> <predictions.jsonl> [--report evidence/value/value-model.md]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from inbrev.evaluate import automatic, load_predictions

# name: (low, base, high, unit, basis)
ASSUMPTIONS = {
    "messages_per_day": (
        30,
        60,
        120,
        "messages",
        "assumption for a 2-3 doctor practice; to be asked in interviews",
    ),
    "manual_s": (
        30,
        60,
        120,
        "s per message",
        "MPA reads, decides route and deadline, forwards; assumption, to be timed (guide part C)",
    ),
    "review_s": (
        20,
        15,
        10,
        "s per message",
        "MPA checks an automatic suggestion with its quote; assumption, to be timed",
    ),
    "false_flag_doctor_s": (
        60,
        30,
        15,
        "s per false flag",
        "doctor glance at a message wrongly flagged as clinical; assumption",
    ),
    "mpa_chf_h": (
        40,
        50,
        60,
        "CHF per hour",
        "MPA full employer cost; assumption (project spec), no sourced wage table",
    ),
    "doctor_chf_h": (200, 150, 120, "CHF per hour", "GP time value; assumption"),
    "inbrev_chf_per_1000": (
        30,
        12,
        6,
        "CHF per 1,000 messages",
        "on-prem box, scripts/cost_model.py (CHF 12 at 60/day); low/high scale with volume, assumption",
    ),
    "workdays_per_month": (21, 21, 21, "days", "assumption"),
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("gold", type=Path)
    ap.add_argument("predictions", type=Path)
    ap.add_argument("--report", type=Path)
    a = ap.parse_args()
    gold = [
        json.loads(x)
        for x in a.gold.read_text(encoding="utf-8").splitlines()
        if x.strip()
    ]
    pred, _ = load_predictions(a.predictions, gold)
    n = len(gold)
    if n == 0:
        raise SystemExit("empty gold file")
    auto = sum(automatic(p) for p in pred) / n
    auto_wrong = (
        sum(
            automatic(p) and p["route"] != g["label"]["route"]
            for p, g in zip(pred, gold)
        )
        / n
    )
    false_flag = (
        sum(
            p["safety_flag"] and not g["label"]["safety_flag"]
            for p, g in zip(pred, gold)
        )
        / n
    )
    missed = sum(
        g["label"]["safety_flag"] and not p["safety_flag"] for p, g in zip(pred, gold)
    )
    clinical = sum(g["label"]["safety_flag"] for g in gold)

    def scenario(i: int) -> dict:
        v = {k: x[i] for k, x in ASSUMPTIONS.items()}
        m = v["messages_per_day"]
        saved_mpa_s = m * auto * (v["manual_s"] - v["review_s"])
        # A wrongly routed automatic message costs one more manual handling later.
        rework_s = m * auto_wrong * v["manual_s"]
        doctor_s = m * false_flag * v["false_flag_doctor_s"]
        mpa_min = (saved_mpa_s - rework_s) / 60
        chf_day = (
            mpa_min / 60 * v["mpa_chf_h"]
            - doctor_s / 3600 * v["doctor_chf_h"]
            - m * v["inbrev_chf_per_1000"] / 1000
        )
        return {
            "mpa_min_day": mpa_min,
            "doctor_min_day": doctor_s / 60,
            "chf_day": chf_day,
            "chf_month": chf_day * v["workdays_per_month"],
            "break_even_manual_s": float("inf")
            if auto <= auto_wrong
            else (
                (
                    doctor_s / 3600 * v["doctor_chf_h"]
                    + m * v["inbrev_chf_per_1000"] / 1000
                )
                * 3600
                / v["mpa_chf_h"]
                / m
                + auto * v["review_s"]
            )
            / (auto - auto_wrong),
        }

    rows = [scenario(i) for i in range(3)]
    lines = [
        "# Value model: staff time and money per practice (assumptions, not measured)",
        "",
        f"Measured on `{a.gold.name}` with `{a.predictions.name}` (n = {n}): automatic share {auto:.2f} (neither abstained nor flagged; the MPA only checks the suggestion and its quote, `review_s`), "
        f"of which wrongly routed {auto_wrong:.3f} of all messages; false clinical flags {false_flag:.3f} of all messages; "
        f"clinical messages missed {missed} of {clinical} (not priced: a missed clinical message is a safety risk that this model does not offset against staff time; safety is reported separately and is the reason every flagged or unsure message goes to a person).",
        "",
        "| Scenario | MPA minutes saved per day | Doctor minutes for false flags per day | Net CHF per day | Net CHF per month | Break-even manual time per message |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for name, r in zip(("cautious", "base", "favourable"), rows):
        lines.append(
            f"| {name} | {r['mpa_min_day']:.0f} | {r['doctor_min_day']:.1f} | {r['chf_day']:.0f} | {r['chf_month']:.0f} | {r['break_even_manual_s']:.0f} s |"
        )
    lines += [
        "",
        "Break-even: the manual handling time per message at which the net CHF value (MPA time saved minus doctor time for false flags minus running cost) is zero in that scenario. "
        "These are scenario projections from assumptions, not measured savings and not confidence bounds.",
        "",
        "Model: saved = messages × automatic share × (manual − review) − messages × wrongly-routed × manual; "
        "cost = false flags × doctor glance + Inbrev running cost.",
        "",
        "| Assumption | cautious | base | favourable | unit | basis |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    lines += [
        f"| `{k}` | {x[0]} | {x[1]} | {x[2]} | {x[3]} | {x[4]} |"
        for k, x in ASSUMPTIONS.items()
    ]
    text = "\n".join(lines) + "\n"
    if a.report:
        a.report.parent.mkdir(parents=True, exist_ok=True)
        a.report.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
