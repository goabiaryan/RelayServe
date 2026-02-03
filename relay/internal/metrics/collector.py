from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class RequestMetrics:
    ttft_ms: float
    tokens: int
    device: str
    queue_ms: float
    batch_size: int
    backend: str


class MetricsCollector:
    def __init__(self, max_items: int = 1000) -> None:
        self._items: List[RequestMetrics] = []
        self._max_items = max_items

    def record(self, metrics: RequestMetrics) -> None:
        self._items.append(metrics)
        if len(self._items) > self._max_items:
            self._items = self._items[-self._max_items :]

    def snapshot(self) -> List[RequestMetrics]:
        return list(self._items)

    def report(self) -> Dict[str, object]:
        if not self._items:
            return {"count": 0, "avg_ttft_ms": 0.0, "avg_queue_ms": 0.0, "by_device": {}}

        total_ttft = sum(item.ttft_ms for item in self._items)
        total_queue = sum(item.queue_ms for item in self._items)
        by_device: Dict[str, Dict[str, float]] = {}
        for item in self._items:
            bucket = by_device.setdefault(
                item.device,
                {"count": 0, "avg_ttft_ms": 0.0, "avg_queue_ms": 0.0},
            )
            bucket["count"] += 1
            bucket["avg_ttft_ms"] += item.ttft_ms
            bucket["avg_queue_ms"] += item.queue_ms

        for bucket in by_device.values():
            count = max(bucket["count"], 1)
            bucket["avg_ttft_ms"] /= count
            bucket["avg_queue_ms"] /= count

        count = len(self._items)
        return {
            "count": count,
            "avg_ttft_ms": total_ttft / count,
            "avg_queue_ms": total_queue / count,
            "by_device": by_device,
        }
