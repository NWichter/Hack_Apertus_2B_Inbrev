"""CHF per 1,000 messages from measured runs and cited prices (all prices excl. VAT).

  python scripts/cost_model.py --offline runs/offline/<run>/predictions.jsonl --api runs/gold-8b.jsonl runs/gold-70b.jsonl
"""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

PRICES = {
    "electricity_chf_kwh": (0.2511, "ElCom 2026, median category C2 (small business), strompreis.elcom.admin.ch"),
    "box_power_w": (39.0, "ServeTheHome 2024, ASRock 4X4 BOX-8840U sustained load 38-39 W"),
    "box_idle_w": (8.0, "ServeTheHome 2024, idle 6.5-9 W"),
    "box_chf": (554.0 + 150.0, "barebone CHF 554 (digitec search result, not verified) + 32 GB RAM and SSD, assumed CHF 150"),
    "box_years": (3.0, "assumed depreciation period"),
    "infomaniak_cpu_chf_h": (0.0448, "Infomaniak Public Cloud a8_ram32 (8 vCPU, 32 GB), price list 2026-10-04"),
    "infomaniak_l4_chf_h": (0.2985, "Infomaniak Public Cloud nvl4_a8_ram16 (NVIDIA L4), price list 2026-10-04"),
    "infomaniak_70b_in_chf_mtok": (0.70, "Infomaniak AI Services, swiss-ai/Apertus-v1.5-70B input, 2026-10-04"),
    "infomaniak_70b_out_chf_mtok": (2.50, "Infomaniak AI Services, swiss-ai/Apertus-v1.5-70B output, 2026-10-04"),
    "messages_per_day": (60.0, "assumption for one practice, to be checked in interviews"),
}


def load(path: Path) -> list[dict]:
    return [json.loads(x)["trace"] for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", type=Path, required=True, help="predictions of the local CPU run")
    ap.add_argument("--wall-s", type=float, default=None, help="wall time of the local run (default: sum of latencies)")
    ap.add_argument("--api", type=Path, nargs="*", default=[])
    ap.add_argument("--report", type=Path, default=None)
    a = ap.parse_args()
    v = {k: x[0] for k, x in PRICES.items()}
    tr = [t for t in load(a.offline) if not t.get("error")]
    lat = [t["latency_s"] for t in tr]
    s_msg = (a.wall_s / len(tr)) if a.wall_s else statistics.mean(lat)
    out_tok = statistics.mean(t["completion_tokens"] for t in tr)
    k = tr[0].get("options", {}).get("samples", "?")
    lines = ["# Cost per 1,000 messages (CHF, excl. VAT)", ""]
    lines.append(f"Local CPU run: n = {len(tr)}, {s_msg:.1f} s per message ({k} sample(s)), median latency {statistics.median(lat):.1f} s, "
                 f"p95 {sorted(lat)[int(0.95 * (len(lat) - 1))]:.1f} s, {out_tok:.0f} output tokens per message, "
                 f"{3600 / s_msg:.0f} messages per hour, {86400 / s_msg:.0f} per day on one box.")
    lines.append("")
    kwh = s_msg * 1000 * v["box_power_w"] / 3.6e6
    energy = kwh * v["electricity_chf_kwh"]
    per_year = v["messages_per_day"] * 365
    hw_year = v["box_chf"] / v["box_years"]
    idle_year = v["box_idle_w"] * 24 * 365 / 1000 * v["electricity_chf_kwh"]
    full = (hw_year + idle_year) / per_year * 1000 + energy
    cloud_cpu = s_msg * 1000 / 3600 * v["infomaniak_cpu_chf_h"]
    rows = [
        ("On-prem CPU box, energy only (measured time x 39 W)", energy, f"{kwh:.2f} kWh per 1,000 messages"),
        (f"On-prem CPU box, full cost at {v['messages_per_day']:.0f} messages/day", full, "depreciation + idle power + energy"),
        ("Swiss cloud CPU VM (Infomaniak 8 vCPU), billed only while sorting", cloud_cpu, "assumes our measured CPU time; other CPU, not measured"),
        ("Swiss cloud CPU VM kept on 24/7, per practice", v["infomaniak_cpu_chf_h"] * 24 * 365 / per_year * 1000, f"{v['infomaniak_cpu_chf_h'] * 24 * 30:.0f} CHF per month"),
        ("Swiss cloud GPU VM (Infomaniak L4) kept on 24/7, per practice", v["infomaniak_l4_chf_h"] * 24 * 365 / per_year * 1000, f"{v['infomaniak_l4_chf_h'] * 24 * 30:.0f} CHF per month; throughput not measured"),
    ]
    for path in a.api:
        t = [x for x in load(path) if not x.get("error")]
        pin = statistics.mean(x["prompt_tokens"] for x in t)
        pout = statistics.mean(x["completion_tokens"] for x in t)
        c = (pin * v["infomaniak_70b_in_chf_mtok"] + pout * v["infomaniak_70b_out_chf_mtok"]) / 1000
        rows.append((f"Swiss token API at the Apertus 70B price, tokens measured in `{path.name}`", c, f"{pin:.0f} in / {pout:.0f} out tokens per message"))
    lines += ["| Setup | CHF per 1,000 messages | Basis |", "| --- | --- | --- |"]
    lines += [f"| {n} | {c:.2f} | {b} |" for n, c, b in rows]
    lines += ["", "Inputs:", ""] + [f"- `{k}` = {x[0]}: {x[1]}" for k, x in PRICES.items()]
    text = "\n".join(lines) + "\n"
    if a.report:
        a.report.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
