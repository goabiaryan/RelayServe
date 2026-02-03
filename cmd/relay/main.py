from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from relay.internal.config.settings import Settings
from relay.internal.server.app import build_app
from relay.internal.server.http_server import run_server


def main() -> None:
    settings = Settings.from_env()
    app = build_app(settings)
    run_server(settings, app)


if __name__ == "__main__":
    main()
