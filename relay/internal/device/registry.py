from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional


@dataclass(frozen=True)
class Device:
    name: str
    backend: str
    vram_gb: float
    tflops: float
    bandwidth_gbps: float

    @property
    def strength_score(self) -> float:
        return (self.tflops * 0.6) + (self.bandwidth_gbps * 0.3) + (self.vram_gb * 0.1)


class DeviceRegistry:
    def __init__(self) -> None:
        self._devices: List[Device] = []

    def add_all(self, devices: Iterable[Device]) -> None:
        for device in devices:
            self._devices.append(device)

    def list(self) -> List[Device]:
        return list(self._devices)

    def best_device(self) -> Optional[Device]:
        if not self._devices:
            return None
        return max(self._devices, key=lambda d: d.strength_score)
