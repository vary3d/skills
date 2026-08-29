#!/usr/bin/env python3
"""Override top-level Customizer assignments and write a temp .scad.

Only the region before the first module/function is touched. Keys that do
not match any top-level assignment are an error by default (they are almost
always typos in variant params); pass --allow-missing to prepend them instead.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

NAME_EQ = re.compile(r"\s*([A-Za-z_][A-Za-z0-9_]*)\s*=")


def iter_statements(text: str):
    """Yield (statement, start_offset, semi_offset) for each statement closed
    by a semicolon at bracket depth 0, outside strings and comments."""
    i, n = 0, len(text)
    start = 0
    depth = 0
    in_str = esc = in_block = in_line = False
    while i < n:
        c = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if in_line:
            if c == "\n":
                in_line = False
        elif in_block:
            if c == "*" and nxt == "/":
                in_block = False
                i += 1
        elif in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        else:
            if c == "/" and nxt == "/":
                in_line = True
                i += 1
            elif c == "/" and nxt == "*":
                in_block = True
                i += 1
            elif c == '"':
                in_str = True
            elif c in "([{":
                depth += 1
            elif c in ")]}":
                depth = max(0, depth - 1)
            elif c == ";" and depth == 0:
                semi = i
                end = i + 1
                j = end
                while j < n and text[j] in " \t":
                    j += 1
                if text[j : j + 2] == "//":
                    nl = text.find("\n", j)
                    end = n if nl == -1 else nl
                yield text[start:end], start, semi - start
                start = end
        i += 1


def parse_assignment(stmt: str, semi: int):
    """Return (name, name_offset) or None. `semi` marks the closing ';'.

    A statement can start with `use` / `include` lines (no semicolon of
    their own), so scan line by line until the first real assignment."""
    pos = 0
    while pos < semi:
        ws = re.match(r"\s+", stmt[pos:])
        if ws:
            pos += ws.end()
            if pos >= semi:
                break
        if stmt.startswith("//", pos):
            nl = stmt.find("\n", pos)
            if nl == -1 or nl >= semi:
                return None
            pos = nl + 1
            continue
        if stmt.startswith("/*", pos):
            close = stmt.find("*/", pos + 2)
            if close == -1 or close >= semi:
                return None
            pos = close + 2
            continue
        m = NAME_EQ.match(stmt, pos)
        if m and m.end() <= semi:
            return m.group(1), m.start(1)
        nl = stmt.find("\n", pos)
        if nl == -1 or nl >= semi:
            return None
        pos = nl + 1
    return None


def scad_literal(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return repr(value)
    if isinstance(value, list):
        return "[" + ", ".join(scad_literal(v) for v in value) + "]"
    return json.dumps(value)


def parse_set(raw: str) -> tuple[str, object]:
    if "=" not in raw:
        raise ValueError(f"expected name=value, got {raw!r}")
    name, text = raw.split("=", 1)
    name = name.strip()
    text = text.strip()
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
        raise ValueError(f"bad param name {name!r}")
    if text in ("true", "false"):
        return name, text == "true"
    if (text.startswith('"') and text.endswith('"')) or (
        text.startswith("'") and text.endswith("'")
    ):
        return name, text[1:-1]
    try:
        if "." in text or "e" in text.lower():
            return name, float(text)
        return name, int(text)
    except ValueError:
        return name, text


def apply_overrides(source: str, overrides: dict, allow_missing: bool) -> str:
    split = re.split(r"^((?:module|function)\s)", source, maxsplit=1, flags=re.M)
    head = split[0]
    rest = "".join(split[1:]) if len(split) > 1 else ""
    pending = dict(overrides)

    out: list[str] = []
    cursor = 0
    for stmt, start, semi in iter_statements(head):
        out.append(head[cursor:start])
        cursor = start + len(stmt)
        parsed = parse_assignment(stmt, semi)
        if parsed and parsed[0] in pending:
            name, name_off = parsed
            lit = scad_literal(pending.pop(name))
            trail = stmt[semi + 1 :].strip()
            stmt = f"{stmt[:name_off]}{name} = {lit};"
            if trail:
                stmt += f" {trail}"
        out.append(stmt)
    out.append(head[cursor:])
    new_head = "".join(out)

    if pending:
        missing = ", ".join(sorted(pending))
        if not allow_missing:
            raise KeyError(missing)
        print(f"warning: no top-level assignment for: {missing}; prepending", file=sys.stderr)
        extra = "".join(f"{k} = {scad_literal(v)};\n" for k, v in pending.items())
        new_head = extra + new_head
    return new_head + rest


def main() -> int:
    p = argparse.ArgumentParser(description="Override OpenSCAD Customizer assignments")
    p.add_argument("scad")
    p.add_argument("-o", "--out", required=True)
    p.add_argument("--set", action="append", default=[], metavar="NAME=VALUE")
    p.add_argument("--params-json", default="", help="JSON object of overrides")
    p.add_argument(
        "--allow-missing",
        action="store_true",
        help="Prepend keys that match no top-level assignment instead of failing",
    )
    args = p.parse_args()

    overrides: dict = {}
    if args.params_json:
        loaded = json.loads(args.params_json)
        if not isinstance(loaded, dict):
            print("params-json must be an object", file=sys.stderr)
            return 2
        overrides.update(loaded)
    for item in args.set:
        name, value = parse_set(item)
        overrides[name] = value

    path = Path(args.scad)
    try:
        text = apply_overrides(path.read_text(encoding="utf-8"), overrides, args.allow_missing)
    except KeyError as exc:
        print(
            f"no top-level assignment for: {exc.args[0]} in {path} (typo in variant params?)",
            file=sys.stderr,
        )
        return 3
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
