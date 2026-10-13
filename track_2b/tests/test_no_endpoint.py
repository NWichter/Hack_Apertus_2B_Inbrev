from fastapi.testclient import TestClient

from inbrev import web
from inbrev.config import REPO_DATA

STORED = REPO_DATA / "demo" / "seed-predictions.jsonl"


def _app(monkeypatch, tmp_path, stored: bool) -> TestClient:
    monkeypatch.setattr(web.cfg, "llm_base_url", "")
    monkeypatch.setattr(web.cfg, "audit_log", tmp_path / "audit.jsonl")
    if stored:
        monkeypatch.setenv("INBREV_PRECOMPUTED", str(STORED))
    else:
        monkeypatch.delenv("INBREV_PRECOMPUTED", raising=False)
    web.inbox.clear()
    return TestClient(web.app)


def test_health_says_no_endpoint(monkeypatch, tmp_path):
    h = _app(monkeypatch, tmp_path, True).get("/v1/health").json()
    assert h["endpoint_configured"] is False
    assert h["endpoint_local"] is False


def test_sort_without_endpoint_uses_stored_results_and_explains(monkeypatch, tmp_path):
    c = _app(monkeypatch, tmp_path, True)
    c.post("/v1/inbox/load/seed")
    r = c.post("/v1/inbox/sort").json()
    assert r["queued"] == 0 and r["stored"] == 12 and r["not_sorted"] == 0
    for var in ("LLM_BASE_URL", "LLM_API_KEY", "LLM_NAME"):
        assert var in r["message"]
    items = c.get("/v1/inbox").json()["items"]
    assert all(i["stored"] and i["status"] == "done" for i in items)


def test_sort_without_endpoint_and_without_stored_results(monkeypatch, tmp_path):
    c = _app(monkeypatch, tmp_path, False)
    c.post("/v1/inbox/load/seed")
    r = c.post("/v1/inbox/sort").json()
    assert r["stored"] == 0 and r["not_sorted"] == 12
    assert "LLM_BASE_URL" in r["message"]
    assert all(i["status"] == "pending" for i in c.get("/v1/inbox").json()["items"])


def test_triage_without_endpoint_is_503_with_explanation(monkeypatch, tmp_path):
    c = _app(monkeypatch, tmp_path, True)
    r = c.post(
        "/v1/triage", json={"subject": "Termin", "body": "Bitte Termin verschieben."}
    )
    assert r.status_code == 503 and "LLM_API_KEY" in r.json()["detail"]
