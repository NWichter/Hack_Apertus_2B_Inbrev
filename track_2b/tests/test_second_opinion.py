import asyncio
import json

from inbrev import pipeline
from inbrev.llm import Completion
from inbrev.pipeline import Options, triage

# Keyword rules see "Rechnung" (billing); the first model says insurer -> low confidence.
MSG = {
    "message_id": "so-1",
    "subject": "Ihre Rechnung Nr. 26-1180",
    "body": "Auf Ihrer Rechnung Nr. 26-1180 ist eine Position doppelt verrechnet. Bitte korrigieren.",
    "received_at": "2026-10-05T08:00",
}


def answer(route: str, quote: str = "Bitte korrigieren") -> str:
    return json.dumps(
        {
            "language": "de",
            "route_quote": quote,
            "route": route,
            "ambiguous": False,
            "safety_quote": None,
            "safety_flag": False,
            "deadline_quote": None,
            "deadline_date": None,
            "deadline": "none",
            "extracted": [],
        }
    )


class Fake:
    def __init__(self, model: str, route: str):
        self.model, self.route, self.calls = model, route, 0
        self.cfg = None

    async def chat(self, messages, n=1, **kw):
        self.calls += 1
        return Completion(
            contents=[answer(self.route)] * n, finish_reasons=["stop"] * n
        )


def run(first_route: str, second_route: str | None, model: str = "apertus-v1.5-70b"):
    first = Fake("apertus-v1.5-8b", first_route)
    second = Fake(model, second_route or first_route)
    pipeline._second_clients.clear()
    if second_route is not None:
        pipeline._second_clients[model] = second
    opts = Options(second_opinion_model=model if second_route is not None else "")
    out = asyncio.run(triage(MSG, first, opts))
    return out, second.calls


def test_off_by_default():
    assert Options().second_opinion_model == ""
    out, calls = run("insurer", None)
    assert calls == 0 and "second_opinion" not in out["trace"]
    assert not out["result"]["abstain"]


def test_disagreement_goes_to_a_person():
    out, calls = run("insurer", "other")
    assert calls == 1
    assert out["result"]["abstain"] and out["result"]["route"] == "insurer"
    assert out["trace"]["second_opinion"]["verdict"] == "disagrees"
    assert any("second opinion" in r for r in out["trace"]["abstain_reasons"])


def test_agreement_stays_automatic():
    out, calls = run("insurer", "insurer")
    assert calls == 1 and not out["result"]["abstain"]
    assert out["trace"]["second_opinion"]["verdict"] == "agrees"


def test_not_asked_when_rules_agree():
    out, calls = run("billing", "other")
    assert calls == 0 and not out["result"]["abstain"]


def test_replay_reproduces_live_result():
    out, _ = run("insurer", "other")
    row = {"result": out["result"], "trace": out["trace"]}
    again = pipeline.replay(row, MSG, Options(second_opinion_model="apertus-v1.5-70b"))
    assert again["result"]["abstain"] == out["result"]["abstain"]
    assert again["trace"]["second_opinion"]["verdict"] == "disagrees"
