"""Scoring against gold labels and a Markdown report."""

from __future__ import annotations

import json
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from . import taxonomy
from .extract import fold, parse_date, source_text
from .runner import read_jsonl

BREAKDOWNS = {
    "language": lambda g: g.get("language"),
    "writing_level": lambda g: (g.get("meta") or {}).get("writing_level"),
    "channel": lambda g: g.get("channel"),
    "generator": lambda g: g.get("generator") or g.get("source"),
    "safety_case": lambda g: (g.get("meta") or {}).get("safety_case"),
}


def _f1(p: float, r: float) -> float:
    return 2 * p * r / (p + r) if p + r else 0.0


def _ratio(a: int, b: int) -> float | None:
    return a / b if b else None


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float] | None:
    """95 % Wilson score interval for k successes out of n."""
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0.0, c - h), min(1.0, c + h))


def automatic(p: dict) -> bool:
    """Handled without a person: no abstention and no safety flag (both go to "a person decides")."""
    return not p.get("abstain") and not p.get("safety_flag")


def binary(gold: list[bool], pred: list[bool]) -> dict:
    tp = sum(g and p for g, p in zip(gold, pred))
    fp = sum((not g) and p for g, p in zip(gold, pred))
    fn = sum(g and (not p) for g, p in zip(gold, pred))
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "recall": _ratio(tp, tp + fn),
        "precision": _ratio(tp, tp + fp),
        "recall_ci": wilson(tp, tp + fn),
        "precision_ci": wilson(tp, tp + fp),
    }


def macro_f1(gold: list[str], pred: list[str], labels: list[str]) -> tuple[float, dict]:
    per = {}
    for lab in labels:
        b = binary([g == lab for g in gold], [p == lab for p in pred])
        if b["tp"] + b["fn"] == 0 and b["fp"] == 0:
            continue
        per[lab] = _f1(b["precision"] or 0.0, b["recall"] or 0.0)
    return (sum(per.values()) / len(per) if per else 0.0), per


def _norm_value(field: str, v) -> str | None:
    if v in (None, ""):
        return None
    if "date" in field or field.endswith("birth_date"):
        d = parse_date(str(v))
        if d:
            return d.isoformat()
    return re.sub(r"[^\w]+", " ", fold(str(v))).strip()


def field_scores(gold: list[dict], pred: list[dict]) -> dict:
    stats = defaultdict(lambda: Counter())
    for g, p in zip(gold, pred):
        gl = g["label"]
        pairs = [
            (
                f"patient.{k}",
                (gl.get("patient") or {}).get(k),
                (p.get("patient") or {}).get(k),
            )
            for k in taxonomy.PATIENT_KEYS
        ]
        keys = set((gl.get("fields") or {})) | set((p.get("fields") or {}))
        pairs += [
            (
                f"fields.{k}",
                (gl.get("fields") or {}).get(k),
                (p.get("fields") or {}).get(k),
            )
            for k in keys
        ]
        for name, gv, pv in pairs:
            gv, pv = _norm_value(name, gv), _norm_value(name, pv)
            if gv is None and pv is None:
                continue
            c = stats[name]
            if gv is not None:
                c["gold"] += 1
            if pv is not None:
                c["pred"] += 1
            if (
                gv is not None
                and pv is not None
                and (gv == pv or (len(gv) > 3 and (gv in pv or pv in gv)))
            ):
                c["match"] += 1
    total = Counter()
    for c in stats.values():
        total.update(c)
    out = {}
    for name, c in list(stats.items()) + [("ALL", total)]:
        p, r = _ratio(c["match"], c["pred"]), _ratio(c["match"], c["gold"])
        out[name] = {
            "gold": c["gold"],
            "pred": c["pred"],
            "match": c["match"],
            "precision": p,
            "recall": r,
            "f1": _f1(p or 0, r or 0),
        }
    return out


