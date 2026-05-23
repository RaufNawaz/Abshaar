from __future__ import annotations

import json
import importlib.util
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from abshaar.jsonl import read_jsonl, write_jsonl
from abshaar.prompts import build_prompt_pack


def check_ollama() -> dict[str, Any]:
    result: dict[str, Any] = {
        "cli_found": shutil.which("ollama") is not None,
        "version": None,
        "api_available": False,
        "models": [],
        "optional_packages": {},
    }

    if result["cli_found"]:
        completed = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        result["version"] = completed.stdout.strip() or completed.stderr.strip()

    try:
        request = urllib.request.Request("http://localhost:11434/api/tags", method="GET")
        with urllib.request.urlopen(request, timeout=3) as response:
            payload = json.loads(response.read().decode("utf-8"))
        result["api_available"] = True
        result["models"] = [item.get("name") for item in payload.get("models", [])]
    except (OSError, urllib.error.URLError, json.JSONDecodeError):
        result["api_available"] = False

    for package_name in ["ollama", "sentence_transformers", "chromadb", "transformers", "torch"]:
        result["optional_packages"][package_name] = importlib.util.find_spec(package_name) is not None

    return result


def run_ollama_chat(model: str, system_prompt: str, user_prompt: str) -> str:
    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "options": {
            "temperature": 0.3,
            "top_p": 0.9,
        },
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        "http://localhost:11434/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        response_payload = json.loads(response.read().decode("utf-8"))
    return response_payload["message"]["content"]


def draft_poem(root: Path, poem_id: str, model: str = "qwen3:8b") -> Path:
    pack = build_prompt_pack(root, poem_id)
    raw_output = run_ollama_chat(model, pack["system_prompt"], pack["user_prompt"])
    output_path = root / "data" / "annotations" / "model_outputs.jsonl"
    existing = read_jsonl(output_path)
    output_id = f"model_output_{poem_id}_{len(existing) + 1:04d}"
    existing.append(
        {
            "id": output_id,
            "poem_id": poem_id,
            "model_stack": {
                "generator": f"{model} via Ollama",
            },
            "prompt_version": "draft_prompt_v1",
            "retrieved_context_ids": pack.get("context_ids", {}),
            "raw_output": raw_output,
            "parsed_output": None,
            "review_status": "needs_review",
        }
    )
    write_jsonl(output_path, existing)
    return output_path
