#!/usr/bin/env python3
"""Optional skill-version soft check. Not a gate; never auto-updates.

Compares the local VERSION file to the published one-line VERSION.
Does not fetch SKILL.md. Does not auto-update.

  python3 check-skill-version.py            # check this skill
  python3 check-skill-version.py --json     # machine-readable
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO = "vary3d/skills"
REF = os.environ.get("VARY3D_SKILLS_REF", "main")
RAW = f"https://raw.githubusercontent.com/{REPO}/{REF}/skills"

VERSION_RE = re.compile(r'^\s*version:\s*["\']?([0-9][0-9A-Za-z.\-+]*)["\']?\s*$', re.M)


def _first_line(text: str) -> str | None:
    for line in text.splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            return s
    return None


def local_version(skill_root: Path) -> str | None:
    vf = skill_root / "VERSION"
    if vf.is_file():
        got = _first_line(vf.read_text(encoding="utf-8"))
        if got:
            return got
    # Older copies without VERSION: fall back to SKILL.md frontmatter.
    md = skill_root / "SKILL.md"
    if md.is_file():
        m = VERSION_RE.search(md.read_text(encoding="utf-8"))
        if m:
            return m.group(1)
    return None


def remote_version(skill_name: str) -> str | None:
    url = f"{RAW}/{skill_name}/VERSION"
    try:
        # Anonymous one-line VERSION fetch; no credentials.
        with urllib.request.urlopen(url, timeout=15) as r:
            text = r.read().decode("utf-8", "replace")
        got = _first_line(text)
        if got:
            return got
    except Exception:
        pass
    # If anonymous raw fails, try gh. VERSION only — never SKILL.md.
    if shutil.which("gh"):
        proc = subprocess.run(
            [
                "gh",
                "api",
                f"repos/{REPO}/contents/skills/{skill_name}/VERSION?ref={REF}",
                "-H",
                "Accept: application/vnd.github.raw",
            ],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if proc.returncode == 0 and proc.stdout:
            return _first_line(proc.stdout)
    return None


def parse_ver(v: str) -> tuple:
    parts = []
    for piece in re.split(r"[.\-+]", v):
        parts.append((0, int(piece)) if piece.isdigit() else (1, piece))
    return tuple(parts)


def main() -> int:
    as_json = "--json" in sys.argv
    skill_root = Path(__file__).resolve().parent.parent
    skill_name = skill_root.name

    local = local_version(skill_root)
    remote = remote_version(skill_name)

    out = {
        "skill": skill_name,
        "local_version": local,
        "remote_version": remote,
        "remote_ref": REF,
        "update_available": False,
        "update_command": f"npx skills update {skill_name}",
    }

    if local is None:
        out["status"] = "no-local-version"
    elif remote is None:
        out["status"] = "remote-unreachable"
    else:
        out["update_available"] = parse_ver(remote) > parse_ver(local)
        out["status"] = "update-available" if out["update_available"] else "current"

    if as_json:
        print(json.dumps(out, ensure_ascii=False))
        return 0

    if out["status"] == "no-local-version":
        print(f"warning: no VERSION in {skill_root}", file=sys.stderr)
        return 0
    if out["status"] == "remote-unreachable":
        print("note: version check unreachable (offline or auth required); skipping", file=sys.stderr)
        return 0
    if out["update_available"]:
        print(f"{skill_name}: local {local} < remote {remote}")
        print(f"update: {out['update_command']}")
    else:
        print(f"{skill_name}: current ({local})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
