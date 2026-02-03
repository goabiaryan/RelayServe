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

Defaults:
- HTTP server: `:8080`
- Endpoints:
  - `GET /healthz`
  - `GET /v1/models`
  - `POST /v1/chat/completions`
  - `GET /metrics`
  - `GET /debug/shard`
  - `POST /v1/chat/pretty` (colorized text response)
- Backends: set `RELAYSERVE_BACKENDS` to comma-separated llama.cpp servers

## Environment

- `RELAYSERVE_PORT` (default `8080`)
- `RELAYSERVE_MODEL_ID` (default `relay-gguf`)
- `RELAYSERVE_BACKENDS` (comma-separated, e.g. `http://localhost:8081,http://localhost:8082`)
- `RELAYSERVE_BATCH_SIZE` (default `4`)
- `RELAYSERVE_BATCH_WAIT_MS` (default `10`)
- `RELAYSERVE_METRICS_MAX_ITEMS` (default `1000`)
- `RELAYSERVE_TOTAL_LAYERS` (default `32`)
- `RELAYSERVE_PRETTY_JSON` (set `1` for readable JSON responses)
- `RELAYSERVE_PRETTY_DEFAULT` (default `1`, set `0` for JSON by default)

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


