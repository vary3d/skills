#!/usr/bin/env python3
"""Single-view PNG render. Cross-platform (macOS/Linux/Windows, no bash).

Usage: preview.py model.scad [out.png] [iso|front|back|left|right|top|bottom|cover]
       [--openscad-arg VALUE] (repeatable; same as validate.py)
"""
from __future__ import annotations

import os
import struct
import subprocess
import sys
import zlib
from math import gcd
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import find_openscad_lib  # noqa: E402
import outline  # noqa: E402

VIEWS = {
    "iso": "55,0,25",
    "front": "90,0,0",
    "back": "90,0,180",
    "left": "90,0,90",
    "right": "90,0,270",
    "top": "0,0,0",
    "bottom": "180,0,0",
    # Viewer default: position (r,-r,r), Z-up. rx = 90 - atan(1/sqrt2), rz = -45
    "cover": "54.736,0,315",
}

VARY3D_SCHEME = {
    "name": "Vary3D",
    "index": 1500,
    "show-in-gui": True,
    "colors": {
        "background": "#FFFFFF",
        "axes-color": "#4D4D4C",
        "opencsg-face-front": "#2A9D90",
        "opencsg-face-back": "#1F7A70",
        "cgal-face-front": "#2A9D90",
        "cgal-face-2d": "#2A9D90",
        "cgal-face-back": "#1F7A70",
        "cgal-edge-front": "#1F7A70",
        "cgal-edge-2d": "#1F7A70",
        "cgal-edge-back": "#1F7A70",
        "crosshair": "#2A9D90",
    },
}


def scheme_dir() -> Path | None:
    if sys.platform == "darwin":
        return Path.home() / "Library/Application Support/OpenSCAD/color-schemes/render"
    if sys.platform.startswith("linux"):
        return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "OpenSCAD/color-schemes/render"
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "OpenSCAD/color-schemes/render"
    return None


def ensure_vary3d_scheme() -> bool:
    d = scheme_dir()
    if d is None:
        return False
    f = d / "Vary3D.json"
    if f.is_file():
        return True
    try:
        d.mkdir(parents=True, exist_ok=True)
        import json

        f.write_text(json.dumps(VARY3D_SCHEME, indent=2) + "\n", encoding="utf-8")
        return True
    except OSError:
        return False


PREVIEW_DIRNAME = ".openscad-preview"


def preview_dir(scad: Path) -> Path:
    """Directory beside the .scad for preview PNGs.

    Many agent image viewers accept workspace paths only — not /tmp. Default all
    preview, probe, and section outputs here (add to .gitignore).
    """
    return scad.resolve().parent / PREVIEW_DIRNAME


def peel_openscad_args(argv: list[str]) -> tuple[list[str], list[str]]:
    """Split `--openscad-arg VALUE` (repeatable) from positional argv.

    Same flag as validate.py. Typical split-model use:
    `--openscad-arg=-D --openscad-arg=part="lid"`
    """
    extra: list[str] = []
    rest: list[str] = []
    i = 0
    n = len(argv)
    while i < n:
        a = argv[i]
        if a == "--openscad-arg":
            if i + 1 >= n:
                print("preview.py: --openscad-arg needs a value", file=sys.stderr)
                sys.exit(2)
            extra.append(argv[i + 1])
            i += 2
        elif a.startswith("--openscad-arg="):
            extra.append(a.split("=", 1)[1])
            i += 1
        else:
            rest.append(a)
            i += 1
    return rest, extra


BG_THRESH = 248
AA_PAD = 3
# Object AABB occupies this fraction of the limiting canvas side.
# About 10% margin on that axis; the other axis gets more if the silhouette is not 4:3.
FILL = 0.80


def _is_background(r: int, g: int, b: int) -> bool:
    return r >= BG_THRESH and g >= BG_THRESH and b >= BG_THRESH


def _content_bbox(rows: list[bytearray], width: int, height: int):
    minx, miny, maxx, maxy = width, height, -1, -1
    for y, row in enumerate(rows):
        for x in range(width):
            i = x * 3
            if _is_background(row[i], row[i + 1], row[i + 2]):
                continue
            if x < minx:
                minx = x
            if x > maxx:
                maxx = x
            if y < miny:
                miny = y
            if y > maxy:
                maxy = y
    if maxx < 0:
        return None
    return minx, miny, maxx, maxy


def _canvas_size(obj_w: int, obj_h: int, img_w: int, img_h: int) -> tuple[int, int]:
    """Same-aspect canvas (cover 4:3) with the object centered at FILL."""
    fill = float(os.environ.get("OPENSCAD_COVER_FILL", FILL))
    fill = min(0.92, max(0.4, fill))
    g = gcd(img_w, img_h) or 1
    rw, rh = img_w // g, img_h // g
    fill_i = max(1, int(round(fill * 100)))
    k = max(
        (obj_w * 100 + rw * fill_i - 1) // (rw * fill_i),
        (obj_h * 100 + rh * fill_i - 1) // (rh * fill_i),
        1,
    )
    return rw * k, rh * k


