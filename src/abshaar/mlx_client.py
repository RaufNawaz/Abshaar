"""Talk to a local `mlx_lm.server` the same way `ollama_client` talks to Ollama.

Why this exists: run 2's LoRA adapter is served by mlx-lm (Rauf's decision,
2026-09-24 -- cheaper than fuse->GGUF and keeps the adapter swappable), but
`rag.ask()` only knew how to call Ollama, so the tuned model could not be put
behind retrieval and the citation gate. Measuring the acceptance criterion
(`tuned+RAG >= base+RAG`) was therefore impossible, and after the 2026-09-24
finding that the tuned model invents sources when served bare, serving it
without that gate is the wrong thing to do anyway.

The server is OpenAI-compatible, so this is a thin POST. Start it with:

    ./scripts/serve_tuned.sh

Model strings beginning `mlx:` route here; everything else goes to Ollama. The
text after the prefix is only a label -- which weights are loaded is decided by
the server's own --model/--adapter-path -- so `--model mlx:run2` records a
distinguishable row in eval_baseline.md without implying this code chose them.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

MLX_PREFIX = "mlx:"
DEFAULT_ENDPOINT = "http://127.0.0.1:8080/v1/chat/completions"


def is_mlx_model(model: str) -> bool:
    return model.startswith(MLX_PREFIX)


def run_mlx_chat(
    model: str,
    system_prompt: str,
    user_prompt: str,
    endpoint: str = DEFAULT_ENDPOINT,
    timeout: int = 300,
) -> str:
    """Mirror of run_ollama_chat: same sampling, same return shape."""
    payload = {
        # mlx_lm.server ignores this and serves whatever it was started with,
        # but the field is required by the OpenAI schema.
        "model": model[len(MLX_PREFIX) :] or "local",
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
        "top_p": 0.9,
        "max_tokens": 800,
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            f"No mlx_lm.server at {endpoint} ({exc}). Start it with "
            "./scripts/serve_tuned.sh"
        ) from exc
    return body["choices"][0]["message"]["content"]


def run_chat(
    model: str, system_prompt: str, user_prompt: str, timeout: int = 180
) -> str:
    """Route to mlx-lm or Ollama based on the model string."""
    if is_mlx_model(model):
        return run_mlx_chat(model, system_prompt, user_prompt, timeout=timeout)
    from abshaar.ollama_client import run_ollama_chat

    return run_ollama_chat(model, system_prompt, user_prompt, timeout=timeout)
