"""Agreement between the grid labels and two open-weights model annotators, and how much the
reported results depend on which label source is taken as truth.

Model annotators are not people. Agreement measures how consistently the written label rules
can be applied to the text; it does not show that a label is clinically correct.

    python scripts/agreement.py \
        --gold gold=<DATA_DIR>/gold-set/merged.v0.jsonl --gold swiss=data/ood/swiss_practice_inbox.jsonl \
        --ann A=runs/annotation/nemotron-super.jsonl --ann B=runs/annotation/gpt-oss-120b.jsonl \
        --pred gold:inbrev-8b-p3=runs/p3/gold-p3-8b.jsonl ... \
        --report evidence/agreement/agreement.md --review <DATA_DIR>/review/disputed.md

No model calls. Bootstrap intervals use seed 2026.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path

from inbrev.baselines import keywords
from inbrev.evaluate import load_predictions, wilson

FIELDS = {
    "route": ("route", "route"),
    "deadline": ("deadline", "deadline"),
    "clinical": ("safety_flag", "clinical_content"),
    "ambiguous": ("abstain", "ambiguous"),
}
B = 2000
UNDEFINED = 0  # bootstrap resamples where kappa is undefined (one class only); reported


def read_jsonl(p: Path) -> list[dict]:
    return [
        json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()
    ]


def cohen(a: list, b: list) -> float | None:
    n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb.get(k, 0) for k in ca) / (n * n)
    return None if pe == 1 else (po - pe) / (1 - pe)


def fleiss(rows: list[list]) -> float | None:
    n = len(rows)
    if n == 0:
        return None
    m = len(rows[0])
    cats = sorted({c for r in rows for c in r}, key=str)
    p_i = []
    totals = Counter()
    for r in rows:
        c = Counter(r)
        totals.update(c)
        p_i.append((sum(v * v for v in c.values()) - m) / (m * (m - 1)))
    p_bar = sum(p_i) / n
    p_e = sum((totals[k] / (n * m)) ** 2 for k in cats)
    return None if p_e == 1 else (p_bar - p_e) / (1 - p_e)


def boot(fn, cols: list[list], seed: int = 2026) -> tuple[float, float] | None:
    n = len(cols[0])
    if n < 5:
        return None
    rng = random.Random(seed)
    vals = []
    global UNDEFINED
    for _ in range(B):
        idx = [rng.randrange(n) for _ in range(n)]
        v = fn(*[[c[i] for i in idx] for c in cols])
        if v is not None:
            vals.append(v)
        else:
            UNDEFINED += 1
    if not vals:
        return None
    vals.sort()
    return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]


def fmt(v, ci=None) -> str:
    if v is None:
        return "–"
    s = f"{v:.2f}"
    if ci:
        s += f" [{ci[0]:.2f}, {ci[1]:.2f}]"
    return s


def frac(k: int, n: int) -> str:
    if n == 0:
        return "–"
    lo, hi = wilson(k, n)
    return f"{k}/{n} [{lo:.2f}, {hi:.2f}]"


def kv(items: list[str]) -> dict[str, str]:
    out = {}
    for it in items:
        k, v = it.split("=", 1)
        out[k] = v
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", action="append", required=True, help="set=path")
    ap.add_argument(
        "--ann", action="append", required=True, help="name=path (two annotators)"
    )
    ap.add_argument("--pred", action="append", default=[], help="set:name=path")
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument(
        "--review",
        type=Path,
        help="Markdown review list with message texts (not for the repo)",
    )
    a = ap.parse_args()

    sets = {k: read_jsonl(Path(v)) for k, v in kv(a.gold).items()}
    ids = [r["message_id"] for rows in sets.values() for r in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("message ids must be unique across sets")
    anns = {}
    meta = {}
    for name, path in kv(a.ann).items():
        d = {}
        models = Counter()
        cost = 0.0
        for r in read_jsonl(Path(path)):
            cost += r.get("cost") or 0.0
            if r.get("annotation"):
                d[r["message_id"]] = r["annotation"]
                models[r["annotator_model"]] += 1
        anns[name] = d
        meta[name] = {"models": dict(models), "cost_usd": round(cost, 4)}
    an = list(anns)
    if len(an) != 2:
        raise SystemExit("exactly two annotators expected")
    A, Bn = an

    lines = ["# Label agreement: grid labels vs. two open-weights model annotators", ""]
    lines += [
        "Annotators are language models, not people: "
        + "; ".join(
            f"**{n}** = {', '.join(meta[n]['models'])} (cost {meta[n]['cost_usd']} USD)"
            for n in an
        )
        + ". They saw only received time, channel, sender, subject and body plus the written label rules"
        " (`scripts/annotate_open_models.py`, guideline a1), never the grid labels or Inbrev output."
        " The grid label is the label the generator was asked to write the text for."
        " κ = Cohen's kappa; Fleiss κ over all three; 95 % bootstrap intervals (2,000 resamples, seed 2026).",
        "",
    ]
    result = {"annotators": meta, "sets": {}}
    all_rows = []
    for sname, rows in sets.items():
        rows = [
            r
            for r in rows
            if r["message_id"] in anns[A] and r["message_id"] in anns[Bn]
        ]
        all_rows += [(sname, r) for r in rows]
    missing = len(ids) - len(all_rows)
    groups = {"all": [r for _, r in all_rows]}
    for sname in sets:
        groups[sname] = [r for s, r in all_rows if s == sname]

    lines += ["## Agreement per label", ""]
    lines += [
        "| Set | n | Label | grid–"
        + A
        + " | grid–"
        + Bn
        + f" | {A}–{Bn} | Fleiss κ | raw agreement all three |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for gname, rows in groups.items():
        res = {}
        for lab, (gk, ak) in FIELDS.items():
            g = [r["label"][gk] for r in rows]
            x = [anns[A][r["message_id"]][ak] for r in rows]
            y = [anns[Bn][r["message_id"]][ak] for r in rows]
            k1, k2, k3 = cohen(g, x), cohen(g, y), cohen(x, y)
            fl = fleiss([list(t) for t in zip(g, x, y)])
            c1, c2, c3 = boot(cohen, [g, x]), boot(cohen, [g, y]), boot(cohen, [x, y])
            cf = boot(
                lambda p, q, s: fleiss([list(t) for t in zip(p, q, s)]), [g, x, y]
            )
            raw = sum(p == q == s for p, q, s in zip(g, x, y))
            res[lab] = {
                "n": len(rows),
                "grid_A": k1,
                "grid_B": k2,
                "A_B": k3,
                "fleiss": fl,
                "all_three": raw,
            }
            lines.append(
                f"| {gname} | {len(rows)} | {lab} | {fmt(k1, c1)} | {fmt(k2, c2)} | {fmt(k3, c3)} | {fmt(fl, cf)} | {raw}/{len(rows)} |"
            )
        result["sets"][gname] = res
    lines.append("")

    # Disputed messages: any annotator disagrees with the grid on route or clinical content.
    disputed = []
    for sname, r in all_rows:
        mid = r["message_id"]
        g = r["label"]
        x, y = anns[A][mid], anns[Bn][mid]
        why = []
        if not (g["route"] == x["route"] == y["route"]):
            why.append("route")
        if not (g["safety_flag"] == x["clinical_content"] == y["clinical_content"]):
            why.append("clinical")
        if why:
            both = (x["route"] == y["route"] != g["route"]) or (
                x["clinical_content"] == y["clinical_content"] != g["safety_flag"]
            )
            disputed.append((sname, r, x, y, why, both))
    dis_ids = {r["message_id"] for _, r, *_ in disputed}
    both_ids = {r["message_id"] for _, r, _, _, _, b in disputed if b}
    lines += [
        f"Messages without an annotation from both models (left out): {missing}. Bootstrap resamples with an undefined κ (only one class drawn) are skipped ({UNDEFINED} in total over all cells, {B} resamples per cell); intervals on sparse labels are therefore conditional. A κ of 1.00 [1.00, 1.00] means no disagreement was observed, not zero uncertainty. Fleiss κ treats the three sources as interchangeable raters (they are fixed); it is given as a summary only.",
        "",
        "## Disputed messages",
        "",
        f"{len(dis_ids)} of {len(all_rows)} messages have at least one annotator disagreeing with the grid on route or clinical content; "
        f"in {len(both_ids)} of them both annotators agree with each other against the grid (candidates for a wrong grid label or a text that does not fit its spec; two models agreeing is a hint, not proof). "
        "These are the review queue for a person; nothing was relabelled.",
        "",
        "| Set | disputed route | disputed clinical | both annotators against grid |",
        "| --- | --- | --- | --- |",
    ]
    for sname in sets:
        sub = [d for d in disputed if d[0] == sname]
        lines.append(
            f"| {sname} | {sum('route' in d[4] for d in sub)} | {sum('clinical' in d[4] for d in sub)} | {sum(d[5] for d in sub)} |"
        )
    lines.append("")

    # Sensitivity: score systems against each label source.
    preds = {}
    for item in a.pred:
        key, path = item.split("=", 1)
        sname, pname = key.split(":", 1)
        preds.setdefault(sname, {})[pname] = path
    if preds:
        lines += [
            "## Do the conclusions depend on the label source?",
            "",
            "Route accuracy and clinical-exclusion recall of each system, scored against the grid labels, against each model annotator,"
            " against the majority of the three, and on the consensus subset (grid and both annotators agree on route and clinical content)."
            " The consensus subset leaves out all disputed messages, which can inflate scores; it is shown only to see whether the ranking of systems changes. Majority: two of three; when all three route labels differ, the grid label is kept (ties: see count below). Intervals are per system (Wilson), not paired tests.",
            "",
            "| Set | System | Route vs grid | vs "
            + A
            + " | vs "
            + Bn
            + " | vs majority | consensus subset | Clinical recall vs grid | consensus subset | vs "
            + A
            + " | vs "
            + Bn
            + " | vs majority |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        result["sensitivity"] = {}
        tie_note = {}
        for sname, pmap in preds.items():
            rows = [r for s, r in all_rows if s == sname]
            systems = {"keyword rules": keywords(rows)}
            for pname, path in pmap.items():
                systems[pname] = load_predictions(Path(path), rows)[0]
            for sysname, pr in systems.items():
                srcs = {"grid": [], A: [], Bn: [], "maj": []}
                ties = 0
                for r in rows:
                    mid = r["message_id"]
                    g = (r["label"]["route"], r["label"]["safety_flag"])
                    x = (anns[A][mid]["route"], anns[A][mid]["clinical_content"])
                    y = (anns[Bn][mid]["route"], anns[Bn][mid]["clinical_content"])
                    mr = Counter([g[0], x[0], y[0]]).most_common(1)[0]
                    ties += mr[1] < 2
                    maj = (
                        mr[0] if mr[1] >= 2 else g[0],
                        [g[1], x[1], y[1]].count(True) >= 2,
                    )
                    srcs["grid"].append(g)
                    srcs[A].append(x)
                    srcs[Bn].append(y)
                    srcs["maj"].append(maj)
                cells = []
                for src in ("grid", A, Bn, "maj"):
                    ok = sum(p.get("route") == t[0] for p, t in zip(pr, srcs[src]))
                    cells.append(frac(ok, len(rows)))
                cons = [i for i, r in enumerate(rows) if r["message_id"] not in dis_ids]
                ok = sum(pr[i].get("route") == rows[i]["label"]["route"] for i in cons)
                cells.append(frac(ok, len(cons)))
                for src in ("grid", "cons", A, Bn, "maj"):
                    if src == "cons":
                        pos = [i for i in cons if srcs["grid"][i][1]]
                    else:
                        pos = [i for i, t in enumerate(srcs[src]) if t[1]]
                    tp = sum(bool(pr[i].get("safety_flag")) for i in pos)
                    cells.append(frac(tp, len(pos)))
                lines.append(f"| {sname} | {sysname} | " + " | ".join(cells) + " |")
                tie_note[sname] = ties
                result["sensitivity"][f"{sname}:{sysname}"] = cells
        lines.append("")
        lines.append("Three-way route ties (grid label kept): " + ", ".join(f"{k} {v}" for k, v in tie_note.items()) + ".")
        lines.append("")

    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    a.report.with_suffix(".json").write_text(
        json.dumps(result, indent=1, default=str), encoding="utf-8"
    )
    print("\n".join(lines))

    if a.review:
        out = [
            "# Review list: disputed labels",
            "",
            "Two open-weights models (not people) labelled blind. Listed are all messages where at least one model",
            "differs from the grid label, first those where both models disagree with the grid. Decide per message:",
            "grid right / model right / text does not fit the specification. Nothing was relabelled automatically.",
            "",
        ]
        disputed.sort(key=lambda d: (not d[5], d[0], d[1]["message_id"]))
        for sname, r, x, y, why, both in disputed:
            g = r["label"]
            out += [
                f"## {r['message_id']} ({sname}) – disputed: {', '.join(why)}{' – both models against the grid' if both else ''}",
                "",
                "| Source | Route | Deadline | Clinical | Ambiguous |",
                "| --- | --- | --- | --- | --- |",
                f"| Grid | {g['route']} | {g['deadline']} | {g['safety_flag']} | {g['abstain']} |",
                f"| {A} | {x['route']} | {x['deadline']} | {x['clinical_content']} | {x['ambiguous']} |",
                f"| {Bn} | {y['route']} | {y['deadline']} | {y['clinical_content']} | {y['ambiguous']} |",
                "",
                f"Received {r.get('received_at')} · {r.get('channel')} · {r.get('sender')}",
                "",
                f"**{r.get('subject')}**",
                "",
                "\n".join("> " + ln for ln in (r.get("body") or "").splitlines()),
                "",
                "Decision: [ ] grid  [ ] model  [ ] text does not fit  · Note:",
                "",
            ]
        a.review.parent.mkdir(parents=True, exist_ok=True)
        a.review.write_text("\n".join(out), encoding="utf-8")
        print(f"review list: {len(disputed)} messages -> {a.review}")


if __name__ == "__main__":
    main()
