#!/usr/bin/env python3
"""Render a 4:3 listing cover. Cross-platform, no bash.

Usage:
  cover.py model.scad [out.png]
  cover.py model.scad [out.png] --set name=value --set x=y
  cover.py model.scad [out.png] --params-json '{"flange_length":60}'
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import preview  # noqa: E402


def main() -> int:
    argv = sys.argv[1:]
    if not argv:
        print("usage: cover.py model.scad [out.png] [--set name=value ...] [--params-json JSON]", file=sys.stderr)
        return 2
    scad = Path(argv[0])
    if not scad.is_file():
        print(f"missing {scad}", file=sys.stderr)
        return 1
    scad = scad.resolve()
    out: Path | None = None
    sets: list[str] = []
    params_json = ""
    i = 1
    if i < len(argv) and argv[i] not in ("--set", "--params-json"):
        out = Path(argv[i])
        i += 1
    while i < len(argv):
        if argv[i] == "--set":
            sets.append(argv[i + 1])
            i += 2
        elif argv[i] == "--params-json":
            params_json = argv[i + 1]
            i += 2
        else:
            print(f"unknown arg: {argv[i]}", file=sys.stderr)
            return 2
    if out is None:
        out = scad.parent / "cover.png"

    src = scad
    tmpdir = None
    if sets or params_json:
        cmd = [sys.executable, str(SCRIPT_DIR / "override-params.py"), str(scad), "-o", "@OUT@"]
        if params_json:
            cmd += ["--params-json", params_json]
        for s in sets:
            cmd += ["--set", s]
        tmpdir = Path(tempfile.mkdtemp(prefix="vary3d-cover-"))
        over = tmpdir / "over.scad"
        cmd[cmd.index("@OUT@")] = str(over)
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            sys.stderr.write(proc.stderr or proc.stdout or "")
            return proc.returncode
        src = over

    # Temp copies live outside the model dir; let relative include/use fall back there.
    env_path = str(scad.parent)
    prev = os.environ.get("OPENSCADPATH")
    os.environ["OPENSCADPATH"] = env_path + (os.pathsep + prev if prev else "")
    try:
        return preview.render(src, out, "cover")
    finally:
        if tmpdir is not None:
            import shutil

            shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
