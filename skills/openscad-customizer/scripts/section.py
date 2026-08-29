#!/usr/bin/env python3
"""Section PNG when six views are not enough. Default is a 2D true cut.

Plane names follow OpenSCAD Z-up: xy cuts z, xz cuts y, yz cuts x.
2D (default): projection(cut=true), upright. Use this for cavities, walls, joints.
3D (--3d): half-space intersection; camera faces the cut. Not a GPU clip.
  Iso of a 3D cutaway looks at the remaining outer shell — a hollow box reads as
  rounded front / square back, not a wall drawing. Do not use that as the cavity check.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HALF = 1.0e4
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))


def _load_override_params():
    spec = importlib.util.spec_from_file_location(
        "override_params", SCRIPT_DIR / "override-params.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


override_params = _load_override_params()


def scad_string(path: Path) -> str:
    return str(path.resolve()).replace("\\", "/")


def parse_d_assignments(extra: list[str]) -> list[tuple[str, str]]:
    """OpenSCAD -D name=value pairs from a validate.py-style extra list."""
    out: list[tuple[str, str]] = []
    i = 0
    while i < len(extra):
        a = extra[i]
        spec = None
        if a == "-D" and i + 1 < len(extra):
            spec = extra[i + 1]
            i += 2
        elif a.startswith("-D") and len(a) > 2:
            spec = a[2:]
            i += 1
        else:
            i += 1
            continue
        name, sep, rest = spec.partition("=")
        if not sep or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name.strip()):
            continue
        out.append((name.strip(), rest.strip()))
    return out


def apply_d_overrides(src: Path, dest: Path, extra: list[str]) -> None:
    """Write a temp copy with top-level -D assignments applied.

    OpenSCAD `-D` on the wrapper does not override assignments inside `include`.
    Uses override-params.py (top-level region only, comment-safe).
    """
    overrides: dict[str, object] = {}
    for name, raw in parse_d_assignments(extra):
        overrides[name] = override_params.parse_set(f"{name}={raw}")[1]
    text = override_params.apply_overrides(
        src.read_text(encoding="utf-8"), overrides, allow_missing=True
    )
    dest.write_text(text, encoding="utf-8")


def preview_extra_argv(extra: list[str]) -> list[str]:
    argv: list[str] = []
    for e in extra:
        argv += ["--openscad-arg", e]
    return argv


def halfspace_cube(plane: str, depth: float, invert: bool) -> str:
    """Half-space cube keeping one side of depth."""
    h = HALF
    if invert:
        # keep axis >= depth
        if plane == "yz":  # x
            return f"translate([{depth}, {-h}, {-h}]) cube([{h}, {2 * h}, {2 * h}]);"
        if plane == "xz":  # y
            return f"translate([{-h}, {depth}, {-h}]) cube([{2 * h}, {h}, {2 * h}]);"
        return f"translate([{-h}, {-h}, {depth}]) cube([{2 * h}, {2 * h}, {h}]);"
    # keep axis <= depth
    if plane == "yz":
        return f"translate([{-h}, {-h}, {-h}]) cube([{h + depth}, {2 * h}, {2 * h}]);"
    if plane == "xz":
        return f"translate([{-h}, {-h}, {-h}]) cube([{2 * h}, {h + depth}, {2 * h}]);"
    return f"translate([{-h}, {-h}, {-h}]) cube([{2 * h}, {2 * h}, {h + depth}]);"


def to_xy_for_projection(plane: str, depth: float) -> str:
    """Move the cut plane onto z=0 for projection(cut=true)."""
    if plane == "xy":
        return f"translate([0, 0, {-depth}])"
    if plane == "xz":
        return f"rotate([90, 0, 0]) translate([0, {-depth}, 0])"
    return f"rotate([0, -90, 0]) translate([{-depth}, 0, 0])"


# Camera that looks at the cut face when keeping axis <= depth.
# OpenSCAD: front is from -Y, back from +Y, left from +X, top from +Z.
# invert (keep >= depth) uses the opposite view.
VIEW_FACING_CUT = {
    "xy": ("top", "bottom"),
    "xz": ("back", "front"),
    "yz": ("left", "right"),
}


def default_view(plane: str, invert: bool, as_2d: bool) -> str:
    if as_2d:
        return "top"
    facing, opposite = VIEW_FACING_CUT[plane]
    return opposite if invert else facing


def upright_2d_xf(plane: str, dims2d: tuple[float, float] | None) -> str:
    """2D fix-up applied AFTER projection: upright axes + stretch the short axis.

    projection() output axes by plane:
      xy → (x, y)    already upright
      xz → (x, -z)   z points down  → flip y so z points up (front-view feel)
      yz → (-z, y)   axes swapped   → rotate(-90) gives (y, z), i.e. y right / z up

    dims2d = displayed (width, height) after the orientation fix. A flat section
    (e.g. 40×4 flange side view) otherwise renders as a hairline where holes are
    1–2 px wide and pixel analysis is noise. Stretching the short axis (≤20×)
    preserves topology — connectivity checks stay valid.
    """
    sx = sy = 1.0
    if dims2d and dims2d[0] > 0 and dims2d[1] > 0:
        lo, hi = min(dims2d), max(dims2d)
        k = max(1.0, min(20.0, hi / lo))
        if dims2d[0] >= dims2d[1]:
            sy = k
        else:
            sx = k
    if plane == "xz":
        return f"scale([{sx}, {-sy}]) "
    if plane == "yz":
        # rotate first, then scale: displayed axes are (y, z)
        return f"scale([{sx}, {sy}]) rotate(-90) "
    return f"scale([{sx}, {sy}]) "


def write_wrapper(
    src: Path,
    dest: Path,
    plane: str,
    depth: float,
    invert: bool,
    as_2d: bool,
    dims2d: tuple[float, float] | None = None,
) -> None:
    # The 2021 parser only takes include <path>, and it must be wrapped in a module for further CSG
    inc = scad_string(src)
    header = f"module __vary3d_section_src() {{\n  include <{inc}>\n}}\n"
    if as_2d:
        xf = to_xy_for_projection(plane, depth)
        up = upright_2d_xf(plane, dims2d)
        text = header + f"{up}projection(cut = true) {xf} __vary3d_section_src();\n"
    else:
        cube = halfspace_cube(plane, depth, invert)
        text = header + f"intersection() {{\n  __vary3d_section_src();\n  {cube}\n}}\n"
    dest.write_text(text, encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser(description="Render a CSG section PNG of an OpenSCAD model")
    p.add_argument("scad")
    p.add_argument("--plane", choices=("xy", "xz", "yz"), default="xz")
    p.add_argument("--depth", type=float, default=0.0, help="Cut position on the plane's normal axis (mm)")
    p.add_argument("--invert", action="store_true", help="Keep the ≥ depth side instead of ≤")
    p.add_argument(
        "--2d",
        dest="as_2d",
        action="store_true",
        help="2D true section via projection(cut=true) (default)",
    )
    p.add_argument(
        "--3d",
        dest="as_2d",
        action="store_false",
        help="3D half-space cutaway; camera faces the cut (xz→back) unless --view is set",
    )
    p.set_defaults(as_2d=True)
    p.add_argument("--view", default=None, help="Camera: iso|front|back|left|right|top|bottom")
    p.add_argument("-o", "--out", help="Output PNG")
    p.add_argument(
        "--check-floating",
        action="store_true",
        help="Auto-generate multiple sections and detect isolated islands (floating parts)",
    )
    p.add_argument(
        "--openscad-arg",
        action="append",
        default=[],
        help="Extra args passed to openscad / validate.py (repeatable). Split: -D and part=\"lid\"",
    )
    args = p.parse_args()

    src = Path(args.scad).resolve()
    if not src.is_file():
        print(f"missing {src}", file=sys.stderr)
        return 1

    extra: list[str] = list(args.openscad_arg)

    # Floating parts detection mode
    if args.check_floating:
        return check_floating(src, extra=extra)

    view = args.view or default_view(args.plane, args.invert, args.as_2d)
    stem = src.stem
    kind = "cut2d" if args.as_2d else "section"
    if args.out:
        out = Path(args.out)
    else:
        sys.path.insert(0, str(SCRIPT_DIR))
        import preview  # noqa: E402

        out = preview.preview_dir(src) / f"{stem}-{kind}-{args.plane}.png"
    out.parent.mkdir(parents=True, exist_ok=True)

    tmp = Path(tempfile.mkdtemp(prefix="vary3d-section-"))
    include_src = src
    if extra:
        patched = tmp / src.name
        apply_d_overrides(src, patched, extra)
        include_src = patched
    wrapper = tmp / "section-wrap.scad"
    write_wrapper(include_src, wrapper, args.plane, args.depth, args.invert, args.as_2d)

    preview_py = SCRIPT_DIR / "preview.py"
    env = os.environ.copy()
    env["OPENSCAD_RENDER"] = "1"  # must be F6, or viewall frames the huge half-space cube
    proc = subprocess.run(
        [sys.executable, str(preview_py), str(wrapper), str(out), view, *preview_extra_argv(extra)],
        env=env,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr or "")
        # The wrapper embeds local absolute paths; dump it only when debugging.
        if os.environ.get("SECTION_DEBUG"):
            sys.stderr.write(wrapper.read_text(encoding="utf-8"))
        return proc.returncode or 1
    print(out)
    return 0


def check_floating(src: Path, extra: list[str] | None = None) -> int:
    """Generate multiple 2D sections and detect isolated islands (floating parts).

    Strategy:
    1. Get bbox from validate.py to determine section positions
    2. Generate 3 sections per axis (25%, 50%, 75% of bbox)
    3. For each section, detect isolated white regions (islands) in the 2D PNG
    4. If an island appears in multiple sections at the same location, it's likely floating

    Returns 0 if no floating parts detected, 1 if found.
    """
    sys.path.insert(0, str(SCRIPT_DIR))
    import preview  # noqa: E402
    from bbox import measure_stl  # noqa: E402

    extra = extra or []

    # First, compile to STL to get bbox (honor -D so split tokens use that mesh)
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="vary3d-check-floating-"))
    stl = tmp / "model.stl"
    include_src = src
    if extra:
        patched = tmp / src.name
        apply_d_overrides(src, patched, extra)
        include_src = patched

    validate_py = SCRIPT_DIR / "validate.py"
    val_cmd = [sys.executable, str(validate_py), str(src), "--out", str(stl)]
    for e in extra:
        val_cmd += [f"--openscad-arg={e}"]
    proc = subprocess.run(
        val_cmd,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print(f"error: failed to compile {src}", file=sys.stderr)
        sys.stderr.write(proc.stderr or "")
        return 1

    measured = measure_stl(stl)
    bbox_min = measured["min"]
    bbox_max = measured["max"]
    size = measured["size"]

    print(f"bbox: {size[0]:.1f} × {size[1]:.1f} × {size[2]:.1f} mm")
    print(f"generating sections at 25%, 50%, 75% of each axis...")

    outdir = preview.preview_dir(src)
    outdir.mkdir(parents=True, exist_ok=True)

    # Generate sections. dims2d (displayed width/height after upright fix) lets the
    # wrapper stretch the short axis so flat sections stay readable.
    dims_by_plane = {
        "xy": (size[0], size[1]),
        "xz": (size[0], size[2]),
        "yz": (size[1], size[2]),
    }

    sections = []
    for axis, plane in enumerate(["yz", "xz", "xy"]):  # x, y, z
        for frac in [0.25, 0.5, 0.75]:
            depth = bbox_min[axis] + size[axis] * frac
            out = outdir / f"{src.stem}-check-{plane}-{int(frac*100)}.png"

            wrapper = tmp / f"section-{plane}-{int(frac*100)}.scad"
            write_wrapper(include_src, wrapper, plane, depth, invert=False, as_2d=True, dims2d=dims_by_plane[plane])

            preview_py = SCRIPT_DIR / "preview.py"
            env = os.environ.copy()
            env["OPENSCAD_RENDER"] = "1"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(preview_py),
                    str(wrapper),
                    str(out),
                    "top",
                    *preview_extra_argv(extra),
                ],
                env=env,
                capture_output=True,
                text=True,
            )
            if proc.returncode == 0:
                sections.append((plane, frac, depth, out))
                print(f"  {plane} @ {depth:.1f}mm → {out.name}")

    # Analyze sections for isolated islands
    print(f"\nanalyzing {len(sections)} sections for isolated islands...")

    # Group sections by plane
    from collections import defaultdict
    by_plane = defaultdict(list)
    for plane, frac, depth, png_path in sections:
        islands = detect_islands(png_path)
        by_plane[plane].append((frac, depth, islands, png_path))

    # A floating part is detected only if MULTIPLE sections of the SAME plane
    # show multiple regions. A single section with holes is normal.
    floating_detected = False
    for plane, results in by_plane.items():
        multi_region_count = sum(1 for _, _, islands, _ in results if islands > 1)
        total = len(results)

        print(f"\n{plane} plane:")
        for frac, depth, islands, png_path in results:
            if islands > 1:
                print(f"  ⚠ {png_path.name}: {islands} regions @ {depth:.1f}mm")
            else:
                print(f"  ✓ {png_path.name}: single region @ {depth:.1f}mm")

        # If >50% of sections in this plane show multiple regions, likely floating
        if multi_region_count > total / 2:
            print(f"  → {multi_region_count}/{total} sections show multiple regions (likely floating)")
            floating_detected = True
        else:
            print(f"  → {multi_region_count}/{total} sections show multiple regions (normal, likely holes)")

    if floating_detected:
        print(f"\n⚠ Floating parts detected! Check sections in {outdir}")
        print(f"  Run: python3 {SCRIPT_DIR}/outline.py <section.png> to visualize")
        return 1
    else:
        print(f"\n✓ No floating parts detected")
        return 0


def detect_islands(png_path: Path) -> int:
    """Count isolated white regions in a 2D section PNG.

    Returns the number of disconnected white regions (islands).
    A single connected part should have 1 region; floating parts create multiple.

    Note: holes inside a part are NOT counted as separate regions — we only care
    about whether the white (part) pixels form a single connected blob.
    """
    sys.path.insert(0, str(SCRIPT_DIR))
    from outline import read_png, unfilter  # noqa: E402

    try:
        width, height, raw, ctype = read_png(png_path)
        rows = unfilter(width, height, raw, ctype)
    except Exception:
        return 0  # cannot analyze, assume OK

    # Convert to binary: BLACK (part) vs WHITE (background/holes)
    # In OpenSCAD section renders, the part is BLACK on white background
    # Threshold: pixel is "part" if brightness < 128
    binary = []
    for row in rows:
        binary_row = []
        for i in range(0, len(row), 3):
            r, g, b = row[i], row[i + 1], row[i + 2]
            lum = (r * 299 + g * 587 + b * 114) // 1000
            binary_row.append(1 if lum < 128 else 0)  # BLACK = part
        binary.append(binary_row)

    # Flood fill to count connected part regions (iterative to avoid recursion limit).
    # Tiny blobs (< 0.1% of pixels) are anti-aliasing noise, not real geometry.
    visited = [[False] * width for _ in range(height)]
    min_area = max(4, int(width * height * 0.001))
    regions = 0

    def flood_fill_iterative(start_x, start_y) -> int:
        stack = [(start_x, start_y)]
        area = 0
        while stack:
            x, y = stack.pop()
            if x < 0 or x >= width or y < 0 or y >= height:
                continue
            if visited[y][x] or binary[y][x] == 0:
                continue
            visited[y][x] = True
            area += 1
            # 4-connectivity
            stack.append((x + 1, y))
            stack.append((x - 1, y))
            stack.append((x, y + 1))
            stack.append((x, y - 1))
        return area

    for y in range(height):
        for x in range(width):
            if binary[y][x] == 1 and not visited[y][x]:
                if flood_fill_iterative(x, y) >= min_area:
                    regions += 1

    return regions


if __name__ == "__main__":
    sys.exit(main())
