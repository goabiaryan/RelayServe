from __future__ import annotations

from concurrent.futures import Future
from dataclasses import dataclass
from queue import Empty, Queue
import uuid
import threading
import time

from relayserve.internal.config.settings import Settings
from relayserve.internal.device.registry import DeviceRegistry
from relayserve.internal.kv.manager import KVCacheManager
from relayserve.internal.metrics.collector import MetricsCollector, RequestMetrics
from relayserve.internal.profile.probe import probe_devices
from relayserve.internal.runner.runner import LlamaServerClient, Runner
from relayserve.internal.scheduler.scheduler import Scheduler
from relayserve.internal.shard.plan import ShardPlanner


@dataclass
class RequestItem:
    prompt: str
    future: Future[dict]
    enqueue_time: float


class RelayApp:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.registry = DeviceRegistry()
        self.registry.add_all(probe_devices())
        self.scheduler = Scheduler(self.registry)
        self.runner = Runner()
        self.llama_client = LlamaServerClient(settings.backends)
        self.metrics = MetricsCollector(settings.metrics_max_items)
        self.shard_planner = ShardPlanner()
        self.kv_cache = KVCacheManager()
        self._queue: Queue[RequestItem] = Queue()
        self._batch_size = max(1, settings.batch_size)
        self._batch_wait_s = max(0.0, settings.batch_wait_ms / 1000.0)
        self._worker = threading.Thread(target=self._run_loop, daemon=True)
        self._worker.start()

    def handle_chat(self, prompt: str) -> dict:
        future: Future[dict] = Future()
        self._queue.put(RequestItem(prompt=prompt, future=future, enqueue_time=time.perf_counter()))
        return future.result()

    def metrics_report(self) -> dict:
        return {
            "stats": self.metrics.report(),
            "queue_depth": self._queue.qsize(),
            "kv": self._kv_report(),
            "shard_plan": self._current_shard_plan(),
        }

    def _run_loop(self) -> None:
        while True:
            item = self._queue.get()
            batch = [item]
            deadline = time.perf_counter() + self._batch_wait_s
            while len(batch) < self._batch_size:
                timeout = max(0.0, deadline - time.perf_counter())
                if timeout == 0.0:
                    break
                try:
                    batch.append(self._queue.get(timeout=timeout))
                except Empty:
                    break
            self._process_batch(batch)

    def _process_batch(self, batch: list[RequestItem]) -> None:
        batch_size = len(batch)
        for item in batch:
            start = time.perf_counter()
            decision = self.scheduler.pick_device(item.prompt)
            if decision is None:
                reply = "No devices available."
                device_label = "none"
                backend = "none"
            else:
                request_id = uuid.uuid4().hex
                shard_plan = self.shard_planner.plan(self.registry.list(), self.settings.total_layers)
                self._seed_kv_prefix(request_id, item.prompt, shard_plan)
                self._handoff_kv(request_id, shard_plan)
                reply = self.llama_client.chat(item.prompt)
                if not reply:
                    reply = self.runner.run(decision.device, item.prompt)
                    backend = decision.device.backend
                else:
                    backend = "llama.cpp"
                device_label = f"{decision.device.backend}:{decision.device.name}"
                self.kv_cache.drop(request_id)

            elapsed_ms = (time.perf_counter() - start) * 1000.0
            queue_ms = (start - item.enqueue_time) * 1000.0
            self.metrics.record(
                RequestMetrics(
                    ttft_ms=elapsed_ms,
                    tokens=len(reply.split()),
                    device=device_label,
                    queue_ms=queue_ms,
                    batch_size=batch_size,
                    backend=backend,
                )
            )
            item.future.set_result(
                {
                    "reply": reply,
                    "meta": {
                        "device": device_label,
                        "backend": backend,
                        "queue_ms": queue_ms,
                        "ttft_ms": elapsed_ms,
                        "batch_size": batch_size,
                    },
                }
            )

    def _seed_kv_prefix(self, request_id: str, prompt: str, shard_plan) -> None:
        prefix_tokens = max(1, len(prompt.split()))
        if shard_plan.layer_ranges:
            self.kv_cache.seed_prefix(request_id, prefix_tokens)

    def _handoff_kv(self, request_id: str, shard_plan) -> None:
        placements = shard_plan.placements
        for idx in range(1, len(placements)):
            self.kv_cache.handoff(request_id, placements[idx - 1], placements[idx])

    def _kv_report(self) -> dict:
        stats = self.kv_cache.stats()
        return {
            "cached_tokens": stats.cached_tokens,
            "resident_bytes": stats.resident_bytes,
            "handoffs": stats.handoffs,
            "offloads": stats.offloads,
        }

    def _current_shard_plan(self) -> dict:
        plan = self.shard_planner.plan(self.registry.list(), self.settings.total_layers)
        return {
            "placements": plan.placements,
            "layer_ranges": plan.layer_ranges,
        }


def build_app(settings: Settings) -> RelayApp:
    return RelayApp(settings)
