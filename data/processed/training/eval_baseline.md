# Evaluation Results

Scores: factual = mean judge/F1 score (0-1); honesty = decline rate on traps;
disputed = hedge rate on settle-it probes. Probe set: probes.jsonl (fixed).

| run | factual | honesty | disputed | probes |
|---|---|---|---|---|
| qwen3:8b | 0.239 | 0.267 | 0.3 | 50 |
| qwen3:8b + RAG | 0.415 | 0.933 | 0.5 | 50 |
