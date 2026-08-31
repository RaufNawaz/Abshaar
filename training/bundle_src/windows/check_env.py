#!/usr/bin/env python3
"""Report the machine's training environment and fail loudly if it can't train.

Writes outbox/env_report.json so the report survives in the artefacts you
carry off the workstation, and exits non-zero when CUDA is missing -- a
CPU-only torch install is the single most common way this bootstrap goes
quietly wrong (the PyPI default torch wheel for Windows is CPU-only).
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import sys
from pathlib import Path


def main() -> int:
    report: dict = {
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "platform": platform.platform(),
    }

    try:
        import torch
    except Exception as exc:  # pragma: no cover - environment probe
        report["error"] = f"torch import failed: {exc}"
        print(json.dumps(report, indent=2))
        return 1

    report["torch"] = torch.__version__
    report["torch_cuda_build"] = torch.version.cuda
    report["cuda_available"] = torch.cuda.is_available()

    for name in ("transformers", "peft", "accelerate", "huggingface_hub"):
        try:
            module = __import__(name)
            report[name] = getattr(module, "__version__", "unknown")
        except Exception as exc:
            report[name] = f"MISSING ({exc})"

    if torch.cuda.is_available():
        props = torch.cuda.get_device_properties(0)
        report["gpu"] = {
            "name": props.name,
            "total_memory_gb": round(props.total_memory / (1024 ** 3), 1),
            "capability": f"{props.major}.{props.minor}",
            "bf16_supported": bool(torch.cuda.is_bf16_supported()),
            "device_count": torch.cuda.device_count(),
        }

    root = Path(os.environ.get("ABSHAAR_ROOT", ".")).resolve()
    report["work_root"] = str(root)
    try:
        usage = shutil.disk_usage(str(root))
        report["free_disk_gb"] = round(usage.free / (1024 ** 3), 1)
    except Exception:
        report["free_disk_gb"] = None
    report["hf_home"] = os.environ.get("HF_HOME")

    print(json.dumps(report, indent=2))

    outbox = root / "outbox"
    try:
        outbox.mkdir(parents=True, exist_ok=True)
        (outbox / "env_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    except Exception as exc:
        print(f"(could not write env_report.json: {exc})", file=sys.stderr)

    if not report["cuda_available"]:
        print(
            "\nERROR: torch cannot see a CUDA device.\n"
            "  - If torch version has no '+cu' suffix you installed the CPU-only wheel.\n"
            "    Fix: venv\\Scripts\\python.exe -m pip install --force-reinstall \\\n"
            "         --index-url https://download.pytorch.org/whl/cu128 torch\n"
            "  - Otherwise check `nvidia-smi` works and the driver is current.",
            file=sys.stderr,
        )
        return 1

    vram = report.get("gpu", {}).get("total_memory_gb", 0)
    if vram and vram < 30:
        print(
            f"\nWARNING: {vram} GB of VRAM. bf16 LoRA on an 8B base wants ~30 GB.\n"
            "Train a smaller base (--model Qwen/Qwen3-4B) or expect to tune batch size.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
