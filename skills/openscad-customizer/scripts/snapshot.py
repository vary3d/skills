#!/usr/bin/env python3
"""Collect this round's edited .scad files plus the PNGs used to judge them
into .openscad-iter/NNN/ next to the working file. Never edit past rounds.

Usage:
  snapshot.py path/to/model.scad [--reason TEXT] [--also other.scad ...] png [png...]
  snapshot.py path/to/dir [--reason TEXT] png [png...]
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import subprocess


def allocate(target: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "version-scad.py"), str(target)],
        capture_output=True,
        text=True,
    )
    sys.stderr.write(proc.stderr)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout)
        raise SystemExit(proc.returncode)
    out = {}
    for line in proc.stdout.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k] = v
    return out


def relpath_from(file: Path, root: Path) -> Path:
    f = file.resolve()
    r = root.resolve()
    try:
        return f.relative_to(r)
    except ValueError:
        return Path(f.name)


def main() -> int:
    argv = sys.argv[1:]
    if not argv:
        print("usage: snapshot.py model.scad|model-dir [--reason TEXT] [--also scad] png [png...]", file=sys.stderr)
        return 2
    target = Path(argv[0])
    argv = argv[1:]
    reason = ""
    also: list[str] = []
    pngs: list[str] = []
    i = 0
    while i < len(argv):
        if argv[i] == "--reason":
            reason = argv[i + 1]
            i += 2
        elif argv[i] == "--also":
            also.append(argv[i + 1])
            i += 2
        else:
            pngs = argv[i:]
            break
    if not pngs:
        print("snapshot needs at least one PNG so scad and images stay in sync", file=sys.stderr)
        return 2

    alloc = allocate(target)
    model_dir = Path(alloc["model_dir"])
    next_dir = Path(alloc["next_dir"])
    next_n = alloc["next_n"]
    prev_dir = alloc.get("prev_dir") or ""

    scads: list[Path] = []
    if target.is_dir():
        scads = sorted(target.glob("*.scad"))
    else:
        scads = [target]
    scads += [Path(a) for a in also]
    if not scads:
        print(f"no .scad to snapshot in {model_dir}", file=sys.stderr)
        return 1

    next_dir.mkdir(parents=True, exist_ok=True)
    copied_scads: list[Path] = []
    for src in scads:
        if not src.is_file():
            print(f"missing scad: {src}", file=sys.stderr)
            return 1
        rel = relpath_from(src, model_dir)
        dest = next_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        copied_scads.append(dest)

    copied_pngs: list[Path] = []
    for src in pngs:
        p = Path(src)
        if not p.is_file():
            print(f"missing png: {p}", file=sys.stderr)
            return 1
        dest = next_dir / p.name
        shutil.copy2(p, dest)
        copied_pngs.append(dest)

    if reason:
        (next_dir / "note.txt").write_text(reason + "\n", encoding="utf-8")

    print(f"snapshot={next_n}")
    print(f"model_dir={model_dir}")
    print(f"round_dir={next_dir}")
    print(f"scads={' '.join(str(p) for p in copied_scads)}")
    print(f"pngs={' '.join(str(p) for p in copied_pngs)}")
    if prev_dir:
        prev_pngs = sorted(Path(prev_dir).glob("*.png"))
        print(f"prev_n={Path(prev_dir).name}")
        print(f"prev_dir={prev_dir}")
        print(f"prev_pngs={' '.join(str(p) for p in prev_pngs)}")
        print("Open current PNGs, then previous PNGs, and compare.", file=sys.stderr)
    else:
        print("prev_n=")
        print("prev_dir=")
        print("prev_pngs=")
        print("First round; open current PNGs only.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
