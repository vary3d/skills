#!/usr/bin/env python3
"""Check info.json against vary3d.info v1. No network."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CATEGORIES = {
    "practical_gadgets",
    "maker_kits",
    "mechanical_structures",
    "educational_models",
    "interactive_toys",
    "general_assets",
}
REQUIRED = (
    "format",
    "version",
    "slug",
    "name",
    "description",
    "category",
    "license",
    "originType",
    "engineType",
    "entry",
)
FORBIDDEN_EXACT = {
    "id",
    "userId",
    "status",
    "visibility",
    "engineVersion",
}
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def fail(msg: str) -> int:
    print(msg, file=sys.stderr)
    return 1


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: validate-info.py packages/<slug>/info.json", file=sys.stderr)
        return 2
    path = Path(sys.argv[1]).resolve()
    if not path.is_file():
        return fail(f"missing {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return fail(f"invalid JSON: {exc}")
    if not isinstance(data, dict):
        return fail("info.json must be an object")

    errors: list[str] = []
    if data.get("format") != "vary3d.info":
        errors.append('format must be "vary3d.info"')
    if data.get("version") != 1:
        errors.append("version must be 1")
    for key in REQUIRED:
        if key not in data:
            errors.append(f"missing {key}")

    slug = data.get("slug")
    if isinstance(slug, str):
        if not SLUG_RE.match(slug):
            errors.append("slug must be lowercase kebab-case ASCII")
        folder = path.parent.name
        if folder != slug:
            errors.append(f"slug {slug!r} must match folder name {folder!r}")
    if data.get("category") not in CATEGORIES:
        errors.append("category is not one of the six spec values")
    if data.get("engineType") != "openscad":
        errors.append('engineType must be "openscad"')
    origin = data.get("originType")
    if origin not in (None, "original", "fork"):
        errors.append('originType must be "original" or "fork"')
    if origin == "fork" and not data.get("sourceUrl") and not data.get("originalAuthor"):
        errors.append("fork: set sourceUrl and/or originalAuthor")

    license_ = data.get("license")
    if isinstance(license_, str) and re.search(r"(?:^|-)ND(?:-|$)", license_.upper()):
        errors.append("license must not be ND (no-derivatives)")

    for key in data:
        if key in FORBIDDEN_EXACT:
            errors.append(f"do not write server field {key}")
        if key.endswith("I18n") or "R2" in key:
            errors.append(f"do not write {key}")
        if key.startswith("__"):
            errors.append(f"do not write {key}")

    tags = data.get("tags")
    if tags is not None:
        if not isinstance(tags, list) or len(tags) > 5:
            errors.append("tags must be an array of at most 5 strings")
        elif any(not isinstance(t, str) for t in tags):
            errors.append("tags must be strings")

    name = data.get("name")
    if isinstance(name, str) and len(name) > 100:
        errors.append("name longer than 100 characters")
    desc = data.get("description")
    if isinstance(desc, str) and len(desc) > 800:
        errors.append("description longer than 800 characters")

    if errors:
        for item in errors:
            print(item, file=sys.stderr)
        return 1
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
