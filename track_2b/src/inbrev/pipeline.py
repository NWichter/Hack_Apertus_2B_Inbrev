"""Inbrev pipeline: model samples -> deterministic checks -> vote -> triage result.

`triage` calls the model; `assemble` is pure and can be replayed on stored raw
samples, so changes to the checks are measured without new model calls.
"""

from __future__ import annotations

import os
import re
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime

from . import prompt, taxonomy
from .config import Settings
from .extract import (
    ahv_numbers,
    detect_language,
    find_quote,
    parse_received,
    source_text,
)
from .llm import LLMClient, LLMError
from .replies import reply_draft
from .safety import lexical_hits
from .verify import Sample, check_sample

DEFAULT_RECEIVED = datetime(2026, 10, 1, 8, 0)


@dataclass
class Options:
    samples: int = 3
    temperature: float = 0.7
    safety_mode: str = "or"  # llm | lexical | or
    abstain_below: float = 0.99  # route vote share needed to run automatically
    use_schema: bool = True
    thinking: bool = False
    mode: str = "admin"  # admin (default) | clinical-triage (optional research mode)

    @classmethod
    def from_env(cls, cfg: Settings) -> "Options":
        return cls(
            samples=cfg.samples,
            temperature=cfg.temperature,
            safety_mode=os.getenv("INBREV_SAFETY_MODE", "or"),
            abstain_below=float(os.getenv("INBREV_ABSTAIN_BELOW", "0.99")),
            mode=os.getenv("INBREV_MODE", "admin"),
        )


CLINICAL_MODES = ("clinical-triage", "clinical_triage")
CLINICAL_DISCLAIMER = (
    "Research prototype, not a medical device, not certified. A clinical mode "
    "would require an MDR/MDSW conformity assessment before any real use."
)

# Prefix match at a word start: "brustschmerz" also hits "Brustschmerzen",
# but "mund" never hits "Mundart" or "gesund".
_ESI_TERMS = {
    1: [
        "bewusstlos", "ohnmacht", "kollabiert", "kann nicht mehr atmen", "keine luft",
        "perte de connaissance", "évanoui", "perso conoscenza", "svenut", "unconscious",
        "passed out", "suizid", "selbstmord", "suicid",
    ],
    2: [
        "brustschmerz", "schmerz in der brust", "schmerzen in der brust", "druck auf der brust",
        "engegefühl", "atemnot", "kurzatmig", "douleur thoracique", "dolore al petto",
        "dolore toracico", "chest pain", "lähmung", "gelähmt", "paralys", "paralisi",
        "hängender mundwinkel", "hängende mundwinkel", "mundwinkel hängt",
        "spricht verwaschen", "starke blutung", "blutet stark", "allergische reaktion",
        "zunge schwillt", "anaphylax",
    ],
    3: [
        "hohes fieber", "fieber über 39", "starke kopfschmerzen", "forte fièvre",
        "febbre alta", "high fever", "severe headache", "krampfanfall", "krampft",
        "convulsion", "seizure",
    ],
}
_ESI_RX = {
    level: re.compile(r"\b(?:" + "|".join(re.escape(t) for t in terms) + ")", re.IGNORECASE)
    for level, terms in _ESI_TERMS.items()
}
_ESI_TEXT = {
    1: ("resuscitation", "immediate", "Keyword match for ESI level 1 wording."),
    2: ("emergency", "emergent", "Keyword match for ESI level 2 wording."),
    3: ("urgent", "urgent", "Keyword match for ESI level 3 wording, or flagged without a keyword match."),
}


