from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from relayserve.internal.device.registry import Device, DeviceRegistry


class RequestPhase(str, Enum):
    PREFILL = "prefill"
    DECODE = "decode"


@dataclass(frozen=True)
class ScheduleDecision:
    device: Device
    phase: RequestPhase


class Scheduler:
    def __init__(self, registry: DeviceRegistry) -> None:
        self._registry = registry

    def classify(self, prompt: str) -> RequestPhase:
        return RequestPhase.PREFILL

    def pick_device(self, prompt: str) -> Optional[ScheduleDecision]:
        device = self._registry.best_device()
        if device is None:
            return None
        return ScheduleDecision(device=device, phase=self.classify(prompt))
