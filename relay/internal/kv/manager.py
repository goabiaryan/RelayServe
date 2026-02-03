from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class KVCacheStats:
    cached_tokens: int = 0
    resident_bytes: int = 0
    handoffs: int = 0
    offloads: int = 0


class KVCacheManager:
    def __init__(self) -> None:
        self._stats = KVCacheStats()
        self._prefix_cache: Dict[str, int] = {}

    def stats(self) -> KVCacheStats:
        return self._stats

    def seed_prefix(self, request_id: str, tokens: int) -> None:
        self._prefix_cache[request_id] = tokens
        self._stats.cached_tokens += tokens

    def handoff(self, request_id: str, from_device: str, to_device: str) -> None:
        if request_id in self._prefix_cache:
            self._stats.handoffs += 1
            self._stats.offloads += 1

    def drop(self, request_id: str) -> None:
        tokens = self._prefix_cache.pop(request_id, 0)
        self._stats.cached_tokens = max(0, self._stats.cached_tokens - tokens)
