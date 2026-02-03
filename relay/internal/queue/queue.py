from __future__ import annotations

from collections import deque
from typing import Deque, Optional


class RequestQueue:
    def __init__(self) -> None:
        self._items: Deque[dict] = deque()

    def enqueue(self, item: dict) -> None:
        self._items.append(item)

    def dequeue(self) -> Optional[dict]:
        if not self._items:
            return None
        return self._items.popleft()

    def __len__(self) -> int:
        return len(self._items)
