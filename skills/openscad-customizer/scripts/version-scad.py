#!/usr/bin/env python3
"""Allocate the next three-digit round under the entry file's .openscad-iter/.

stdout prints key=value lines; human notes go to stderr.
Usage: version-scad.py model.scad|model-dir [--dir ITER_ROOT]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROUND_RE = re.compile(r"^\d{3}$")


def main() -> int:
    argv = sys.argv[1:]
    if not argv:
        print("usage: version-scad.py model.scad|model-dir [--dir ITER_ROOT]", file=sys.stderr)
        return 2
    target = Path(argv[0])
    iter_root: Path | None = None
    if "--dir" in argv:
        i = argv.index("--dir")
        iter_root = Path(argv[i + 1])
    if target.suffix == ".scad":
        if not target.is_file():
            print(f"missing {target}", file=sys.stderr)
            return 1
        model_dir = target.resolve().parent
    elif target.is_dir():
        model_dir = target.resolve()
    else:
        print(f"missing {target}", file=sys.stderr)
        return 1
    root = iter_root or (model_dir / ".openscad-iter")
    root.mkdir(parents=True, exist_ok=True)
    gitignore = root / ".gitignore"
    if not gitignore.is_file():
        gitignore.write_text("*\n", encoding="utf-8")
    existing = sorted(d.name for d in root.iterdir() if d.is_dir() and ROUND_RE.match(d.name))
    if existing:
        prev_n = existing[-1]
        next_n = f"{int(prev_n) + 1:03d}"
        prev_dir = root / prev_n
    else:
        prev_n = ""
        next_n = "001"
        prev_dir = ""
    next_dir = root / next_n
    kv = {
        "slug": model_dir.name,
        "model_dir": str(model_dir),
        "iter_root": str(root),
        "iter_dir": str(next_dir),
        "prev_n": prev_n,
        "next_n": next_n,
        "prev_dir": str(prev_dir) if prev_dir else "",
        "next_dir": str(next_dir),
        "prev_stem": prev_n,
        "next_stem": next_n,
    }
    for k, v in kv.items():
        print(f"{k}={v}")
    print(f"Next round: {next_n}", file=sys.stderr)
    if prev_n:
        print(f"Previous: {prev_n} ({prev_dir})", file=sys.stderr)
    else:
        print("No previous round", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
