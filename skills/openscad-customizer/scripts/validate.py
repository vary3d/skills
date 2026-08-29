#!/usr/bin/env python3
"""Compile .scad to STL and measure the bounding box. Hard-gate entry point."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

# bbox.py / find-openscad.py live next to this file
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from bbox import compare_expect, count_bodies, measure_stl  # noqa: E402
from find_openscad_lib import find as _find_openscad  # noqa: E402


def find_openscad() -> str:
    found = _find_openscad()
    if found:
        return found
    raise FileNotFoundError(
        "openscad not found. Install from https://openscad.org/downloads.html or set OPENSCAD="
    )


def missing_library_line(log: str) -> str | None:
    """OpenSCAD treats a missing use/include as a warning and may still exit 0."""
    for line in log.splitlines():
        low = line.lower()
        if "can't open library" in low or "can't open include file" in low:
            return line.strip()
    return None


def compile_stl(scad: Path, stl: Path, timeout: int, extra: list[str]) -> str:
    cmd = [find_openscad(), "-o", str(stl), *extra, str(scad)]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    log = (proc.stdout or "") + (proc.stderr or "")
    missing = missing_library_line(log)
    if missing:
        raise RuntimeError(
            f"OpenSCAD missing library (still compiles leftover geometry).\n{missing}\n"
            f"{log.strip() or '(no output)'}"
        )
    if proc.returncode != 0 or not stl.exists() or stl.stat().st_size < 84:
        raise RuntimeError(
            f"OpenSCAD failed (exit {proc.returncode}).\n{log.strip() or '(no output)'}"
        )
    return log


def main() -> int:
    p = argparse.ArgumentParser(description="Compile OpenSCAD and check bbox")
    p.add_argument("scad")
    p.add_argument("--expect", nargs=3, type=float, metavar=("X", "Y", "Z"))
    p.add_argument("--tol", type=float, default=1.0)
    p.add_argument("--out", help="STL output path (default: temp file)")
    p.add_argument("--timeout", type=int, default=180)
    p.add_argument(
        "--openscad-arg",
        action="append",
        default=[],
        help="Extra args passed to openscad (repeatable)",
    )
    p.add_argument(
        "--single-body",
        action="store_true",
        help="Check that the STL contains exactly one connected solid body",
    )
    args = p.parse_args()

    scad = Path(args.scad).resolve()
    if not scad.is_file():
        print(json.dumps({"ok": False, "error": f"missing {scad}"}))
        return 1

    tmp_dir = None
    if args.out:
        stl = Path(args.out).resolve()
        stl.parent.mkdir(parents=True, exist_ok=True)
    else:
        tmp_dir = tempfile.mkdtemp(prefix="openscad-validate-")
        stl = Path(tmp_dir) / (scad.stem + ".stl")

    try:
        log = compile_stl(scad, stl, args.timeout, args.openscad_arg)
        measured = measure_stl(stl)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"ok": False, "scad": str(scad), "error": str(exc)}, indent=2))
        return 1

    result = {
        "ok": True,
        "scad": str(scad),
        "stl": str(stl),
        **{k: v for k, v in measured.items() if not k.startswith("_")},
        "openscad_log_tail": "\n".join(log.strip().splitlines()[-20:]),
    }
    if args.expect:
        result.update(compare_expect(measured, list(args.expect), args.tol))
        result["ok"] = result["bbox_ok"]

    # Single-body check (floating parts detection)
    if args.single_body:
        bodies = count_bodies(measured["_tris"])
        result["bodies"] = bodies
        if bodies != 1:
            result["ok"] = False
            result["warning"] = f"multiple bodies detected (expected 1, got {bodies})"
            print(json.dumps(result, indent=2))
            return 3  # new exit code for multi-body

    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
