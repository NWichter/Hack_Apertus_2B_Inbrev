"""Where does Apertus beat the keyword rules, and what does a rules-first hybrid cost?

Uses stored predictions only (no model call). Hybrid: if exactly one keyword family
matches and the lexical net is silent, the rules decide; otherwise Inbrev (Apertus) decides.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from inbrev import taxonomy
from inbrev.baselines import _KW, keywords
from inbrev.evaluate import _ci, macro_f1, wilson
from inbrev.extract import source_text
from inbrev.runner import read_jsonl
from inbrev.safety import lexical_flag


def rule_is_clear(text: str) -> bool:
    hits = [r for r, rx in _KW.items() if rx.search(text)]
    return len(hits) == 1 and not lexical_flag(text)


def metrics(gold: list[dict], pred: list[dict]) -> dict:
    gl = [g["label"] for g in gold]
    n = len(gold)
    route_ok = sum(x["route"] == p["route"] for x, p in zip(gl, pred))
    s_pos = sum(x["safety_flag"] for x in gl)
    s_tp = sum(x["safety_flag"] and p["safety_flag"] for x, p in zip(gl, pred))
    t_pos = sum(x["deadline"] == "today" for x in gl)
    t_tp = sum(x["deadline"] == "today" and p["deadline"] == "today" for x, p in zip(gl, pred))
    dl_ok = sum(x["deadline"] == p["deadline"] for x, p in zip(gl, pred))
    f1, _ = macro_f1([x["route"] for x in gl], [p["route"] for p in pred], taxonomy.routes())
    return {
        "n": n,
        "route": (route_ok, n),
        "macro_f1": f1,
        "safety": (s_tp, s_pos),
        "today": (t_tp, t_pos),
        "deadline": (dl_ok, n),
    }


def mcnemar_exact(b: int, c: int) -> float:
    from math import comb

    k, m = min(b, c), b + c
    if m == 0:
        return 1.0
    return min(1.0, 2 * sum(comb(m, i) for i in range(k + 1)) / 2**m)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("gold", type=Path)
    ap.add_argument("predictions", type=Path)
    ap.add_argument("--report", type=Path, required=True)
    a = ap.parse_args()
    gold = read_jsonl(a.gold)
    rows = {r["result"]["message_id"]: r["result"] for r in read_jsonl(a.predictions)}
    gold = [g for g in gold if g["message_id"] in rows]
    llm = [rows[g["message_id"]] for g in gold]
    kw = keywords(gold)
    texts = [source_text(g.get("subject"), g.get("body")) for g in gold]
    clear = [rule_is_clear(t) for t in texts]
    hybrid = [k if c else l for k, l, c in zip(kw, llm, clear)]

    lines = [f"# Apertus vs. keyword rules vs. rules-first hybrid", "", f"Gold `{a.gold.name}`, predictions `{a.predictions.name}`, n = {len(gold)}", ""]
    lines += ["| Setup | Model calls | Route acc | Macro-F1 | Clinical exclusion recall | Today recall | Deadline acc |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for name, pred, calls in (("Keyword rules", kw, 0), ("Inbrev (Apertus)", llm, len(gold)), ("Hybrid: rules if clear, else Apertus", hybrid, len(gold) - sum(clear))):
        m = metrics(gold, pred)
        lines.append(f"| {name} | {calls} | {_ci(*m['route'])} | {m['macro_f1']:.3f} | {_ci(*m['safety'])} | {_ci(*m['today'])} | {_ci(*m['deadline'])} |")

    gl = [g["label"] for g in gold]
    b = sum(x["route"] == l["route"] and x["route"] != k["route"] for x, l, k in zip(gl, llm, kw))
    c = sum(x["route"] != l["route"] and x["route"] == k["route"] for x, l, k in zip(gl, llm, kw))
    lines += ["", f"Route, paired: Apertus right and rules wrong {b}, rules right and Apertus wrong {c}, exact McNemar p = {mcnemar_exact(b, c):.3g}.", ""]
    clear_idx = [i for i, cl in enumerate(clear) if cl]
    if clear_idx:
        ok_kw = sum(gl[i]["route"] == kw[i]["route"] for i in clear_idx)
        ok_llm = sum(gl[i]["route"] == llm[i]["route"] for i in clear_idx)
        missed = [gold[i]["message_id"] for i in clear_idx if gl[i]["safety_flag"]]
        lines += [f"Rules are clear on {len(clear_idx)} of {len(gold)} messages: route correct rules {_ci(ok_kw, len(clear_idx))}, Apertus {_ci(ok_llm, len(clear_idx))}. Safety cases among them (missed by the hybrid unless Apertus is asked): {', '.join(missed) or 'none'}.", ""]

    def group_table(title: str, key) -> None:
        groups = defaultdict(list)
        for i, g in enumerate(gold):
            groups[key(g)].append(i)
        lines.extend([f"**{title}**", "", "| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |", "| --- | --- | --- | --- | --- | --- |"])
        for gname, idx in sorted(groups.items(), key=lambda kv: (-len(kv[1]), str(kv[0]))):
            sp = sum(gl[i]["safety_flag"] for i in idx)
            lines.append(
                f"| {gname} | {len(idx)} | {_ci(sum(gl[i]['route'] == kw[i]['route'] for i in idx), len(idx))} | {_ci(sum(gl[i]['route'] == llm[i]['route'] for i in idx), len(idx))} "
                f"| {_ci(sum(gl[i]['safety_flag'] and kw[i]['safety_flag'] for i in idx), sp)} | {_ci(sum(gl[i]['safety_flag'] and llm[i]['safety_flag'] for i in idx), sp)} |"
            )
        lines.append("")

    group_table("By gold route", lambda g: g["label"]["route"])
    group_table("By writing level", lambda g: (g.get("meta") or {}).get("writing_level"))
    group_table("Mixed topics", lambda g: (g.get("meta") or {}).get("mixed_topic"))
    group_table("By safety case type", lambda g: (g.get("meta") or {}).get("safety_case"))
    group_table("By language", lambda g: g.get("language"))
    group_table("By generator", lambda g: g.get("generator") or g.get("source"))
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:16]))


if __name__ == "__main__":
    main()
