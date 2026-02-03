from __future__ import annotations

import os
import platform
import shutil
import subprocess
from typing import List

from relay.internal.device.registry import Device


def probe_devices() -> list[Device]:
    cpu_name = platform.processor() or platform.machine() or "cpu"
    cpu_cores = os.cpu_count() or 1
    cpu_device = Device(
        name=f"{cpu_name} ({cpu_cores} cores)",
        backend="cpu",
        vram_gb=0.0,
        tflops=max(0.1, cpu_cores * 0.05),
        bandwidth_gbps=10.0,
    )

    devices = [cpu_device]

    devices.extend(_probe_nvidia_smi())
    devices.extend(_probe_macos_system_profiler())

    if os.getenv("RELAY_ENABLE_GPU", "0") == "1":
        devices.append(
            Device(
                name="stub-gpu",
                backend=os.getenv("RELAY_GPU_BACKEND", "cuda"),
                vram_gb=float(os.getenv("RELAY_GPU_VRAM_GB", "12")),
                tflops=float(os.getenv("RELAY_GPU_TFLOPS", "20")),
                bandwidth_gbps=float(os.getenv("RELAY_GPU_BW_GBPS", "300")),
            )
        )

    return devices


def _probe_nvidia_smi() -> List[Device]:
    if shutil.which("nvidia-smi") is None:
        return []

    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            check=False,
            timeout=2,
        )
    except Exception:
        return []

    devices: List[Device] = []
    for line in result.stdout.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 2:
            continue
        name, memory_mb = parts[0], parts[1]
        try:
            vram_gb = float(memory_mb) / 1024.0
        except ValueError:
            vram_gb = 0.0
        devices.append(
            Device(
                name=name,
                backend="cuda",
                vram_gb=vram_gb,
                tflops=float(os.getenv("RELAY_GPU_TFLOPS", "20")),
                bandwidth_gbps=float(os.getenv("RELAY_GPU_BW_GBPS", "300")),
            )
        )
    return devices


def _probe_macos_system_profiler() -> List[Device]:
    if platform.system().lower() != "darwin":
        return []
    if shutil.which("system_profiler") is None:
        return []

    try:
        result = subprocess.run(
            ["system_profiler", "SPDisplaysDataType"],
            capture_output=True,
            text=True,
            check=False,
            timeout=2,
        )
    except Exception:
        return []

    devices: List[Device] = []
    current_name = None
    current_vram = 0.0
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith("Chipset Model:") or line.startswith("Model:"):
            current_name = line.split(":", 1)[1].strip()
        if "VRAM" in line and ":" in line:
            value = line.split(":", 1)[1].strip()
            if value.endswith("GB"):
                try:
                    current_vram = float(value.replace("GB", "").strip())
                except ValueError:
                    current_vram = 0.0
        if current_name:
            devices.append(
                Device(
                    name=current_name,
                    backend="metal",
                    vram_gb=current_vram,
                    tflops=float(os.getenv("RELAY_GPU_TFLOPS", "20")),
                    bandwidth_gbps=float(os.getenv("RELAY_GPU_BW_GBPS", "300")),
                )
            )
            current_name = None
            current_vram = 0.0
    return devices
