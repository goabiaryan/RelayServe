from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    port: int
    model_id: str
    backends: list[str]
    batch_size: int
    batch_wait_ms: int
    metrics_max_items: int
    total_layers: int
    pretty_json: bool
    pretty_default: bool

    @staticmethod
    def from_env() -> "Settings":
        port = int(os.getenv("RELAY_PORT", "8080"))
        model_id = os.getenv("RELAY_MODEL_ID", "relay-gguf")
        backends_raw = os.getenv("RELAY_BACKENDS", "").strip()
        backends = [item.strip() for item in backends_raw.split(",") if item.strip()]
        batch_size = int(os.getenv("RELAY_BATCH_SIZE", "4"))
        batch_wait_ms = int(os.getenv("RELAY_BATCH_WAIT_MS", "10"))
        metrics_max_items = int(os.getenv("RELAY_METRICS_MAX_ITEMS", "1000"))
        total_layers = int(os.getenv("RELAY_TOTAL_LAYERS", "32"))
        pretty_json = os.getenv("RELAY_PRETTY_JSON", "0") == "1"
        pretty_default = os.getenv("RELAY_PRETTY_DEFAULT", "1") == "1"
        return Settings(
            port=port,
            model_id=model_id,
            backends=backends,
            batch_size=batch_size,
            batch_wait_ms=batch_wait_ms,
            metrics_max_items=metrics_max_items,
            total_layers=total_layers,
            pretty_json=pretty_json,
            pretty_default=pretty_default,
        )
