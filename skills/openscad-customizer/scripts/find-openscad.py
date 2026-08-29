#!/usr/bin/env python3
"""OpenSCAD CLI discovery, importable and runnable.

Import:  from find_openscad_lib import find
Run:     python3 find-openscad.py [--ensure]
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

DOWNLOAD = "https://openscad.org/downloads.html"


def is_exe(p: str) -> bool:
    return bool(p) and Path(p).is_file()


def candidates() -> list[str]:
    out: list[str] = []
    env = os.environ.get("OPENSCAD", "").strip()
    if env:
        out.append(env)
        found = shutil.which(env)
        if found:
            out.append(found)
    for name in ("openscad", "openscad.exe", "OpenSCAD", "OpenSCAD.exe"):
        found = shutil.which(name)
        if found:
            out.append(found)
    if sys.platform == "darwin":
        out.extend(
            [
                "/opt/homebrew/bin/openscad",
                "/usr/local/bin/openscad",
                "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD",
            ]
        )
        apps = Path("/Applications")
        if apps.is_dir():
            for app in apps.glob("OpenSCAD*.app"):
                out.append(str(app / "Contents/MacOS/OpenSCAD"))
        portable = Path.home() / "Applications" / "OpenSCAD-portable"
        if portable.is_dir():
            for app in portable.glob("OpenSCAD*.app"):
                out.append(str(app / "Contents/MacOS/OpenSCAD"))
    elif sys.platform.startswith("linux"):
        out.extend(["/usr/bin/openscad", "/usr/local/bin/openscad", "/snap/bin/openscad"])
        portable = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "openscad-portable"
        if portable.is_dir():
            out.extend(str(p) for p in portable.glob("*.AppImage"))
            out.extend(str(p) for p in portable.rglob("openscad") if p.is_file())
    elif sys.platform == "win32":
        pf = os.environ.get("ProgramFiles", r"C:\Program Files")
        pf86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        local = os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData/Local"))
        for base in (pf, pf86, local):
            b = Path(base)
            for pat in ("OpenSCAD/openscad.exe", "OpenSCAD*/openscad.exe", "Programs/OpenSCAD/openscad.exe"):
                if b.is_dir():
                    out.extend(str(p) for p in b.glob(pat))
        portable = Path(local) / "OpenSCAD-portable"
        if portable.is_dir():
            out.extend(str(p) for p in portable.rglob("openscad.exe"))
    return out


def find() -> str | None:
    seen: set[str] = set()
    for c in candidates():
        try:
            rp = str(Path(c).resolve())
        except OSError:
            rp = c
        if rp.lower() in seen:
            continue
        seen.add(rp.lower())
        if is_exe(c):
            return rp
    return None


def hints() -> None:
    e = lambda *a: print(*a, file=sys.stderr)
    e(f"openscad CLI not found. Install from {DOWNLOAD} or set OPENSCAD to the executable.")
    if sys.platform == "darwin":
        e("macOS (Homebrew snapshot cask, or a portable dmg without brew):")
        e("  brew install --cask openscad@snapshot")
    elif sys.platform.startswith("linux"):
        if shutil.which("apt-get"):
            e("Debian/Ubuntu:  apt-get update && apt-get install -y openscad")
            e("(that package install may need administrator rights on this machine.)")
        elif shutil.which("dnf"):
            e("Fedora:  dnf install -y openscad")
            e("(that package install may need administrator rights on this machine.)")
        elif shutil.which("pacman"):
            e("Arch:  pacman -Sy openscad")
            e("(that package install may need administrator rights on this machine.)")
        else:
            e("Linux: distro package openscad, or a portable AppImage — re-run with --ensure.")
    elif sys.platform == "win32":
        e("Windows: winget install OpenSCAD.OpenSCAD  /  choco install openscad,")
        e("or a portable zip (no admin) — re-run with --ensure after the user agrees.")
        e("Manual: install from the site, then set OPENSCAD to the full path of openscad.exe")
    e("After the user agrees, re-run with --ensure (OPENSCAD_INSTALL=1 in non-interactive shells)")
    e("to install a portable build into the user directory (no administrator rights).")


def run(cmd: list[str]) -> int:
    print("+", " ".join(cmd), file=sys.stderr)
    return subprocess.call(cmd)


def install() -> int:
    # Portable user-dir install only: no elevation, no brew/winget/apt.
    print("Installing a portable OpenSCAD build into the user directory (no admin).", file=sys.stderr)
    return _portable()


def _portable() -> int:
    script = Path(__file__).resolve().parent / "install-portable.py"
    return run([sys.executable, str(script)])


def main() -> int:
    ensure = "--ensure" in sys.argv[1:]
    found = find()
    if found:
        print(found)
        return 0
    if not ensure:
        hints()
        return 1
    if os.environ.get("OPENSCAD_INSTALL") != "1" and not sys.stdin.isatty():
        print("Refusing to install from a non-interactive session.", file=sys.stderr)
        hints()
        return 1
    if install() != 0:
        return 1
    found = find()
    if found:
        print(found)
        return 0
    print("OpenSCAD installed but still not found. Set OPENSCAD to the executable.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
