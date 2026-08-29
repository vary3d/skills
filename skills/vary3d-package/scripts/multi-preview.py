#!/usr/bin/env python3
"""Six-view PNGs. Cross-platform. Usage: multi-preview.py model.scad [outdir] [view...]

PNG output defaults to <scad-dir>/.openscad-preview/ so agent image viewers can
open them (workspace paths only — not /tmp).

Options:
  --probe          Render 200x200 _probe.png into .openscad-preview/
  --imgsize WxH    Override the default 800x800 (8-bit RGB, no alpha, non-interlaced)
  --openscad-arg   Extra OpenSCAD CLI arg (repeatable). Split: -D and part="lid"
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import preview  # noqa: E402

DEFAULT_VIEWS = ["iso", "front", "back", "left", "right", "top"]
DEFAULT_IMGSIZE = "800,800"
PROBE_NAME = "_probe.png"


def probe(scad: Path, extra: list[str] | None = None) -> int:
    """Render a tiny probe PNG beside the .scad; keep the file for Read."""
    scad = scad.resolve()
    outdir = preview.preview_dir(scad)
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / PROBE_NAME
    os.environ["OPENSCAD_IMGSIZE"] = "200,200"
    return preview.render(scad, out, "iso", extra=extra)


def default_outdir(scad: Path) -> Path:
    return preview.preview_dir(scad)


def main() -> int:
    argv, extra = preview.peel_openscad_args(sys.argv[1:])
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    if "--probe" in argv:
        argv.remove("--probe")
        if not argv:
            print("usage: multi-preview.py --probe model.scad [--openscad-arg ...]", file=sys.stderr)
            return 2
        return probe(Path(argv[0]), extra=extra)
    if "--imgsize" in argv:
        i = argv.index("--imgsize")
        if i + 1 >= len(argv):
            print("--imgsize needs a value like 800,800", file=sys.stderr)
            return 2
        os.environ["OPENSCAD_IMGSIZE"] = argv[i + 1]
        del argv[i : i + 2]
    else:
        os.environ.setdefault("OPENSCAD_IMGSIZE", DEFAULT_IMGSIZE)

    scad = Path(argv[0])
    if not scad.is_file():
        print(f"missing {scad}", file=sys.stderr)
        return 1
    stem = scad.stem
    outdir = Path(argv[1]) if len(argv) > 1 and argv[1] not in preview.VIEWS else default_outdir(scad)
    views = [a for a in argv[1:] if a in preview.VIEWS] or DEFAULT_VIEWS
    outdir.mkdir(parents=True, exist_ok=True)
    rc = 0
    for view in views:
        out = outdir / f"{stem}-{view}.png"
        r = preview.render(scad.resolve(), out, view, extra=extra)
        if r != 0:
            rc = r
    print(outdir)
    return rc


if __name__ == "__main__":
    sys.exit(main())