def score(gold: list[dict], pred: list[dict], traces: list[dict] | None = None) -> dict:
    gl = [g["label"] for g in gold]
    routes = taxonomy.routes()
    groute, proute = [x["route"] for x in gl], [p["route"] for p in pred]
    mf1, per_route = macro_f1(groute, proute, routes)
    covered = [i for i, p in enumerate(pred) if automatic(p)]
    safety = binary([x["safety_flag"] for x in gl], [p["safety_flag"] for p in pred])
    today = binary(
        [x["deadline"] == "today" for x in gl], [p["deadline"] == "today" for p in pred]
    )
    abst = binary(
        [bool(x.get("abstain")) for x in gl], [bool(p.get("abstain")) for p in pred]
    )
    n = len(gold)
    route_ok = sum(a == b for a, b in zip(groute, proute))
    deadline_ok = sum(x["deadline"] == p["deadline"] for x, p in zip(gl, pred))
    out = {
        "n": n,
        "route_accuracy_ci": wilson(route_ok, n),
        "deadline_accuracy_ci": wilson(deadline_ok, n),
        "coverage_ci": wilson(len(covered), n),
        "route_accuracy": sum(a == b for a, b in zip(groute, proute)) / len(gold),
        "route_macro_f1": mf1,
        "route_f1": per_route,
        "deadline_accuracy": sum(
            x["deadline"] == p["deadline"] for x, p in zip(gl, pred)
        )
        / len(gold),
        "assignee_accuracy": sum(
            x["assignee"] == p["assignee"] for x, p in zip(gl, pred)
        )
        / len(gold),
        "safety": safety,
        "today": today,
        "abstain": abst,
        "coverage": len(covered) / len(gold),
        "route_accuracy_covered": _ratio(
            sum(groute[i] == proute[i] for i in covered), len(covered)
        ),
        "all_correct_covered": _ratio(
            sum(
                groute[i] == proute[i]
                and gl[i]["deadline"] == pred[i]["deadline"]
                and gl[i]["safety_flag"] == pred[i]["safety_flag"]
                for i in covered
            ),
            len(covered),
        ),
        "safety_missed_ids": [
            g["message_id"]
            for g, x, p in zip(gold, gl, pred)
            if x["safety_flag"] and not p["safety_flag"]
        ],
        "fields": field_scores(gold, pred),
        "confusion": Counter(
            f"{a}->{b}" for a, b in zip(groute, proute) if a != b
        ).most_common(),
        "coverage_curve": coverage_curve(
            groute, proute, [p.get("confidence", 1.0) for p in pred]
        ),
    }
    if traces:
        out["ops"] = ops_stats(traces, gold)
    return out


def coverage_curve(gold: list[str], pred: list[str], conf: list[float]) -> list[dict]:
    pts = []
    for t in sorted(set(conf)):
        keep = [i for i, c in enumerate(conf) if c >= t]
        pts.append(
            {
                "threshold": t,
                "coverage": len(keep) / len(gold),
                "accuracy": _ratio(sum(gold[i] == pred[i] for i in keep), len(keep)),
            }
        )
    return pts


def ops_stats(traces: list[dict], gold: list[dict]) -> dict:
    pt = [t.get("prompt_tokens") or 0 for t in traces]
    ct = [t.get("completion_tokens") or 0 for t in traces]
    lat = [t["latency_s"] for t in traces if t.get("latency_s") is not None]
    quotes = Counter()
    for t in traces:
        quotes.update(t.get("quote_status") or {})
    samples = sum(t.get("samples", 0) for t in traces)
    return {
        "errors": sum(1 for t in traces if t.get("error")),
        "invalid_samples": sum(len(t.get("sample_errors") or []) for t in traces),
        "samples": samples,
        "sample_error_kinds": Counter(
            e for t in traces for e in (t.get("sample_errors") or [])
        ).most_common(),
        "prompt_tokens_mean": statistics.mean(pt) if pt else 0,
        "completion_tokens_mean": statistics.mean(ct) if ct else 0,
        "latency_mean_s": statistics.mean(lat) if lat else None,
        "latency_p95_s": sorted(lat)[int(0.95 * (len(lat) - 1))] if lat else None,
        "quote_status": dict(quotes),
        "lexical_only_safety": sum(
            1
            for t in traces
            if t.get("lexical_safety_hits") and not t.get("llm_safety_votes")
        ),
    }


