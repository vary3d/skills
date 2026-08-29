#!/usr/bin/env python3
"""Render one cover per variant in variants.json and write back cover paths."""

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
        cmd = [
            sys.executable,
            str(cover_py),
            str(scad),
            str(out),
            "--params-json",
            json.dumps(params, ensure_ascii=False),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            sys.stderr.write(proc.stderr or "")
            sys.stderr.write(proc.stdout or "")
            print(f"cover failed for {name}", file=sys.stderr)
            return proc.returncode or 1
        item["cover"] = rel_cover
        print(rel_cover)
        rendered += 1

    variants_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"{rendered} variant covers → {covers_dir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
