from __future__ import annotations

from relayserve.internal.config.settings import Settings
from relayserve.internal.server.app import build_app
from relayserve.internal.server.http_server import run_server


def main() -> None:
    settings = Settings.from_env()
    app = build_app(settings)
    run_server(settings, app)
