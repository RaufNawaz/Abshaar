# training/

Configs, adapters, and serving assets for the Bulleh Shah expert model
(plan: `docs/15_bulleh_shah_expert_model_implementation_plan.md`, Phases 5–6).

| Path | What it is |
|---|---|
| `axolotl_qwen3_8b.yml` | Path B (cloud QLoRA) config for Qwen3-8B. Verify field names against current Axolotl docs before a paid run. |
| `Modelfile.abshaar-bulleh` | Ollama Modelfile template for serving the fused model (Phase 6). Fill in the FROM path after fusing. |
| `adapters/` | LoRA adapter checkpoints from `scripts/train_lora.sh`. Gitignored (large); record SHA-256 + eval scores in `EVAL_MATRIX.md` instead. |
| `EVAL_MATRIX.md` | Final base / base+RAG / LoRA / LoRA+RAG comparison (written in Phase 6). |

Rules (from the plan):
- No training run before the baseline evals exist in
  `data/processed/training/eval_baseline.md`.
- Acceptance: tuned+RAG ≥ base+RAG on factual scores AND ≥ base on honesty
  traps. A model that hallucinates more than base is rejected.
- Training data comes ONLY from `data/processed/training/mlx/` (gated,
  leak-scanned). Never point a trainer at raw corpus files.