def breakdown(gold: list[dict], pred: list[dict], key) -> dict:
    groups = defaultdict(list)
    for i, g in enumerate(gold):
        groups[key(g)].append(i)
    out = {}
    for name, idx in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        gs, ps = [gold[i] for i in idx], [pred[i] for i in idx]
        s = binary(
            [g["label"]["safety_flag"] for g in gs], [p["safety_flag"] for p in ps]
        )
        out[str(name)] = {
            "n": len(idx),
            "route_accuracy": sum(
                g["label"]["route"] == p["route"] for g, p in zip(gs, ps)
            )
            / len(idx),
            "deadline_accuracy": sum(
                g["label"]["deadline"] == p["deadline"] for g, p in zip(gs, ps)
            )
            / len(idx),
            "safety_recall": s["recall"],
            "coverage": sum(automatic(p) for p in ps) / len(idx),
            "route_ok": sum(g["label"]["route"] == p["route"] for g, p in zip(gs, ps)),
            "safety_tp": s["tp"],
            "safety_pos": s["tp"] + s["fn"],
        }
    return out


def load_predictions(path: Path, gold: list[dict]) -> tuple[list[dict], list[dict]]:
    rows = {r["result"]["message_id"]: r for r in read_jsonl(path)}
    missing = [g["message_id"] for g in gold if g["message_id"] not in rows]
    if missing:
        raise SystemExit(
            f"{path}: {len(missing)} gold messages without prediction, e.g. {missing[:3]}"
        )
    ordered = [rows[g["message_id"]] for g in gold]
    return [r["result"] for r in ordered], [r["trace"] for r in ordered]


