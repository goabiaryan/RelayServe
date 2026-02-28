from __future__ import annotations

import os
import sys

# Ensure RelayServe root is on path so router and backends can be imported
def _relay_serve_root() -> str:
    root = os.environ.get("RELAYSERVE_ROOT")
    if root:
        return os.path.abspath(root)
    # When run from source, __file__ is RelayServe/relayserve/cli.py
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> None:
    root = _relay_serve_root()
    if root not in sys.path:
        sys.path.insert(0, root)

    from relayserve.internal.config.settings import Settings
    from relayserve.internal.server.app import build_app
    from relayserve.internal.server.http_server import run_server

    settings = Settings.from_env()
    app = build_app(settings)
    run_server(settings, app)
