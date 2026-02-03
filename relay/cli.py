from __future__ import annotations

from relay.internal.config.settings import Settings
from relay.internal.server.app import build_app
from relay.internal.server.http_server import run_server


def main() -> None:
    settings = Settings.from_env()
    app = build_app(settings)
    run_server(settings, app)
