from __future__ import annotations

import json
from typing import Iterator, Optional
from urllib import request

from relayserve.internal.device.registry import Device


class Runner:
    def run(self, device: Device, prompt: str) -> str:
        return f"Echo: {prompt}"


class LlamaServerClient:
    def __init__(self, endpoints: list[str]) -> None:
        self._endpoints = endpoints
        self._index = 0

    def has_backends(self) -> bool:
        return bool(self._endpoints)

    def next_endpoint(self) -> Optional[str]:
        if not self._endpoints:
            return None
        endpoint = self._endpoints[self._index % len(self._endpoints)]
        self._index = (self._index + 1) % len(self._endpoints)
        return endpoint

    def chat(self, prompt: str) -> Optional[str]:
        endpoint = self.next_endpoint()
        if endpoint is None:
            return None
        url = endpoint.rstrip("/") + "/v1/chat/completions"
        payload = {
            "model": "relay-gguf",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with request.urlopen(req, timeout=60) as resp:
                body = resp.read().decode("utf-8")
            parsed = json.loads(body)
        except Exception:
            return None

        choices = parsed.get("choices", [])
        if not choices:
            return None
        message = choices[0].get("message", {})
        return str(message.get("content", "")).strip()

    def chat_stream(
        self, prompt: str, request_id: str, model_id: str
    ) -> Iterator[dict]:
        """Stream chat completion chunks from backend in OpenAI SSE format."""
        endpoint = self.next_endpoint()
        if endpoint is None:
            return
        url = endpoint.rstrip("/") + "/v1/chat/completions"
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
        }
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            url, data=data, headers={"Content-Type": "application/json"}, method="POST"
        )
        try:
            with request.urlopen(req, timeout=60) as resp:
                content_type = (resp.headers.get("Content-Type") or "").lower()
                body = resp.read().decode("utf-8")

                if "text/event-stream" not in content_type and "application/json" in content_type:
                    # Backend returned non-streaming JSON; emit one chunk then done
                    parsed = json.loads(body)
                    choices = parsed.get("choices", [])
                    if choices:
                        message = choices[0].get("message", {})
                        content = str(message.get("content", "")).strip()
                        yield {
                            "id": request_id,
                            "object": "chat.completion.chunk",
                            "model": model_id,
                            "choices": [
                                {
                                    "index": 0,
                                    "delta": {"role": "assistant", "content": content},
                                    "finish_reason": "stop",
                                }
                            ],
                        }
                    return
                # SSE: parse line by line
                for line in body.splitlines():
                    line = line.strip()
                    if not line.startswith("data: "):
                        continue
                    data_part = line[6:].strip()
                    if data_part == "[DONE]":
                        return
                    try:
                        chunk = json.loads(data_part)
                        chunk["id"] = request_id
                        if "model" not in chunk or not chunk["model"]:
                            chunk["model"] = model_id
                        yield chunk
                    except json.JSONDecodeError:
                        continue
        except Exception:
            raise
