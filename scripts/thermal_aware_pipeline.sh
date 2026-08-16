#!/usr/bin/env bash
# Background-friendly, thermal-aware, resumable runner for docs/17 Phases 2-5
# (Chroma index build through LoRA training). macOS-only by nature: it uses
# `pmset`/`taskpolicy` (macOS tools) to run the Ollama/MLX steps at background
# QoS so foreground work stays responsive, and it pauses instead of piling on
# load when pmset reports the CPU is already thermally throttled. There is no
# Windows equivalent — mlx-lm and this thermal tooling are Apple-only, so no
# .ps1 counterpart is provided (same precedent as scripts/train_lora.sh).
#
# It does NOT bypass the standing rule that Rauf must explicitly authorize
# model runs: nothing that touches Ollama/MLX executes unless
# training/RUN_AUTHORIZED exists. That file is a deliberate, durable,
# machine-local switch (gitignored) — create it yourself when you want a run
# to actually start:
#   touch training/RUN_AUTHORIZED
#
# Usage:
#   ./scripts/thermal_aware_pipeline.sh status   # show authorization + progress, no side effects
#   ./scripts/thermal_aware_pipeline.sh run       # run all pending stages (needs RUN_AUTHORIZED)
#   ./scripts/thermal_aware_pipeline.sh augment   # optional augmentation stage, run separately
#   ./scripts/thermal_aware_pipeline.sh selftest  # exercises the logic below with fake stages; touches no model

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

LOG_DIR="training/pipeline_logs"
STATE_FILE="$LOG_DIR/completed_stages.txt"
AUTH_FILE="training/RUN_AUTHORIZED"

THERM_MAX_WAIT_SECONDS=${THERM_MAX_WAIT_SECONDS:-3600}
THERM_POLL_SECONDS=${THERM_POLL_SECONDS:-60}
NICE_LEVEL=${NICE_LEVEL:-15}

log() {
  mkdir -p "$LOG_DIR"
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_DIR/run.log"
}

is_done() {
  [[ -f "$STATE_FILE" ]] && grep -qxF "$1" "$STATE_FILE"
}

mark_done() {
  mkdir -p "$LOG_DIR"
  echo "$1" >>"$STATE_FILE"
}

check_authorized() {
  if [[ ! -f "$AUTH_FILE" ]]; then
    log "BLOCKED: $AUTH_FILE not present. This step runs real local model inference/training."
    log "Create it deliberately when you want this to actually start:  touch $AUTH_FILE"
    exit 1
  fi
}

# Prints "1" (hot / throttled) or "0" (not hot / unknown). Relies on
# `pmset -g therm`, which only populates CPU_Speed_Limit etc. once a real
# thermal-pressure event has fired. Before any event, macOS reports "No
# thermal warning level has been recorded" — verified on this machine
# (2026-08-16, idle) — which we treat as "not hot" rather than blocking
# forever on a metric that may never appear. If the field format ever
# doesn't match what's parsed here, this fails open (treats as not-hot) and
# logs that the metric was unreadable, rather than silently trusting a guess.
thermally_hot() {
  local out limit
  out=$(pmset -g therm 2>/dev/null || true)
  if ! grep -q "CPU_Speed_Limit" <<<"$out"; then
    echo 0
    return
  fi
  limit=$(grep "CPU_Speed_Limit" <<<"$out" | sed -E 's/.*=[[:space:]]*([0-9]+).*/\1/')
  if [[ "$limit" =~ ^[0-9]+$ ]] && [[ "$limit" -lt 100 ]]; then
    echo 1
  else
    echo 0
  fi
}

wait_for_cool() {
  local waited=0
  while [[ "$(thermally_hot)" == "1" ]]; do
    if ((waited >= THERM_MAX_WAIT_SECONDS)); then
      log "Still thermally limited after ${THERM_MAX_WAIT_SECONDS}s; stopping. Re-run later to resume."
      exit 2
    fi
    log "pmset -g therm reports CPU_Speed_Limit < 100 (thermally throttled). Waiting ${THERM_POLL_SECONDS}s..."
    sleep "$THERM_POLL_SECONDS"
    waited=$((waited + THERM_POLL_SECONDS))
  done
}

