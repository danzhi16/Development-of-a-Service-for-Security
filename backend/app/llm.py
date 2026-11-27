import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

import httpx

RETRY_STATUSES = (429, 502, 503)
MAX_ATTEMPTS = 5
# Generation may take minutes, but an unreachable server should fail the job quickly.
CONNECT_TIMEOUT_SECONDS = 10


class LLMError(Exception):
    pass


@dataclass
class Completion:
    text: str
    finish_reason: str | None
    usage: dict | None


class LLMClient:
    """Client of an OpenAI-compatible chat completions API (vLLM, Ollama)."""

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        timeout: float = 180,
        transport: httpx.AsyncBaseTransport | None = None,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ):
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        timeouts = httpx.Timeout(timeout, connect=CONNECT_TIMEOUT_SECONDS)
        self._http = httpx.AsyncClient(
            base_url=base_url, headers=headers, timeout=timeouts, transport=transport
        )
        self._sleep = sleep

    async def close(self) -> None:
        await self._http.aclose()

    async def complete(
        self, model: str, system: str, prompt: str,
        temperature: float, max_tokens: int, seed: int | None,
    ) -> Completion:
        body = {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        }
        if seed is not None:
            body["seed"] = seed
        response = await self._post(body)
        try:
            data = response.json()
            choice = data["choices"][0]
            # PostgreSQL text cannot hold NUL; storing it would requeue the job forever.
            text = (choice["message"]["content"] or "").replace("\x00", "")
        except (ValueError, KeyError, IndexError, TypeError) as error:
            raise LLMError(f"unexpected reply: {response.text[:300]}") from error
        return Completion(text, choice.get("finish_reason"), data.get("usage"))

    # Only rate limits and gateway errors are retried, as in the pilot script.
    async def _post(self, body: dict) -> httpx.Response:
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response = await self._http.post("chat/completions", json=body)
            except httpx.ConnectTimeout as error:
                raise LLMError("LLM server unreachable: connect timeout") from error
            except httpx.TimeoutException as error:
                raise LLMError("LLM server timeout") from error
            except httpx.HTTPError as error:
                raise LLMError(f"LLM server unreachable: {error!r}") from error
            if response.status_code in RETRY_STATUSES and attempt < MAX_ATTEMPTS:
                await self._sleep(20 * attempt)
                continue
            if response.is_error:
                raise LLMError(f"HTTP {response.status_code}: {response.text[:300]}")
            return response
        raise AssertionError("unreachable")
