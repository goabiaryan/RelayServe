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


