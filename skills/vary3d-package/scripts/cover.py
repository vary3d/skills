#!/usr/bin/env python3
"""Render a 4:3 listing cover. Cross-platform, no bash.

Usage:
  cover.py model.scad [out.png]
  cover.py model.scad [out.png] --set name=value --set x=y
  cover.py model.scad [out.png] --params-json '{"flange_length":60}'

Overrides are OpenSCAD -D on the entry file (end-of-file assignment), so
they apply to names defined in included params.scad. Do not rewrite the
entry source: that cannot see Global keys and prepending loses to include.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


override_params = _load("override_params", "override-params.py")
preview = _load("preview", "preview.py")


def d_pairs_from_values(values: dict) -> list[str]:
    extra: list[str] = []
    for name, value in values.items():
        extra += ["-D", f"{name}={override_params.scad_literal(value)}"]
    return extra


def parse_overrides(sets: list[str], params_json: str) -> dict:
    overrides: dict = {}
    if params_json:
        loaded = json.loads(params_json)
        if not isinstance(loaded, dict):
            raise ValueError("params-json must be an object")
        overrides.update(loaded)
    for item in sets:
        name, value = override_params.parse_set(item)
        overrides[name] = value
    return overrides


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

    extra: list[str] = []
    if sets or params_json:
        try:
            extra = d_pairs_from_values(parse_overrides(sets, params_json))
        except (json.JSONDecodeError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 2

    return preview.render(scad, out, "cover", extra=extra or None)


if __name__ == "__main__":
    sys.exit(main())
