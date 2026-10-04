import asyncio
import json

import httpx

from inbrev.config import Settings
from inbrev.llm import LLMClient


def _client(handler) -> LLMClient:
    cfg = Settings()
    cfg.llm_base_url = "http://llm.test/v1"
    cfg.split_samples = "auto"
    c = LLMClient(cfg)
    c._client = httpx.AsyncClient(base_url=cfg.llm_base_url, transport=httpx.MockTransport(handler))
    return c


def test_server_without_n_gets_single_requests():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        calls.append(body)
        if body["n"] > 1:
            return httpx.Response(400, json={"error": {"message": "Field 'n': Value must be between 1 <= value <= 1"}})
        return httpx.Response(200, json={
            "choices": [{"message": {"content": f"s{body['seed']}"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 2},
        })

    c = _client(handler)
    comp = asyncio.run(c.chat([{"role": "user", "content": "x"}], n=3, temperature=0.7))
    assert comp.contents == ["s1000", "s1001", "s1002"]
    assert comp.split and comp.prompt_tokens == 30 and comp.completion_tokens == 6
    assert [b["n"] for b in calls] == [3, 1, 1, 1]
    comp = asyncio.run(c.chat([{"role": "user", "content": "x"}], n=3))
    assert [b["n"] for b in calls[4:]] == [1, 1, 1]


def test_server_with_n_keeps_one_request():
    def handler(request: httpx.Request) -> httpx.Response:
        n = json.loads(request.content)["n"]
        return httpx.Response(200, json={
            "choices": [{"message": {"content": str(i)}, "finish_reason": "stop"} for i in range(n)],
            "usage": {"prompt_tokens": 10, "completion_tokens": 3},
        })

    comp = asyncio.run(_client(handler).chat([{"role": "user", "content": "x"}], n=3))
    assert comp.contents == ["0", "1", "2"] and not comp.split