def _write_rgb_png(path: Path, width: int, height: int, rows: list[bytearray]) -> None:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(
            ">I", zlib.crc32(tag + data) & 0xFFFFFFFF
        )

    raw = bytearray()
    for row in rows:
        raw.append(0)
        raw.extend(row[: width * 3])
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


def tighten_png(path: Path) -> None:
    """Place the object in the center of a same-aspect canvas (cover stays 4:3).

    Not a minimum crop: the AABB fills about 80% of the limiting side so the
    margin stays even. OpenSCAD --viewall often leaves the mesh in a corner;
    compositing onto a new white canvas recenters it.
    """
    if os.environ.get("OPENSCAD_NO_CROP"):
        return
    width, height, raw, ctype = outline.read_png(path)
    rows = outline.unfilter(width, height, raw, ctype)
    bbox = _content_bbox(rows, width, height)
    if bbox is None:
        return
    minx, miny, maxx, maxy = bbox
    minx = max(0, minx - AA_PAD)
    miny = max(0, miny - AA_PAD)
    maxx = min(width - 1, maxx + AA_PAD)
    maxy = min(height - 1, maxy + AA_PAD)
    obj_w = maxx - minx + 1
    obj_h = maxy - miny + 1
    canvas_w, canvas_h = _canvas_size(obj_w, obj_h, width, height)
    ox = (canvas_w - obj_w) // 2
    oy = (canvas_h - obj_h) // 2
    white = bytes([255, 255, 255]) * canvas_w
    out_rows = [bytearray(white) for _ in range(canvas_h)]
    for i in range(obj_h):
        src = rows[miny + i][minx * 3 : (maxx + 1) * 3]
        dest = ox * 3
        out_rows[oy + i][dest : dest + len(src)] = src
    _write_rgb_png(path, canvas_w, canvas_h, out_rows)


def render(scad: Path, out: Path, view: str, extra: list[str] | None = None) -> int:
    rot = os.environ.get("OPENSCAD_ROT", VIEWS[view])
    if view == "cover":
        imgsize = os.environ.get("OPENSCAD_IMGSIZE", "1200,900")
        if ensure_vary3d_scheme():
            scheme = "Vary3D"
        else:
            print("warning: could not install Vary3D color scheme; cover falls back to Tomorrow", file=sys.stderr)
            scheme = "Tomorrow"
    else:
        imgsize = os.environ.get("OPENSCAD_IMGSIZE", "800,800")
        scheme = "Tomorrow"
    scheme = os.environ.get("OPENSCAD_COLORSCHEME", scheme)

    openscad = find_openscad_lib.find()
    if not openscad:
        print("openscad not found. Install from https://openscad.org/downloads.html or set OPENSCAD=", file=sys.stderr)
        return 1

    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        openscad,
        "--viewall",
        "--autocenter",
        f"--imgsize={imgsize}",
        "--projection=o",
        f"--camera=0,0,0,{rot},0",
        f"--colorscheme={scheme}",
    ]
    if os.environ.get("OPENSCAD_RENDER"):
        cmd.append("--render")
    cmd += list(extra or [])
    cmd += ["-o", str(out), str(scad)]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    log = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0 or not out.is_file() or out.stat().st_size == 0:
        sys.stderr.write(log)
        return proc.returncode or 1
    if os.environ.get("OPENSCAD_VERBOSE"):
        sys.stderr.write(log)
    try:
        tighten_png(out)
    except (ValueError, OSError) as exc:
        print(f"warning: could not tighten {out.name}: {exc}", file=sys.stderr)
    print(out)
    return 0


def main() -> int:
    argv, extra = peel_openscad_args(sys.argv[1:])
    if not argv:
        print(
            "usage: preview.py model.scad [out.png] [view] [--openscad-arg ...]",
            file=sys.stderr,
        )
        return 2
    scad = Path(argv[0])
    if not scad.is_file():
        print(f"missing {scad}", file=sys.stderr)
        return 1
    view = argv[2] if len(argv) > 2 else "iso"
    if view not in VIEWS:
        print(f"unknown view: {view}", file=sys.stderr)
        return 2
    default_out = scad.with_name(f"{scad.stem}-{view}.png")
    out = Path(argv[1]) if len(argv) > 1 and argv[1] not in VIEWS else default_out
    return render(scad.resolve(), out, view, extra=extra)


if __name__ == "__main__":
    sys.exit(main())
