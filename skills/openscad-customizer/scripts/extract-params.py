#!/usr/bin/env python3
"""Extract top-level Customizer parameters (before the first module/function)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

GROUP = re.compile(r"^/\*\s*\[([^\]]+)\]\s*\*/", re.M)
DESC = re.compile(r"^//\s*(.*)$")
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
    """Return (name, name_offset, raw_value, trailing_comment) or None.

    `semi` is the offset of the closing semicolon inside `stmt`, so string
    values containing `;` are never mistaken for the terminator. A statement
    can start with `use` / `include` lines (no semicolon of their own), so
    scan line by line until the first real assignment."""
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
            name = m.group(1)
            value = stmt[m.end() : semi].strip()
            trail = stmt[semi + 1 :].strip()
            return name, m.start(1), value, trail
        nl = stmt.find("\n", pos)
        if nl == -1 or nl >= semi:
            return None
        pos = nl + 1
    return None


def _parse_value(raw: str):
    text = raw.strip()
    if text in ("true", "false"):
        return True if text == "true" else False
    if len(text) >= 2 and (
        (text.startswith('"') and text.endswith('"'))
        or (text.startswith("'") and text.endswith("'"))
    ):
        return text[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    try:
        if "." in text or "e" in text.lower():
            return float(text)
        return int(text)
    except ValueError:
        return text


SHADOW_LINE = re.compile(r"[ \t]*([A-Za-z_][A-Za-z0-9_]*)[ \t]*=")


def shadowed_assignments(source: str, head_len: int, rest: str) -> list[str]:
    """Assignments at top level after the first module/function: never knobs.
    Bracket depth decides top-level, so indented in-module locals do not
    false-positive and unindented ones still do."""
    names: list[str] = []
    depth = 0
    in_str = esc = in_block = False
    for line in rest.splitlines():
        if depth == 0 and not in_block:
            m = SHADOW_LINE.match(line)
            if m:
                names.append(m.group(1))
        i = 0
        in_line = False
        while i < len(line):
            c = line[i]
            nxt = line[i + 1] if i + 1 < len(line) else ""
            if in_line:
                break
            if in_block:
                if c == "*" and nxt == "/":
                    in_block = False
                    i += 2
                    continue
                i += 1
                continue
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
                i += 1
                continue
            if c == "/" and nxt == "/":
                break
            if c == "/" and nxt == "*":
                in_block = True
                i += 2
                continue
            if c == '"':
                in_str = True
            elif c in "([{":
                depth += 1
            elif c in ")]}":
                depth = max(0, depth - 1)
            i += 1
    return names


def extract(source: str) -> tuple[list[dict], list[str]]:
    split = re.split(r"^((?:module|function)\s)", source, maxsplit=1, flags=re.M)
    head = split[0]
    rest = "".join(split[1:]) if len(split) > 1 else ""
    groups = [(0, "")]
    for match in GROUP.finditer(head):
        groups.append((match.start(), match.group(1).strip()))

    params: list[dict] = []
    for stmt, start, semi in iter_statements(head):
        parsed = parse_assignment(stmt, semi)
        if not parsed:
            continue
        name, name_off, value, trail = parsed
        if re.match(r"^[A-Za-z_]", value) and value not in ("true", "false"):
            continue
        pos = start + name_off
        group = ""
        for gstart, label in groups:
            if gstart <= pos:
                group = label
        above = head[:pos].rstrip()
        last_line = above.split("\n")[-1] if above else ""
        desc_match = DESC.match(last_line.strip())
        description = desc_match.group(1).strip() if desc_match else ""
        hint = trail[2:].strip() if trail.startswith("//") else ""
        params.append(
            {
                "name": name,
                "value": _parse_value(value),
                "group": group,
                "description": description,
                "hint": hint,
            }
        )
    warnings = shadowed_assignments(source, len(head), rest)
    return params, warnings


VISIBLE_SIMPLE_MAX = 6
VISIBLE_COMPLEX_MAX = 8

# Visible names that are print/cradle internals unless the user asked to retune them.
DENY_VISIBLE_NAMES = frozenset(
    {
        "gap",
        "fit_gap",
        "motion_gap",
        "bed_chamfer",
        "reveal_ratio",
        "label_size",
        "arm_w",
        "plate_t",
        "lip_h",
        "lip_w",
        "chamfer",
        "corner_radius",
        "fold_angle",
        "tilt_deg",
        "pin_d",
    }
)

DEBUG_PART_TOKENS = frozenset(
    {"assembly", "coin", "section", "interference"}
)


def is_hidden_group(group: str | None) -> bool:
    return (group or "").strip().lower() == "hidden"


def split_visible(params: list[dict]) -> tuple[list[dict], list[dict]]:
    vis, hid = [], []
    for p in params:
        (hid if is_hidden_group(p.get("group")) else vis).append(p)
    return vis, hid


def is_literal_value(raw: str) -> bool:
    """True if OpenSCAD Customizer can treat this as a slider default."""
    text = raw.strip()
    if text in ("true", "false"):
        return True
    if len(text) >= 2 and (
        (text[0] == text[-1] == '"') or (text[0] == text[-1] == "'")
    ):
        return True
    if text.startswith("["):
        return not re.search(r"[A-Za-z_]", text)
    try:
        if "." in text or "e" in text.lower():
            float(text)
        else:
            int(text)
        return True
    except ValueError:
        return False


def file_scope_derived(head: str) -> list[str]:
    """Top-level assignments that are expressions, not Customizer literals."""
    names: list[str] = []
    for stmt, _start, semi in iter_statements(head):
        parsed = parse_assignment(stmt, semi)
        if not parsed:
            continue
        name, _off, value, _trail = parsed
        if name.startswith("$"):
            continue
        if not is_literal_value(value):
            names.append(name)
    return names


def enum_tokens(param: dict) -> list[str]:
    hint = param.get("hint") or ""
    match = re.search(r"\[([^\]]+)\]", hint)
    if match:
        tokens = []
        for item in match.group(1).split(","):
            item = item.strip()
            if not item:
                continue
            tokens.append(item.split(":", 1)[0].strip().strip("\"'"))
        return tokens
    value = param.get("value")
    if isinstance(value, str) and value:
        return [value]
    return []


def style_warnings(params: list[dict], head: str) -> list[str]:
    out: list[str] = []
    vis, _hid = split_visible(params)
    n = len(vis)
    if n > VISIBLE_COMPLEX_MAX:
        out.append(
            f"visible knobs {n} > {VISIBLE_COMPLEX_MAX} (complex ceiling); "
            "move internals to Hidden or derive them in the module"
        )
    elif n > VISIBLE_SIMPLE_MAX:
        out.append(
            f"visible knobs {n} > {VISIBLE_SIMPLE_MAX} (simple-part ceiling); "
            f"complex parts may go to {VISIBLE_COMPLEX_MAX} including part and one color"
        )
    colors = [p for p in vis if str(p.get("name", "")).endswith("_color")]
    if len(colors) > 1:
        out.append(
            f"{len(colors)} visible *_color knobs; default is one color "
            "(put extras in Hidden unless the user asked for two-color / dual material)"
        )
    denied = [p["name"] for p in vis if p["name"] in DENY_VISIBLE_NAMES]
    if denied:
        out.append(
            "visible deny-list knobs "
            + ", ".join(denied)
            + "; Hidden or derive in the module unless the user asked to retune them"
        )
    derived = file_scope_derived(head)
    if derived:
        shown = ", ".join(derived[:12])
        extra = "" if len(derived) <= 12 else f" (+{len(derived) - 12} more)"
        out.append(
            f"derived at file scope ({shown}{extra}); move inside the module"
        )
    seen_groups: set[str] = set()
    for p in params:
        group = (p.get("group") or "").strip()
        if not group or group in seen_groups:
            continue
        seen_groups.add(group)
        if re.search(r"[^\x00-\x7F]", group):
            out.append(
                f"group [{group}] is not English; Customizer groups default to English"
            )
    for p in params:
        if p.get("name") != "part":
            continue
        tokens = {t.lower() for t in enum_tokens(p)}
        bad = sorted(tokens & DEBUG_PART_TOKENS)
        if bad:
            out.append(
                "part enum includes debug tokens "
                + ", ".join(bad)
                + "; one-piece files must not Customizer-assign part for a ghost mate / section / interference"
            )
        break
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Extract OpenSCAD Customizer parameters")
    p.add_argument("scad")
    args = p.parse_args()
    path = Path(args.scad)
    source = path.read_text(encoding="utf-8")
    params, shadowed = extract(source)
    split = re.split(r"^((?:module|function)\s)", source, maxsplit=1, flags=re.M)
    head = split[0]
    vis, hid = split_visible(params)
    warnings = [
        f"{w}: assignment after the first module/function is not a Customizer knob; move it above the first module"
        for w in shadowed
    ]
    warnings.extend(style_warnings(params, head))
    out: dict = {
        "file": str(path),
        "visible_count": len(vis),
        "hidden_count": len(hid),
        "params": params,
    }
    if warnings:
        out["warnings"] = warnings
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
