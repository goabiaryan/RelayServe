# RelayServe

[![PyPI version](https://badge.fury.io/py/relayserve.svg)](https://badge.fury.io/py/relayserve)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


RelayServe is a minimal LLM inference server that adapts to heterogeneous devices.

## Quick start

Install from PyPI:

```bash
pip install relayserve
relayserve
```

## Multi-backend (llama.cpp)

```bash
export LLAMA_SERVER_PATH=/path/to/llama.cpp/server
export LLAMA_MODEL_PATH=/path/to/models/phi-3-mini.gguf
export LLAMA_PORTS=8081,8082
python scripts/spawn_backends.py
```

```bash
export RELAYSERVE_BACKENDS=http://localhost:8081,http://localhost:8082
relayserve
``

## Spawning llama.cpp backends

```bash
export LLAMA_SERVER_PATH=/path/to/llama.cpp/server
export LLAMA_MODEL_PATH=/path/to/models/phi-3-mini.gguf
export LLAMA_PORTS=8081,8082
python scripts/spawn_backends.py
```

Then run the RelayServe server with:

```bash
export RELAYSERVE_BACKENDS=http://localhost:8081,http://localhost:8082
relayserve
```

## Streaming and request ID

RelayServe supports **OpenAI-compatible streaming** for `POST /v1/chat/completions`: send `"stream": true` in the request body to receive Server-Sent Events (SSE) until `data: [DONE]`.

**Example (curl, non-streaming):**
```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: my-request-123" \
  -d '{"model":"relay-gguf","messages":[{"role":"user","content":"Hello"}]}'
```

**Example (curl, streaming):**
```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: my-request-456" \
  -d '{"model":"relay-gguf","messages":[{"role":"user","content":"Hello"}],"stream":true}'
```

**Request-ID:** Send `X-Request-ID` or `Request-Id` in the request; the same value is echoed in the response header and in the JSON `id` field (or in each streamed chunk `id`). If omitted, the server generates a UUID.

**Python example:** See `examples/streaming_chat.py`. Run with a live RelayServe backend:
```bash
python examples/streaming_chat.py "Your prompt" "optional-request-id"
```


