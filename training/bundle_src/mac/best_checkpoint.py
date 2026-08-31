#!/usr/bin/env python3
"""Read a training log and say which checkpoint to actually keep.

mlx-lm's final `adapters.safetensors` is the LAST state, not the BEST one.
If validation loss bottoms partway through and then climbs, the final file is
a worse model than a checkpoint you already have on disk. This parses the log
and says so plainly.

Usage:
    python3 best_checkpoint.py <work_root>/logs/train-*.log [--adapter-dir DIR]
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

VAL_RE = re.compile(r"Iter\s+(\d+):\s*Val loss\s+([0-9.]+)")
TRAIN_RE = re.compile(r"Iter\s+(\d+):\s*Train loss\s+([0-9.]+)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("--adapter-dir", type=Path, default=None,
                        help="Adapter folder, to check which checkpoints actually exist")
    args = parser.parse_args()

    text = args.log.read_text(encoding="utf-8", errors="replace")
    vals = [(int(i), float(v)) for i, v in VAL_RE.findall(text)]
    trains = dict((int(i), float(v)) for i, v in TRAIN_RE.findall(text))
    if not vals:
        print(f"No validation lines found in {args.log}")
        return 1

    print(f"{'iter':>7}  {'val loss':>9}  {'train loss':>10}   trend")
    previous = None
    for iteration, value in vals:
        train = trains.get(iteration)
        arrow = ""
        if previous is not None:
            arrow = "down" if value < previous else ("up  <-- worse" if value > previous else "flat")
        print(f"{iteration:>7}  {value:>9.3f}  {(f'{train:.3f}' if train else '-'):>10}   {arrow}")
        previous = value

    best_iter, best_val = min(vals, key=lambda pair: pair[1])
    final_iter, final_val = vals[-1]
    print()
    print(f"Best validation loss: {best_val:.3f} at iteration {best_iter}")
    print(f"Final validation loss: {final_val:.3f} at iteration {final_iter}")

    if best_iter == final_iter:
        print("\nThe final adapter IS the best one. Use adapters.safetensors.")
    else:
        worse_by = final_val - best_val
        print(f"\nThe run got WORSE after iteration {best_iter} (by {worse_by:.3f}).")
        print("The final adapters.safetensors is not your best model.")
        candidate = f"{best_iter:07d}_adapters.safetensors"
        if args.adapter_dir:
            path = args.adapter_dir / candidate
            if path.exists():
                print(f"Use this checkpoint instead:\n  {path}")
            else:
                existing = sorted(args.adapter_dir.glob("[0-9]*_adapters.safetensors"))
                print(f"\n{candidate} was not saved (--save-every did not line up with")
                print("--steps-per-eval). Closest checkpoints that do exist:")
                for item in existing:
                    print(f"  {item.name}")
        else:
            print(f"Look for {candidate} in the adapter folder (pass --adapter-dir to check).")
        print("\nTo use it: copy it over adapters.safetensors in a COPY of the adapter")
        print("folder (keep the original), then point the fuse/import step at that copy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
