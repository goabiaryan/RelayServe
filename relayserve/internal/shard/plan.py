from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from relayserve.internal.device.registry import Device


@dataclass(frozen=True)
class ShardPlan:
    placements: List[str]
    layer_ranges: List[Tuple[int, int]]


class ShardPlanner:
    def plan(self, devices: list[Device], total_layers: int) -> ShardPlan:
        placements = [f"{device.backend}:{device.name}" for device in devices]
        if not devices or total_layers <= 0:
            return ShardPlan(placements=placements, layer_ranges=[])

        strengths = [max(device.strength_score, 0.1) for device in devices]
        total_strength = sum(strengths)
        allocations = [max(1, int(total_layers * (s / total_strength))) for s in strengths]

        while sum(allocations) > total_layers:
            idx = allocations.index(max(allocations))
            allocations[idx] = max(1, allocations[idx] - 1)
        while sum(allocations) < total_layers:
            idx = allocations.index(max(allocations))
            allocations[idx] += 1

        layer_ranges: List[Tuple[int, int]] = []
        cursor = 0
        for allocation in allocations:
            start = cursor
            end = min(total_layers - 1, start + allocation - 1)
            layer_ranges.append((start, end))
            cursor = end + 1

        return ShardPlan(placements=placements, layer_ranges=layer_ranges)
