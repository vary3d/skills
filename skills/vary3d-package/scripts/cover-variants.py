#!/usr/bin/env python3
"""Render one cover per variant in variants.json and write back cover paths.

Also renders a default cover for each extra exportable build root in the
same folder (not params.scad, not module-only helpers). Entry default
remains cover.png from cover.py.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def slugify(name: str) -> str:
    text = name.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text or "variant"


def unique_slug(name: str, used: set[str]) -> str:
    base = slugify(name)
    slug = base
    n = 2
    while slug in used:
        slug = f"{base}-{n}"
        n += 1
    used.add(slug)
    return slug


def iter_items(data: dict):
    files = data.get("files") or {}
    if isinstance(files, dict):
        for rel, items in files.items():
            if not isinstance(items, list):
                continue
            for item in items:
                if isinstance(item, dict):
                    yield rel, item
    package = data.get("package") or []
    if isinstance(package, list):
        for item in package:
            if isinstance(item, dict):
                rel = item.get("previewEntryPath") or "model.scad"
                yield rel, item


SKIP_ROOT_NAMES = frozenset({"params.scad", "geometry.scad"})


def extra_build_roots(model_dir: Path, entry: str) -> list[Path]:
    """Exportable extra entries: package-root .scad except Global and module-only helpers."""
    roots: list[Path] = []
    skip = set(SKIP_ROOT_NAMES)
    skip.add(entry)
    for path in sorted(model_dir.glob("*.scad")):
        if path.name in skip:
            continue
        roots.append(path)
    return roots


def run_cover(cover_py: Path, scad: Path, out: Path, params: dict | None = None) -> int:
    cmd = [sys.executable, str(cover_py), str(scad), str(out)]
    if params:
        cmd += ["--params-json", json.dumps(params, ensure_ascii=False)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr or "")
        sys.stderr.write(proc.stdout or "")
        return proc.returncode or 1
    try:
        print(out.relative_to(scad.parent))
    except ValueError:
        print(out)
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: cover-variants.py packages/<slug>/variants.json", file=sys.stderr)
        return 2
    variants_path = Path(sys.argv[1]).resolve()
    if not variants_path.is_file():
        print(f"missing {variants_path}", file=sys.stderr)
        return 1
    data = json.loads(variants_path.read_text(encoding="utf-8"))
    model_dir = variants_path.parent
    covers_dir = model_dir / "covers"
    covers_dir.mkdir(parents=True, exist_ok=True)
    cover_py = SCRIPT_DIR / "cover.py"
    used: set[str] = set()
    rendered = 0
    entry = "model.scad"
    hint = data.get("modelHint") or {}
    if isinstance(hint, dict) and hint.get("entry"):
        entry = str(hint["entry"])

    for rel, item in iter_items(data):
        name = str(item.get("name") or "variant")
        params = item.get("params") or {}
        if not isinstance(params, dict):
            print(f"invalid variant {name!r}: params must be an object", file=sys.stderr)
            return 1
        scad = model_dir / rel
        if not scad.is_file():
            print(f"missing scad for {name}: {scad}", file=sys.stderr)
            return 1
        slug = unique_slug(name, used)
        out = covers_dir / f"{slug}.png"
        rel_cover = f"covers/{slug}.png"
        code = run_cover(cover_py, scad, out, params)
        if code != 0:
            print(f"cover failed for {name}", file=sys.stderr)
            return code
        item["cover"] = rel_cover
        rendered += 1

    variants_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"{rendered} variant covers → {covers_dir}", file=sys.stderr)

    info_path = model_dir / "info.json"
    if info_path.is_file():
        try:
            info = json.loads(info_path.read_text(encoding="utf-8"))
            if isinstance(info, dict) and info.get("entry"):
                entry = str(info["entry"])
        except json.JSONDecodeError:
            pass

    for root in extra_build_roots(model_dir, entry):
        out = covers_dir / f"{root.stem}.png"
        code = run_cover(cover_py, root, out, None)
        if code != 0:
            print(f"cover failed for build root {root.name}", file=sys.stderr)
            return code
        rendered += 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