def classify_clinical_urgency(text: str, safety_flag: bool) -> dict:
    """Keyword-based ESI-style urgency hint for the optional research mode.

    Only called with --mode clinical-triage (off by default). Not validated, not
    certified, not for patient care. The default admin mode never ranks severity.
    """
    base = {"status": "research_prototype", "disclaimer": CLINICAL_DISCLAIMER}
    if not safety_flag:
        return {
            **base,
            "esi_level": 5,
            "category": "routine",
            "urgency": "none",
            "matched": None,
            "description": "No safety flag; no urgency hint.",
        }
    level, matched = 3, None
    for lvl in (1, 2, 3):
        m = _ESI_RX[lvl].search(text)
        if m:
            level, matched = lvl, m.group()
            break
    cat, urg, desc = _ESI_TEXT[level]
    return {
        **base,
        "esi_level": level,
        "category": cat,
        "urgency": urg,
        "matched": matched,
        "description": desc,
    }


def _vote(values: list) -> tuple[object, float]:
    values = [v for v in values if v is not None]
    if not values:
        return None, 0.0
    ((top, count),) = Counter(values).most_common(1)
    return top, count / len(values)


async def triage(message: dict, client: LLMClient, opts: Options) -> dict:
    received = parse_received(message.get("received_at")) or DEFAULT_RECEIVED
    msgs = prompt.messages_for(message, received)
    call = {
        "model": client.model,
        "prompt_version": prompt.PROMPT_VERSION,
        "error": None,
    }
    try:
        comp = await client.chat(
            msgs,
            schema=prompt.output_schema() if opts.use_schema else None,
            n=opts.samples,
            temperature=opts.temperature if opts.samples > 1 else 0.0,
            extra={"chat_template_kwargs": {"enable_thinking": True}} if opts.thinking else None,
        )
        raw, finish = comp.contents, comp.finish_reasons
        call.update(
            prompt_tokens=comp.prompt_tokens,
            completion_tokens=comp.completion_tokens,
            latency_s=round(comp.latency_s, 3),
            retries=comp.retries,
        )
    except LLMError as e:
        raw, finish = [], []
        call["error"] = str(e)
    return assemble(message, raw, finish, opts, call)


def assemble(
    message: dict, raw: list[str], finish: list[str], opts: Options, call: dict
) -> dict:
    text = source_text(message.get("subject"), message.get("body"))
    received = parse_received(message.get("received_at")) or DEFAULT_RECEIVED
    samples = [check_sample(c, f, text, received.date()) for c, f in zip(raw, finish)]
    good = [s for s in samples if s.ok]
    lex = lexical_hits(text)

    route, route_share = _vote([s.route for s in good])
    route = route or "other"
    majority = [s for s in good if s.route == route]

    llm_safety = any(s.safety_flag for s in good)
    safety = {"llm": llm_safety, "lexical": bool(lex), "or": llm_safety or bool(lex)}[
        opts.safety_mode
    ]
    if not good and opts.safety_mode != "llm":
        safety = True

    if safety or route == "report_received":
        deadline = "today"
        dates = [s.deadline_date for s in good if s.deadline_date]
    else:
        deadline = _vote([s.deadline for s in good])[0] or "none"
        dates = [
            s.deadline_date for s in good if s.deadline == deadline and s.deadline_date
        ]
    deadline_date = Counter(dates).most_common(1)[0][0] if dates else None

    ambiguous_votes = sum(s.ambiguous for s in good)
    reasons = []
    if not good:
        reasons.append("no valid model output")
    else:
        if route_share < opts.abstain_below:
            reasons.append(f"samples disagree on route ({route_share:.2f})")
        if ambiguous_votes * 2 > len(good):
            reasons.append("model marks message as ambiguous")
        if not any(s.route_quote for s in majority):
            reasons.append("no verifiable evidence for route")
    abstain = bool(reasons)

    patient, fields, evidence = _merge_extractions(majority, text, taxonomy.route_fields(route))
    language = _vote([s.language for s in good])[0]
    if language not in taxonomy.LANGUAGES:
        language = detect_language(text)

    route_quote = next((s.route_quote for s in majority if s.route_quote), None)
    if route_quote:
        evidence.insert(0, {"field": "route", "quote": route_quote})
    if safety:
        sq = next(
            (s.safety_quote for s in good if s.safety_flag and s.safety_quote), None
        )
        if sq:
            evidence.append({"field": "safety_flag", "quote": sq})
        elif lex:
            evidence.append(
                {"field": "safety_flag", "quote": text[lex[0][1] : lex[0][2]]}
            )
    if deadline != "none" or deadline_date:
        dq = next(
            (
                s.deadline_quote
                for s in good
                if s.deadline == deadline and s.deadline_quote
            ),
            None,
        )
        if dq:
            evidence.append({"field": "deadline", "quote": dq})

    is_clinical_triage = opts.mode.lower() in CLINICAL_MODES
    clinical_triage = (
        classify_clinical_urgency(text, safety) if is_clinical_triage else None
    )

    result = {
        "message_id": message.get("message_id") or "",
        "mode": "clinical-triage" if is_clinical_triage else "admin",
        "language": language,
        "route": route,
        "deadline": deadline,
        "deadline_date": deadline_date,
        "assignee": taxonomy.assignee_for(route, safety),
        "safety_flag": safety,
        "abstain": abstain,
        "confidence": round(route_share, 3),
        "patient": patient,
        "fields": fields,
        "evidence": evidence,
        "clinical_triage": clinical_triage,
        "reply_draft": None
        if (safety or abstain)
        else reply_draft(route, language, patient, fields),
    }
    trace = {
        **call,
        "options": asdict(opts),
        "samples": len(samples),
        "valid_samples": len(good),
        "sample_errors": [s.error for s in samples if not s.ok],
        "route_votes": dict(Counter(s.route for s in good)),
        "llm_safety_votes": sum(s.safety_flag for s in good),
        "lexical_safety_hits": [h[0] for h in lex],
        "ambiguous_votes": ambiguous_votes,
        "abstain_reasons": reasons,
        "quote_status": _quote_stats(good),
        "dropped": [d for s in good for d in s.dropped],
        "raw": raw,
        "finish": finish,
    }
    return {"result": result, "trace": trace}


