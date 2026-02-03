# Relay (MVP)

Relay is a minimal LLM inference server that adapts to heterogeneous devices.

## Quick start

```bash
python cmd/relay/main.py
```

Or install locally and run as a CLI:

```bash
pip install -e .
relayserve
```

With uv:

```bash
uv pip install -e .
relayserve
```

Install from PyPI:

```bash
pip install relayserve
relayserve
```

Defaults:
- HTTP server: `:8080`
- Endpoints:
  - `GET /healthz`
  - `GET /v1/models`
  - `POST /v1/chat/completions`
  - `GET /metrics`
  - `GET /debug/shard`
  - `POST /v1/chat/pretty` (colorized text response)
 - Backends: set `RELAY_BACKENDS` to comma-separated llama.cpp servers

## Environment

- `RELAY_PORT` (default `8080`)
- `RELAY_MODEL_ID` (default `relay-gguf`)
- `RELAY_BACKENDS` (comma-separated, e.g. `http://localhost:8081,http://localhost:8082`)
- `RELAY_BATCH_SIZE` (default `4`)
- `RELAY_BATCH_WAIT_MS` (default `10`)
- `RELAY_METRICS_MAX_ITEMS` (default `1000`)
- `RELAY_TOTAL_LAYERS` (default `32`)
- `RELAY_PRETTY_JSON` (set `1` for readable JSON responses)
- `RELAY_PRETTY_DEFAULT` (default `1`, set `0` for JSON by default)

## Spawning llama.cpp backends

```bash
export LLAMA_SERVER_PATH=/path/to/llama.cpp/server
export LLAMA_MODEL_PATH=/path/to/models/phi-3-mini.gguf
export LLAMA_PORTS=8081,8082
python scripts/spawn_backends.py
```

Then run the relay server with:

```bash
export RELAY_BACKENDS=http://localhost:8081,http://localhost:8082
python cmd/relay/main.py
```


