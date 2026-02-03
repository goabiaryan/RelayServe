from __future__ import annotations

import json
from typing import Optional
from urllib import request

from relay.internal.device.registry import Device


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