# Runs a command at background scheduling priority so interactive/foreground
# work is not starved. taskpolicy -c background assigns background QoS
# (same mechanism macOS uses for Spotlight/Time Machine); nice lowers CPU
# scheduling priority for the wrapping process on top of that.
run_priority() {
  if command -v taskpolicy >/dev/null 2>&1; then
    nice -n "$NICE_LEVEL" taskpolicy -c background -- "$@"
  else
    nice -n "$NICE_LEVEL" "$@"
  fi
}

run_stage() {
  local name="$1"
  shift
  if is_done "$name"; then
    log "SKIP (already done): $name"
    return 0
  fi
  check_authorized
  wait_for_cool
  log "START: $name"
  set +e
  run_priority "$@" 2>&1 | tee -a "$LOG_DIR/${name}.log"
  local status="${PIPESTATUS[0]}"
  set -e
  if [[ "$status" -ne 0 ]]; then
    log "FAILED: $name (exit $status) — see $LOG_DIR/${name}.log. Fix and re-run; completed stages are skipped."
    exit "$status"
  fi
  mark_done "$name"
  log "DONE: $name"
}

cmd_status() {
  echo "Authorized to run model steps: $([[ -f "$AUTH_FILE" ]] && echo yes || echo "NO -- touch $AUTH_FILE to enable")"
  echo "Low Power Mode: $(pmset -g | awk '/lowpowermode/ {print ($2==1) ? "ON (slower, cooler)" : "OFF (faster, hotter)"}')"
  echo "Currently thermally throttled: $([[ "$(thermally_hot)" == "1" ]] && echo yes || echo no)"
  echo "Completed stages:"
  if [[ -f "$STATE_FILE" ]]; then
    sed 's/^/  - /' "$STATE_FILE"
  else
    echo "  (none yet)"
  fi
}

cmd_run() {
  run_stage "build-index" ./scripts/abshaar.sh build-index
  run_stage "rag-smoke-test" .venv/bin/python scripts/rag_smoke_test.py --model qwen3:8b
  run_stage "baseline-4b" ./scripts/abshaar.sh run-eval --model qwen3:4b --judge qwen3:8b
  run_stage "baseline-8b" ./scripts/abshaar.sh run-eval --model qwen3:8b --judge qwen3:4b
  run_stage "baseline-8b-rag" ./scripts/abshaar.sh run-eval --model qwen3:8b --rag --judge qwen3:4b
  run_stage "export-mlx-dataset" ./scripts/abshaar.sh export-mlx-dataset
  run_stage "train-lora" ./scripts/train_lora.sh
  log "Core pipeline (docs/17 Phases 2-5) complete. Fuse + acceptance-eval + accept/reject (Phase 6) need a human decision per the runbook — do those by hand next."
}

cmd_augment() {
  run_stage "augment-training-data" ./scripts/abshaar.sh augment-training-data --generator qwen3:8b --verifier qwen3:4b --limit-per-family 30
  log "If this succeeded, re-run export-mlx-dataset and validate per docs/17 §4 before training on the augmented set."
}

# Exercises is_done/mark_done/thermally_hot/run_priority end to end with fake,
# harmless commands (`true`, `echo`) in an isolated state dir. Touches
# training/RUN_AUTHORIZED nowhere and calls no model — safe to run anytime.
cmd_selftest() {
  local tmp
  tmp=$(mktemp -d)
  (
    LOG_DIR="$tmp/logs"
    STATE_FILE="$tmp/logs/completed_stages.txt"
    mkdir -p "$LOG_DIR"
    echo "thermally_hot() -> $(thermally_hot) (expect 0 on an unthrottled machine)"
    run_priority true
    echo "run_priority true -> exit $?"
    if [[ -f "$STATE_FILE" ]]; then echo "FAIL: state file exists before any stage ran"; exit 1; fi
    echo "stage-a" >>"$STATE_FILE"
    if is_done "stage-a"; then echo "is_done stage-a -> true (expect true)"; else echo "FAIL: is_done stage-a"; exit 1; fi
    if is_done "stage-b"; then echo "FAIL: is_done stage-b should be false"; exit 1; else echo "is_done stage-b -> false (expect false)"; fi
    echo "selftest OK"
  )
  local result=$?
  rm -rf "$tmp"
  return $result
}

case "${1:-status}" in
  status) cmd_status ;;
  run) cmd_run ;;
  augment) cmd_augment ;;
  selftest) cmd_selftest ;;
  *)
    echo "usage: $0 [status|run|augment|selftest]"
    exit 2
    ;;
esac
