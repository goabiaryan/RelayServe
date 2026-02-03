from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from typing import Callable, Optional
from urllib.parse import urlparse

from relay.internal.config.settings import Settings
from relay.internal.server.app import RelayApp


class RelayHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, app: RelayApp, **kwargs) -> None:
        self._app = app
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/healthz":
            self._send_json(200, {"status": "ok"})
            return
        if path == "/v1/models":
            self._send_json(
                200,
                {"data": [{"id": self._app.settings.model_id, "object": "model"}]},
            )
            return
        if path == "/metrics":
            self._send_json(200, self._app.metrics_report())
            return
        if path == "/debug/shard":
            self._send_json(200, self._app.metrics_report().get("shard_plan", {}))
            return
        self._send_json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path not in ("/v1/chat/completions", "/v1/chat/pretty"):
            self._send_json(404, {"error": "not_found"})
            return

        payload = self._read_json()
        if payload is None:
            self._send_json(400, {"error": "invalid_json"})
            return

        prompt = _extract_prompt(payload)
        if not prompt:
            self._send_json(400, {"error": "missing_prompt"})
            return

        reply_data = self._app.handle_chat(prompt)
        if path == "/v1/chat/pretty" or _prefer_pretty(self, payload):
            self._send_text(200, _format_pretty_text(reply_data))
            return

        response = _format_chat_response(self._app.settings.model_id, prompt, reply_data)
        self._send_json(200, response)

    def log_message(self, format: str, *args) -> None:
        return

    def _read_json(self) -> Optional[dict]:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0:
            return None
        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            return None

    def _send_json(self, status: int, payload: dict) -> None:
        if self._app.settings.pretty_json:
            data = json.dumps(payload, indent=2).encode("utf-8")
        else:
            data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_text(self, status: int, payload: str) -> None:
        data = payload.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def run_server(settings: Settings, app: RelayApp) -> None:
    handler_factory = _make_handler(app)
    server = ThreadingHTTPServer(("", settings.port), handler_factory)
    pretty_default = "pretty" if settings.pretty_default else "json"
    print(
        "Relay starting\n"
        f"- Listening: :{settings.port}\n"
        f"- Model: {settings.model_id}\n"
        f"- Response default: {pretty_default}\n"
        f"- Backends: {', '.join(settings.backends) if settings.backends else 'none'}"
    )
    server.serve_forever()


def _make_handler(app: RelayApp) -> Callable[..., RelayHandler]:
    def handler(*args, **kwargs):
        return RelayHandler(*args, app=app, **kwargs)

    return handler


def _extract_prompt(payload: dict) -> str:
    messages = payload.get("messages", [])
    if not isinstance(messages, list):
        return ""
    for message in reversed(messages):
        if isinstance(message, dict) and message.get("role") == "user":
            return str(message.get("content", "")).strip()
    return ""


def _format_chat_response(model_id: str, prompt: str, reply_data: dict) -> dict:
    reply = str(reply_data.get("reply", "")).strip()
    meta = reply_data.get("meta", {})
    prompt_tokens = len(prompt.split())
    completion_tokens = len(reply.split())
    return {
        "id": "relay-chat-1",
        "object": "chat.completion",
        "model": model_id,
        "relay": meta,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": reply},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }


def _format_pretty_text(reply_data: dict) -> str:
    reply = str(reply_data.get("reply", "")).strip()
    meta = reply_data.get("meta", {})
    device = meta.get("device", "unknown")
    backend = meta.get("backend", "unknown")
    queue_ms = meta.get("queue_ms", 0.0)
    ttft_ms = meta.get("ttft_ms", 0.0)
    batch_size = meta.get("batch_size", 1)

    return (
        "\033[1;36mRelay Response\033[0m\n"
        f"\033[1;32mReply:\033[0m {reply}\n"
        f"\033[1;34mDevice:\033[0m {device}\n"
        f"\033[1;35mBackend:\033[0m {backend}\n"
        f"\033[1;33mQueue:\033[0m {queue_ms:.2f} ms | "
        f"\033[1;33mTTFT:\033[0m {ttft_ms:.2f} ms | "
        f"\033[1;33mBatch:\033[0m {batch_size}\n"
    )


def _prefer_pretty(handler: RelayHandler, payload: dict) -> bool:
    if not handler._app.settings.pretty_default:
        return False
    accept = (handler.headers.get("Accept") or "").lower()
    if "application/json" in accept:
        return False
    if payload.get("format") == "json":
        return False
    return True
