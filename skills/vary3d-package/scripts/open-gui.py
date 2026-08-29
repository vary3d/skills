#!/usr/bin/env python3
"""Open a .scad in the desktop OpenSCAD app so the user can inspect it.

  python3 open-gui.py model.scad

Uses the CLI found by find-openscad.py (which may be a portable install).
On macOS prefers `open -a` so the GUI app launches even when only the
/Applications bundle exists.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import find_openscad_lib  # noqa: E402


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: open-gui.py model.scad", file=sys.stderr)
        return 2
    scad = Path(sys.argv[1]).resolve()
    if not scad.is_file():
        print(f"missing {scad}", file=sys.stderr)
        return 1

    if sys.platform == "darwin":
        # `open -a` launches the GUI app bundle; works even if the CLI is a
        # bare binary that would otherwise run headless.
        app = None
        exe = find_openscad_lib.find()
        if exe and ".app" in exe:
            app = exe.split(".app", 1)[0] + ".app"
        cmd = ["open"]
        if app:
            cmd += ["-a", app]
        else:
            cmd += ["-a", "OpenSCAD"]
        cmd.append(str(scad))
    else:
        exe = find_openscad_lib.find()
        if not exe:
            print("openscad not found. Run find-openscad.py first.", file=sys.stderr)
            return 1
        if sys.platform == "win32":
            # Detach so the CLI returns while the GUI stays open.
            subprocess.Popen([exe, str(scad)], creationflags=getattr(subprocess, "DETACHED_PROCESS", 0))
            print(scad)
            return 0
        cmd = [exe, str(scad)]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr or proc.stdout or "")
        return proc.returncode or 1
    print(scad)
    return 0


if __name__ == "__main__":
    sys.exit(main())
