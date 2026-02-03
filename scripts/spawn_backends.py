from __future__ import annotations

import os
import shlex
import subprocess
import sys
from pathlib import Path


def main() -> int:
    llama_server = os.getenv("LLAMA_SERVER_PATH", "").strip()
    model_path = os.getenv("LLAMA_MODEL_PATH", "").strip()
    if not llama_server or not model_path:
        print("Set LLAMA_SERVER_PATH and LLAMA_MODEL_PATH.", file=sys.stderr)
        return 2

    ports = os.getenv("LLAMA_PORTS", "8081").split(",")
    ports = [p.strip() for p in ports if p.strip()]

    extra_args = shlex.split(os.getenv("LLAMA_SERVER_ARGS", ""))
    processes: list[subprocess.Popen] = []

    for port in ports:
        cmd = [
            llama_server,
            "-m",
            model_path,
            "--host",
            "0.0.0.0",
            "--port",
            str(port),
        ] + extra_args
        print("Starting:", " ".join(shlex.quote(part) for part in cmd))
        processes.append(
            subprocess.Popen(
                cmd,
                cwd=str(Path(model_path).parent),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
        )

    print("Backends running. Ctrl+C to stop.")
    try:
        while True:
            for process in processes:
                line = process.stdout.readline() if process.stdout else ""
                if line:
                    print(line.rstrip())
    except KeyboardInterrupt:
        for process in processes:
            process.terminate()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