def _merge_extractions(
    samples: list[Sample], text: str, allowed_fields: list[str]
) -> tuple[dict, dict, list]:
    by_field: dict[str, Counter] = {}
    quotes: dict[tuple[str, str], str] = {}
    for s in samples:
        for item in s.extracted:
            by_field.setdefault(item["field"], Counter())[item["value"]] += 1
            quotes.setdefault((item["field"], item["value"]), item["quote"])
    patient = {k: None for k in taxonomy.PATIENT_KEYS}
    fields: dict[str, str] = {}
    evidence = []
    need = max(1, (len(samples) + 1) // 2)
    for name, counter in by_field.items():
        value, count = counter.most_common(1)[0]
        if count < need:
            continue
        group, key = name.split(".", 1)
        if group == "fields" and key not in allowed_fields:
            continue
        if group == "patient":
            patient[key] = value
        else:
            fields[key] = value
        evidence.append({"field": name, "quote": quotes[(name, value)]})
    found_ahv = ahv_numbers(text)
    if found_ahv and not patient["ahv_number"]:
        patient["ahv_number"] = found_ahv[0]
        _, span = find_quote(found_ahv[0], text)
        if span:
            evidence.append(
                {"field": "patient.ahv_number", "quote": text[span[0] : span[1]]}
            )
    return patient, fields, evidence


def _quote_stats(samples: list[Sample]) -> dict:
    c: Counter = Counter()
    for s in samples:
        c[f"route:{s.route_quote_status}"] += 1
        for item in s.extracted:
            c[item["quote_status"]] += 1
        c["dropped"] += len(s.dropped)
    return dict(c)


def replay(row: dict, message: dict, opts: Options) -> dict:
    """Re-run the deterministic part on stored raw samples."""
    trace = row["trace"]
    raw = trace.get("raw") or []
    finish = trace.get("finish") or ["stop"] * len(raw)
    keep = (
        "model",
        "prompt_version",
        "error",
        "prompt_tokens",
        "completion_tokens",
        "latency_s",
        "retries",
    )
    call = {k: trace.get(k) for k in keep}
    out = assemble(message, raw, finish, opts, call)
    out["run"] = row.get("run", {})
    return out