def errors_table(
    gold: list[dict], pred: list[dict], traces: list[dict] | None, limit: int = 40
) -> list[str]:
    lines = [
        "| id | lang | level | gold route/deadline/safety | predicted | votes | abstain reasons |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    n = 0
    for i, (g, p) in enumerate(zip(gold, pred)):
        L = g["label"]
        if (
            L["route"] == p["route"]
            and L["deadline"] == p["deadline"]
            and L["safety_flag"] == p["safety_flag"]
        ):
            continue
        t = traces[i] if traces else {}
        lines.append(
            f"| {g['message_id']} | {g.get('language')} | {(g.get('meta') or {}).get('writing_level', '')} "
            f"| {L['route']} / {L['deadline']} / {L['safety_flag']} | {p['route']} / {p['deadline']} / {p['safety_flag']}"
            f"{' (abstain)' if p.get('abstain') else ''} | {t.get('route_votes', '')} | {'; '.join(t.get('abstain_reasons') or [])} |"
        )
        n += 1
        if n >= limit:
            break
    return lines


def _fmt(v) -> str:
    if v is None:
        return "–"
    if isinstance(v, float):
        return f"{v:.3f}"
    return str(v)


def _ci(k: int, n: int) -> str:
    w = wilson(k, n)
    return f"{k}/{n} [{w[0]:.2f}, {w[1]:.2f}]" if w else "–"


def render_report(
    gold_path: Path, results: dict[str, dict], details: dict[str, tuple]
) -> str:
    lines = [
        f"# Inbrev evaluation",
        "",
        f"Gold: `{gold_path.name}`, n = {next(iter(results.values()))['n']}",
        "",
    ]
    lines += [
        "| Setup | Route acc | Route macro-F1 | Safety recall | Safety precision | Today recall | Today precision | Deadline acc | Coverage | Route acc (covered) | Field F1 | Tokens in/out | Latency s |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for name, s in results.items():
        ops = s.get("ops") or {}
        tok = (
            f"{ops['prompt_tokens_mean']:.0f}/{ops['completion_tokens_mean']:.0f}"
            if ops
            else "–"
        )
        lines.append(
            f"| {name} | {_fmt(s['route_accuracy'])} | {_fmt(s['route_macro_f1'])} | {_fmt(s['safety']['recall'])} | {_fmt(s['safety']['precision'])} "
            f"| {_fmt(s['today']['recall'])} | {_fmt(s['today']['precision'])} | {_fmt(s['deadline_accuracy'])} | {_fmt(s['coverage'])} "
            f"| {_fmt(s['route_accuracy_covered'])} | {_fmt(s['fields']['ALL']['f1'])} | {tok} | {_fmt(ops.get('latency_mean_s'))} |"
        )
    lines += [
        "",
        "95 % Wilson intervals (k/n [low, high]):",
        "",
        "| Setup | Route acc | Safety recall | Safety precision | Today recall | Deadline acc | Coverage |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for name, s in results.items():
        n = s["n"]
        sf, td = s["safety"], s["today"]
        lines.append(
            f"| {name} | {_ci(round(s['route_accuracy'] * n), n)} | {_ci(sf['tp'], sf['tp'] + sf['fn'])} "
            f"| {_ci(sf['tp'], sf['tp'] + sf['fp'])} | {_ci(td['tp'], td['tp'] + td['fn'])} "
            f"| {_ci(round(s['deadline_accuracy'] * n), n)} | {_ci(round(s['coverage'] * n), n)} |"
        )
    for name, s in results.items():
        gold, pred, traces = details[name]
        if traces is None:
            continue
        lines += ["", f"## {name}", ""]
        lines.append(
            f"Safety missed: {', '.join(s['safety_missed_ids']) or 'none'} · abstain on gold-ambiguous: {s['abstain']['tp']}/{s['abstain']['tp'] + s['abstain']['fn']} · all-correct on covered: {_fmt(s['all_correct_covered'])}"
        )
        lines.append("")
        lines.append(
            f"Ops: `{json.dumps(s.get('ops'), ensure_ascii=False, default=str)}`"
        )
        lines += [
            "",
            "Route F1: " + ", ".join(f"{k} {v:.2f}" for k, v in s["route_f1"].items()),
            "",
        ]
        lines.append(
            "Confusions (gold->pred): "
            + ", ".join(f"{k} ×{v}" for k, v in s["confusion"][:12])
        )
        lines += [
            "",
            "Coverage curve: "
            + ", ".join(
                f"≥{p['threshold']:.2f}: cov {p['coverage']:.2f} acc {_fmt(p['accuracy'])}"
                for p in s["coverage_curve"]
            ),
            "",
        ]
        for bname, key in BREAKDOWNS.items():
            b = breakdown(gold, pred, key)
            if len(b) <= 1:
                continue
            lines += [
                f"**By {bname}**",
                "",
                "| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
            lines += [
                f"| {k} | {v['n']} | {_ci(v['route_ok'], v['n'])} | {_fmt(v['deadline_accuracy'])} | {_ci(v['safety_tp'], v['safety_pos'])} | {_fmt(v['coverage'])} |"
                for k, v in b.items()
            ]
            lines.append("")
        lines += [
            "**Fields**",
            "",
            "| field | gold | pred | match | P | R | F1 |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        lines += [
            f"| {k} | {v['gold']} | {v['pred']} | {v['match']} | {_fmt(v['precision'])} | {_fmt(v['recall'])} | {_fmt(v['f1'])} |"
            for k, v in sorted(s["fields"].items())
        ]
        lines += [
            "",
            "**Errors (route, deadline or safety wrong)**",
            "",
        ] + errors_table(gold, pred, traces)
    return "\n".join(lines) + "\n"


def main_eval(
    gold_path: Path, pred_paths: list[Path], report: Path | None, with_baselines: bool
) -> dict:
    gold = read_jsonl(gold_path)
    results, details = {}, {}
    if with_baselines:
        from .baselines import BASELINES

        for name, fn in BASELINES.items():
            pred = fn(gold)
            results[name] = score(gold, pred)
            details[name] = (gold, pred, None)
    for path in pred_paths:
        pred, traces = load_predictions(path, gold)
        name = path.stem
        results[name] = score(gold, pred, traces)
        details[name] = (gold, pred, traces)
    text = render_report(gold_path, results, details)
    if report:
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(text, encoding="utf-8")
        report.with_suffix(".json").write_text(
            json.dumps(results, ensure_ascii=False, indent=1, default=str),
            encoding="utf-8",
        )
    print(text.split("\n## ")[0])
    return results
