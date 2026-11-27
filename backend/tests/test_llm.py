import asyncio
import json

import httpx
import pytest

from app.llm import MAX_ATTEMPTS, LLMClient, LLMError

REPLY = {"choices": [{"message": {"content": "code"}, "finish_reason": "stop"}], "usage": {"total_tokens": 3}}


def complete(handler, seed=None):
    delays = []

    async def scenario():
        async def sleep(seconds):
            delays.append(seconds)

        client = LLMClient("http://llm/v1", "key", transport=httpx.MockTransport(handler), sleep=sleep)
        try:
            return await client.complete("m", "sys", "task", 0, 100, seed)
        finally:
            await client.close()

    return asyncio.run(scenario()), delays


def test_request_carries_parameters_and_reply_is_parsed():
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json=REPLY)

    completion, _ = complete(handler, seed=7)

    body = json.loads(seen[0].content)
    assert str(seen[0].url) == "http://llm/v1/chat/completions"
    assert seen[0].headers["authorization"] == "Bearer key"
    assert (body["model"], body["seed"], body["max_tokens"]) == ("m", 7, 100)
    assert [message["content"] for message in body["messages"]] == ["sys", "task"]
    assert (completion.text, completion.finish_reason) == ("code", "stop")


def test_rate_limit_is_retried():
    replies = [httpx.Response(429), httpx.Response(200, json=REPLY)]

    completion, delays = complete(lambda _: replies.pop(0))

    assert completion.text == "code"
    assert delays == [20]


def test_retries_are_limited():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(503, text="busy")

    with pytest.raises(LLMError, match="HTTP 503"):
        complete(handler)
    assert len(calls) == MAX_ATTEMPTS


@pytest.mark.parametrize(
    ("response", "message"),
    [(httpx.Response(404, text="no model"), "HTTP 404"), (httpx.Response(200, json={}), "unexpected reply")],
)
def test_bad_replies_raise(response, message):
    with pytest.raises(LLMError, match=message):
        complete(lambda _: response)


def test_timeout_raises():
    def handler(request):
        raise httpx.ReadTimeout("slow", request=request)

    with pytest.raises(LLMError, match="timeout"):
        complete(handler)
