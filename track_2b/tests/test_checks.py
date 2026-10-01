import json
from datetime import date

from jsonschema import Draft202012Validator

from inbrev.config import REPO_DATA
from inbrev.extract import (
    ahv_check_digit_valid,
    ahv_numbers,
    deadline_from_date,
    find_quote,
    parse_date,
)
from inbrev.pipeline import Options, assemble
from inbrev.safety import lexical_flag
from inbrev.verify import check_sample

SCHEMA = json.loads(
    (REPO_DATA / "schema" / "triage_result.schema.json").read_text(encoding="utf-8")
)
TEXT = "KOSTENGUTSPRACHE – RÜCKFRAGE\nVersicherte Person: Anna Meier, 22.08.1979, AHV 756.1234.9876.14\nWir benötigen bis 08.10.2026 die ärztliche Verordnung."
MSG = {
    "message_id": "t-1",
    "subject": TEXT.split("\n", 1)[0],
    "body": TEXT.split("\n", 1)[1],
    "received_at": "2026-10-01T08:00",
}


def sample(**over) -> str:
    base = {
        "language": "de",
        "route_quote": "KOSTENGUTSPRACHE – RÜCKFRAGE",
        "route": "insurer",
        "ambiguous": False,
        "safety_quote": None,
        "safety_flag": False,
        "deadline_quote": "bis 08.10.2026",
        "deadline_date": "2026-10-08",
        "deadline": "this_week",
        "extracted": [
            {"field": "patient.name", "value": "Anna Meier", "quote": "Anna Meier"},
            {
                "field": "patient.insurance_number",
                "value": "756.1234.9876.14",
                "quote": "AHV 756.1234.9876.14",
            },
            {
                "field": "patient.birth_date",
                "value": "1979-08-22",
                "quote": "22.08.1979",
            },
        ],
    }
    base.update(over)
    return json.dumps(base, ensure_ascii=False)


def test_find_quote_levels():
    assert find_quote("Anna Meier", TEXT)[0] == "exact"
    assert find_quote("anna   meier", TEXT)[0] == "normalized"
    status, span = find_quote("KOSTENGUTSPRACHE – RúCKFRAGE", TEXT)
    assert (
        status == "fuzzy" and TEXT[span[0] : span[1]] == "KOSTENGUTSPRACHE – RÜCKFRAGE"
    )
    assert find_quote("&quot;Anna Meier&quot;", TEXT)[0] == "exact"
    assert find_quote("Hans Muster wohnt in Bern", TEXT)[0] == "missing"
    assert find_quote("null", TEXT)[0] == "missing"


def test_ahv_and_dates():
    assert ahv_numbers(TEXT) == ["756.1234.9876.14"]
    assert not ahv_check_digit_valid("756.1234.9876.14")
    assert ahv_check_digit_valid("756.9217.0769.85")
    assert parse_date("22.08.1979") == date(1979, 8, 22)
    received = date(2026, 10, 1)
    assert deadline_from_date(date(2026, 10, 2), received) == "today"
    assert deadline_from_date(date(2026, 10, 8), received) == "this_week"
    assert deadline_from_date(date(2026, 10, 9), received) == "none"


def test_check_sample_moves_ahv_and_computes_deadline():
    s = check_sample(sample(), "stop", TEXT, date(2026, 10, 1))
    assert s.ok and s.route == "insurer" and s.deadline == "this_week"
    fields = {e["field"]: e["value"] for e in s.extracted}
    assert fields["patient.ahv_number"] == "756.1234.9876.14"
    assert "patient.insurance_number" not in fields


def test_deadline_without_evidence_is_none():
    s = check_sample(
        sample(deadline_quote=None, deadline_date=None, deadline="today"),
        "stop",
        TEXT,
        date(2026, 10, 1),
    )
    assert s.deadline == "none"


def test_drops_unverifiable_values():
    s = check_sample(
        sample(
            extracted=[
                {
                    "field": "patient.name",
                    "value": "Hans Muster",
                    "quote": "Hans Muster",
                },
                {
                    "field": "patient.birth_date",
                    "value": "1980-01-01",
                    "quote": "22.08.1979",
                },
                {"field": "fields.topic", "value": "null", "quote": "null"},
            ]
        ),
        "stop",
        TEXT,
        date(2026, 10, 1),
    )
    assert s.extracted == []
    assert {d["reason"] for d in s.dropped} == {
        "quote not in message",
        "date differs from quote",
    }


def test_truncated_and_broken_samples():
    assert (
        check_sample(
            '{"route": "insurer", "safety', "length", TEXT, date(2026, 10, 1)
        ).error
        == "truncated"
    )
    assert check_sample("not json", "stop", TEXT, date(2026, 10, 1)).error.startswith(
        "json"
    )
    assert (
        check_sample(sample(route="urgent"), "stop", TEXT, date(2026, 10, 1)).error
        == "route not in taxonomy"
    )


def test_assemble_vote_and_schema():
    raws = [sample(), sample(), sample(route="billing")]
    out = assemble(
        MSG, raws, ["stop"] * 3, Options(abstain_below=0.6), {"model": "fake"}
    )
    r = out["result"]
    assert r["route"] == "insurer" and r["assignee"] == "admin" and not r["abstain"]
    assert r["confidence"] == round(2 / 3, 3)
    assert r["patient"]["ahv_number"] == "756.1234.9876.14"
    errors = list(Draft202012Validator(SCHEMA).iter_errors(r))
    assert not errors, errors
    for e in r["evidence"]:
        assert e["quote"] in TEXT


def test_assemble_abstains_on_disagreement_and_no_output():
    raws = [sample(), sample(route="billing"), sample(route="other")]
    assert assemble(MSG, raws, ["stop"] * 3, Options(), {})["result"]["abstain"]
    empty = assemble(MSG, [], [], Options(), {"error": "down"})["result"]
    assert empty["abstain"] and empty["safety_flag"]


def test_safety_or_lexical_net():
    msg = {
        **MSG,
        "body": MSG["body"] + "\nPS: seit heute Morgen habe ich Druck auf der Brust.",
    }
    out = assemble(msg, [sample()] * 3, ["stop"] * 3, Options(), {})["result"]
    assert (
        out["safety_flag"]
        and out["deadline"] == "today"
        and out["assignee"] == "doctor"
    )
    assert out["reply_draft"] is None
    llm_only = assemble(
        msg, [sample()] * 3, ["stop"] * 3, Options(safety_mode="llm"), {}
    )["result"]
    assert not llm_only["safety_flag"]


def test_lexicon_examples():
    assert lexical_flag("j'ai du mal à respirer depuis ce matin")
    assert lexical_flag("dolore al petto da stamattina")
    assert not lexical_flag("Bitte Termin verschieben auf Dienstag")


def test_thinking_prefix_and_redaction():
    from inbrev.llm import redact

    raw = "<|inner_prefix|>Let me think.<|inner_suffix|>" + sample()
    assert check_sample(raw, "stop", TEXT, date(2026, 10, 1)).route == "insurer"
    assert "abc123" not in redact("Rate limit exceeded for api_key: abc123. Retry later")
