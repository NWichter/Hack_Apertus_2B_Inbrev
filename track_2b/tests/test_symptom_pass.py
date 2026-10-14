import json

from inbrev.pipeline import Options, assemble, symptom_votes

MSG = {
    "message_id": "t1",
    "subject": "Rezept Metformin",
    "body": "Bitte ein neues Rezept für Metformin 500 mg. Seit heute habe ich Fieber.",
    "received_at": "2026-10-05T08:00",
}
MAIN = json.dumps(
    {
        "language": "de",
        "route_quote": "Bitte ein neues Rezept für Metformin 500 mg",
        "route": "prescription_request",
        "ambiguous": False,
        "safety_quote": None,
        "safety_flag": False,
        "deadline_quote": None,
        "deadline_date": None,
        "deadline": "none",
        "extracted": [],
    }
)


def sym(flag: bool, quote: str | None) -> str:
    return json.dumps({"symptom_quote": quote, "current_symptom": flag})


def test_symptom_votes_need_verified_quote():
    text = MSG["subject"] + "\n" + MSG["body"]
    assert symptom_votes([sym(True, "Seit heute habe ich Fieber")], text)[0] == 1
    assert symptom_votes([sym(True, "starke Brustschmerzen")], text)[0] == 0
    assert symptom_votes([sym(False, "Seit heute habe ich Fieber")], text)[0] == 0


def test_symptom_pass_raises_flag_and_deadline():
    call = {
        "symptom_raw": [
            sym(True, "Seit heute habe ich Fieber"),
            sym(False, None),
            sym(False, None),
        ]
    }
    off = assemble(MSG, [MAIN] * 3, ["stop"] * 3, Options(), dict(call))["result"]
    on = assemble(
        MSG, [MAIN] * 3, ["stop"] * 3, Options(symptom_check=True), dict(call)
    )["result"]
    assert not off["safety_flag"]
    assert on["safety_flag"] and on["deadline"] == "today"
    assert {"field": "safety_flag", "quote": "Seit heute habe ich Fieber"} in on[
        "evidence"
    ]


def test_rules_gate_abstains_on_disagreement():
    other = MAIN.replace('"prescription_request"', '"billing"')
    res = assemble(MSG, [other] * 3, ["stop"] * 3, Options(rules_gate=True), {})[
        "result"
    ]
    assert res["abstain"]


def test_failed_symptom_pass_sends_message_to_a_person():
    clean = dict(MSG, body="Bitte ein neues Rezept für Metformin 500 mg.")
    ok = assemble(
        clean, [MAIN] * 3, ["stop"] * 3, Options(symptom_check=True),
        {"symptom_raw": [sym(False, None)] * 3},
    )["result"]
    assert not ok["abstain"]
    for call in (
        {"symptom_raw": [], "symptom_error": "HTTP 500"},
        {"symptom_raw": ["not json", ""]},
    ):
        res = assemble(
            clean, [MAIN] * 3, ["stop"] * 3, Options(symptom_check=True), dict(call)
        )
        assert res["result"]["abstain"]
        assert "symptom check failed" in res["trace"]["abstain_reasons"]
