#!/usr/bin/env python3
"""Check variants.json against vary3d.variants v1. No network."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def fail(msg: str) -> int:
    print(msg, file=sys.stderr)
    return 1


def check_cover(cover, errors: list[str], where: str) -> None:
    if cover is None:
        return
    if not isinstance(cover, str) or not cover or cover.startswith("/") or ".." in cover:
        errors.append(f"{where}: cover must be a relative path without ..")
        return
    if cover.startswith("data:") or ";base64," in cover:
        errors.append(f"{where}: cover must be a file path, not embedded image data")


def check_params(params, errors: list[str], warnings: list[str], where: str) -> None:
    if not isinstance(params, dict):
        errors.append(f"{where}: params must be an object")
        return
    if "__vary" in params:
        errors.append(f"{where}: do not write __vary")
    for key in params:
        if key.startswith("_") and key != "__vary":
            warnings.append(f"{where}: params key {key!r} starts with _ (discouraged)")


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: validate-variants.py packages/<slug>/variants.json", file=sys.stderr)
        return 2
    path = Path(sys.argv[1]).resolve()
    if not path.is_file():
        return fail(f"missing {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return fail(f"invalid JSON: {exc}")
    if not isinstance(data, dict):
        return fail("variants.json must be an object")

    errors: list[str] = []
    warnings: list[str] = []
    if data.get("format") != "vary3d.variants":
        errors.append('format must be "vary3d.variants"')
    if data.get("version") != 1:
        errors.append("version must be 1")
    files = data.get("files") or {}
    package = data.get("package") or []
    has_files = isinstance(files, dict) and any(files.values())
    has_package = isinstance(package, list) and len(package) > 0
    if not has_files and not has_package:
        errors.append("need a non-empty files or package collection")

    if isinstance(files, dict):
        for rel, items in files.items():
            if not isinstance(rel, str) or rel.startswith("/") or ".." in rel:
                errors.append(f"bad files key {rel!r}")
                continue
            if not isinstance(items, list) or len(items) < 1:
                errors.append(f"{rel}: expected a non-empty array")
                continue
            for i, item in enumerate(items):
                where = f"{rel}[{i}]"
                if not isinstance(item, dict):
                    errors.append(f"{where} must be an object")
                    continue
                if not item.get("name"):
                    errors.append(f"{where}: missing name")
                check_params(item.get("params"), errors, warnings, where)
                check_cover(item.get("cover"), errors, where)

    if isinstance(package, list):
        for i, item in enumerate(package):
            where = f"package[{i}]"
            if not isinstance(item, dict):
                errors.append(f"{where} must be an object")
                continue
            if not item.get("name"):
                errors.append(f"{where}: missing name")
            check_params(item.get("params"), errors, warnings, where)
            check_cover(item.get("cover"), errors, where)

    for item in warnings:
        print(f"warning: {item}", file=sys.stderr)
    if errors:
        for item in errors:
            print(item, file=sys.stderr)
        return 1
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
