#!/usr/bin/env python3
"""Portable OpenSCAD install: download the official archive into the user dir.

Used by find-openscad.py --ensure. Downloads the official archive into the
user dir (no administrator rights). Verifies the official sha256 before extracting.

  python3 install-portable.py            # install for this platform
  python3 install-portable.py --print    # print the URL + target, do not download
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

VERSION = "2021.01"
BASE = "https://files.openscad.org"

# Official sha256 from files.openscad.org/<file>.sha256
ARTIFACTS = {
    ("win32", "amd64"): (
        f"{BASE}/OpenSCAD-{VERSION}-x86-64.zip",
        "fb0caabf5bbc89f8f2f80c10b79ae64d697aaff6efd58b2756f5d6270edb7ba7",
    ),
    # No unpinned 32-bit zip; that platform installs from the OpenSCAD site.
    ("darwin", "universal"): (
        f"{BASE}/OpenSCAD-{VERSION}.dmg",
        "4e4568e19992636ba497c04bc2238399c92314fcb7bf75dc3632aa623ca3635e",
    ),
    ("linux", "amd64"): (
        f"{BASE}/OpenSCAD-{VERSION}-x86_64.AppImage",
        "f758528f2cd213f773c7a105fb63bf3b45bf754b0f586fbb7c9cd653ffcd0882",
    ),
    ("linux", "arm64"): (
        f"{BASE}/OpenSCAD-{VERSION}-aarch64.AppImage",
        "518b7e1671b3ecb7e9da81a4df47ecf9dc9c7def97bce6dc0dcd553795b89da9",
    ),
}


def platform_key() -> tuple[str, str] | None:
    import platform

    mach = platform.machine().lower()
    if sys.platform == "win32":
        return ("win32", "amd64") if ("64" in mach or mach in ("amd64", "x86_64")) else ("win32", "x86")
    if sys.platform == "darwin":
        return ("darwin", "universal")
    if sys.platform.startswith("linux"):
        if mach in ("x86_64", "amd64"):
            return ("linux", "amd64")
        if mach in ("aarch64", "arm64"):
            return ("linux", "arm64")
    return None


def install_dir() -> Path:
    if sys.platform == "win32":
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local")) / "OpenSCAD-portable"
    if sys.platform == "darwin":
        return Path.home() / "Applications" / "OpenSCAD-portable"
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "openscad-portable"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: Path) -> None:
    print(f"Downloading {url}", file=sys.stderr)
    if shutil.which("curl"):
        rc = subprocess.call(["curl", "-fSL", "--progress-bar", "-o", str(dest), url])
        if rc != 0:
            raise OSError(f"curl exit {rc}")
        return
    with urllib.request.urlopen(url) as r, dest.open("wb") as f:
        shutil.copyfileobj(r, f)


def find_exe(root: Path) -> Path | None:
    if sys.platform == "win32":
        for p in root.rglob("openscad.exe"):
            return p
    elif sys.platform == "darwin":
        for p in root.rglob("OpenSCAD*.app/Contents/MacOS/OpenSCAD"):
            return p
    else:
        for p in root.rglob("*.AppImage"):
            return p
        for p in root.rglob("openscad"):
            if p.is_file():
                return p
    return None


def install() -> int:
    key = platform_key()
    if key is None or key not in ARTIFACTS:
        print(f"No portable build for {sys.platform}. Install from https://openscad.org/downloads.html", file=sys.stderr)
        return 1
    url, want = ARTIFACTS[key]
    dest_dir = install_dir()
    dest_dir.mkdir(parents=True, exist_ok=True)
    archive = dest_dir / Path(url).name

    if not archive.is_file():
        try:
            download(url, archive)
        except Exception as exc:  # noqa: BLE001
            print(f"download failed: {exc}", file=sys.stderr)
            return 1
    if want:
        got = sha256(archive)
        if got != want:
            archive.unlink(missing_ok=True)
            print(f"sha256 mismatch: got {got}, want {want}", file=sys.stderr)
            return 1

    print(f"Extracting to {dest_dir}", file=sys.stderr)
    if archive.suffix == ".zip":
        with zipfile.ZipFile(archive) as z:
            z.extractall(dest_dir)
    elif archive.suffix == ".dmg":
        if sys.platform != "darwin":
            print("dmg only on macOS", file=sys.stderr)
            return 1
        mount = subprocess.run(["hdiutil", "attach", "-nobrowse", "-readonly", str(archive)], capture_output=True, text=True)
        if mount.returncode != 0:
            print(mount.stderr, file=sys.stderr)
            return 1
        vol = None
        for line in mount.stdout.splitlines():
            if "/Volumes/" in line:
                vol = line.split("\t")[-1].strip()
        if not vol:
            print("could not mount dmg", file=sys.stderr)
            return 1
        try:
            for app in Path(vol).glob("OpenSCAD*.app"):
                target = dest_dir / app.name
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(app, target)
        finally:
            subprocess.run(["hdiutil", "detach", vol], capture_output=True)
    elif archive.suffix == ".AppImage":
        target = dest_dir / archive.name
        shutil.copy2(archive, target)
        target.chmod(0o755)
    else:
        print(f"unsupported archive {archive}", file=sys.stderr)
        return 1

    exe = find_exe(dest_dir)
    if not exe:
        print("installed but could not locate the OpenSCAD executable", file=sys.stderr)
        return 1
    print(exe)
    return 0


def main() -> int:
    if "--print" in sys.argv:
        key = platform_key()
        if key and key in ARTIFACTS:
            print(ARTIFACTS[key][0])
            print(install_dir())
        return 0
    return install()


if __name__ == "__main__":
    sys.exit(main())
