import json

from fastapi.testclient import TestClient

from inbrev import evaluate, web
from inbrev.baselines import BASELINES
from inbrev.config import REPO_DATA
from inbrev.llm import Completion
from inbrev.runner import read_jsonl

SEED = read_jsonl(REPO_DATA / "seed" / "messages.seed.jsonl")


class FakeClient:
    model = "fake-apertus"

    async def chat(self, messages, **kw):
        out = {
            "language": "de",
            "route_quote": None,
            "route": "appointment",
            "ambiguous": False,
            "safety_quote": None,
            "safety_flag": False,
            "deadline_quote": None,
            "deadline_date": None,
            "deadline": "none",
            "extracted": [],
        }
        return Completion(
            contents=[json.dumps(out)] * kw.get("n", 1),
            finish_reasons=["stop"] * kw.get("n", 1),
        )


def test_web_flow(monkeypatch, tmp_path):
    monkeypatch.setattr(web, "_client", FakeClient())
    monkeypatch.setattr(web.cfg, "audit_log", tmp_path / "audit.jsonl")
    c = TestClient(web.app)
    assert c.get("/v1/health").json()["model"]
    assert c.post("/v1/inbox/load/seed").json()["loaded"] == len(SEED)
    r = c.post(
        "/v1/triage",
        json={
            "subject": "Termin",
            "body": "Ich möchte den Termin am Donnerstag verschieben.",
        },
    ).json()
    assert r["route"] == "appointment"
    assert r["abstain"]  # no route quote -> a person decides
    up = c.post(
        "/v1/upload",
        files={"file": ("note.txt", "Bitte Rezept für Metformin".encode())},
    ).json()
    assert up["status"] == "done"
    assert (tmp_path / "audit.jsonl").read_text(encoding="utf-8").count("\n") == 2
    assert c.get("/").status_code == 200


def test_baselines_and_score_on_seed():
    for name, fn in BASELINES.items():
        if name == "tfidf_logreg":
            continue
        pred = fn(SEED)
        s = evaluate.score(SEED, pred)
        assert 0 <= s["route_accuracy"] <= 1, name
    perfect = [
        {
            **g["label"],
            "message_id": g["message_id"],
            "confidence": 1.0,
            "patient": g["label"].get("patient") or {},
            "fields": g["label"].get("fields") or {},
        }
        for g in SEED
    ]
    s = evaluate.score(SEED, perfect)
    assert (
        s["route_accuracy"] == 1
        and s["safety"]["recall"] == 1
        and s["fields"]["ALL"]["f1"] == 1
    )
