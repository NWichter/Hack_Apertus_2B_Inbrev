"""Deterministic checks on one model sample. Nothing here calls the model."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date

from . import taxonomy
from .extract import (
    AHV_RE,
    ahv_numbers,
    clean_quote,
    dates_in,
    deadline_from_date,
    parse_date,
    quote_span_text,
)


@dataclass
class Sample:
    ok: bool
    raw: str
    error: str | None = None
    language: str | None = None
    route: str | None = None
    route_quote: str | None = None
    route_quote_status: str = "missing"
    ambiguous: bool = False
    safety_flag: bool = False
    safety_quote: str | None = None
    safety_quote_status: str = "missing"
    deadline_model: str | None = None
    deadline: str | None = None
    deadline_date: str | None = None
    deadline_quote: str | None = None
    deadline_quote_status: str = "missing"
    extracted: list[dict] = field(default_factory=list)
    dropped: list[dict] = field(default_factory=list)


def clean_value(field_name: str, value: str | None) -> str | None:
    value = clean_quote(value)
    if not value:
        return None
    if field_name == "patient.birth_date":
        d = parse_date(value)
        return d.isoformat() if d else None
    if field_name == "patient.ahv_number":
        found = ahv_numbers(value)
        return found[0] if found else None
    return value


def _date_consistent(value: str, quote: str) -> bool:
    """A date value must match a date written in its quote, if the quote holds one."""
    in_quote = dates_in(quote)
    if not in_quote:
        return True
    return parse_date(value) in in_quote


def check_sample(raw: str, finish_reason: str, text: str, received: date) -> Sample:
    if finish_reason == "length":
        return Sample(ok=False, raw=raw, error="truncated")
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as e:
        return Sample(ok=False, raw=raw, error=f"json: {e.msg}")
    if not isinstance(obj, dict) or obj.get("route") not in taxonomy.routes():
        return Sample(ok=False, raw=raw, error="route not in taxonomy")

    s = Sample(ok=True, raw=raw)
    s.language = obj.get("language")
    s.route = obj["route"]
    s.ambiguous = bool(obj.get("ambiguous"))
    s.route_quote_status, s.route_quote = quote_span_text(
        obj.get("route_quote") or "", text
    )

    s.safety_flag = bool(obj.get("safety_flag"))
    s.safety_quote_status, s.safety_quote = quote_span_text(
        obj.get("safety_quote") or "", text
    )

    s.deadline_model = (
        obj.get("deadline") if obj.get("deadline") in taxonomy.DEADLINES else "none"
    )
    s.deadline_quote_status, s.deadline_quote = quote_span_text(
        obj.get("deadline_quote") or "", text
    )
    dd = parse_date(obj.get("deadline_date"))
    if dd and s.deadline_quote is None:
        dd = None
    if dd and not _date_consistent(dd.isoformat(), s.deadline_quote):
        dd = None
    if dd and abs((dd - received).days) > 400:
        dd = None
    s.deadline_date = dd.isoformat() if dd else None

    if s.safety_flag or s.route == "report_received":
        s.deadline = "today"
    elif dd:
        s.deadline = deadline_from_date(dd, received)
    elif s.deadline_quote is not None:
        s.deadline = s.deadline_model
    else:
        s.deadline = "none"

    allowed = set(_allowed_fields())
    seen: set[str] = set()
    for item in obj.get("extracted") or []:
        if not isinstance(item, dict):
            continue
        name = item.get("field")
        raw_value = item.get("value")
        if (
            name == "patient.insurance_number"
            and raw_value
            and AHV_RE.search(raw_value)
        ):
            name = "patient.ahv_number"
        value = clean_value(name, raw_value) if name in allowed else None
        status, span_text = quote_span_text(item.get("quote") or "", text)
        reason = None
        if value is None:
            reason = "empty or unparsable value"
        elif span_text is None:
            reason = "quote not in message"
        elif name == "patient.birth_date" and not _date_consistent(value, span_text):
            reason = "date differs from quote"
        elif name == "patient.ahv_number" and value.replace(".", "") not in re.sub(
            r"\D", "", text
        ):
            reason = "AHV number not in message"
        elif name in seen:
            reason = "duplicate field"
        if reason:
            if value is not None:
                s.dropped.append(
                    {
                        "field": name,
                        "value": raw_value,
                        "quote": item.get("quote"),
                        "reason": reason,
                    }
                )
            continue
        seen.add(name)
        s.extracted.append(
            {"field": name, "value": value, "quote": span_text, "quote_status": status}
        )
    return s


def _allowed_fields() -> list[str]:
    from .prompt import extractable_fields

    return extractable_fields()
