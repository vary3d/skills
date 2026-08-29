#!/usr/bin/env python3
"""Measure an STL bounding box. No third-party dependencies."""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path


def _cross(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _dot(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _iter_binary_tris(data: bytes, count: int):
    off = 84
    for _ in range(count):
        # 3 normal + 9 vertex floats, little-endian
        nums = struct.unpack_from("<12f", data, off)
        yield (nums[3:6], nums[6:9], nums[9:12])
        off += 50


def _iter_ascii_tris(text: str):
    verts: list[tuple[float, float, float]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if line.lower().startswith("vertex"):
            parts = line.split()
            verts.append((float(parts[1]), float(parts[2]), float(parts[3])))
            if len(verts) == 3:
                yield tuple(verts)
                verts = []


def measure_stl(path: Path) -> dict:
    data = path.read_bytes()
    if len(data) < 84:
        raise ValueError(f"STL too small: {path}")

    n_bin = struct.unpack_from("<I", data, 80)[0]
    # ASCII starts with "solid" and mentions "facet" early; otherwise verify binary by declared triangle count
    looks_ascii = data[:5].lower() == b"solid" and b"facet" in data[:512].lower()
    binary = not looks_ascii and n_bin > 0 and len(data) >= 84 + n_bin * 50

    xmin = ymin = zmin = float("inf")
    xmax = ymax = zmax = float("-inf")
    volume = 0.0
    triangles = 0

    tris = _iter_binary_tris(data, n_bin) if binary else _iter_ascii_tris(data.decode("utf-8", "replace"))
    all_tris = []
    for v1, v2, v3 in tris:
        triangles += 1
        all_tris.append((v1, v2, v3))
        for x, y, z in (v1, v2, v3):
            xmin, xmax = min(xmin, x), max(xmax, x)
            ymin, ymax = min(ymin, y), max(ymax, y)
            zmin, zmax = min(zmin, z), max(zmax, z)
        volume += _dot(v1, _cross(v2, v3)) / 6.0

    if triangles == 0:
        raise ValueError(f"empty mesh: {path}")

    size = [xmax - xmin, ymax - ymin, zmax - zmin]
    return {
        "path": str(path),
        "format": "binary" if binary else "ascii",
        "triangles": triangles,
        "min": [xmin, ymin, zmin],
        "max": [xmax, ymax, zmax],
        "size": size,
        "volume_mm3": abs(volume),
        "_tris": all_tris,  # internal: for body counting
    }


def count_bodies(tris: list[tuple]) -> int:
    """Count disconnected solid bodies using triangle adjacency.

    Two triangles are connected if they share at least one vertex (within epsilon).
    Uses union-find to group triangles into bodies.
    """
    if not tris:
        return 0

    # Snap vertices to a 0.001 mm grid to avoid float noise
    def quantize(v):
        return (round(v[0], 3), round(v[1], 3), round(v[2], 3))

    # Map quantized vertices to triangle indices
    vert_to_tris = {}
    for i, (v1, v2, v3) in enumerate(tris):
        for v in (v1, v2, v3):
            qv = quantize(v)
            if qv not in vert_to_tris:
                vert_to_tris[qv] = []
            vert_to_tris[qv].append(i)

    # Union-find
    parent = list(range(len(tris)))

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    # Merge triangles that share a vertex
    for tri_indices in vert_to_tris.values():
        for i in range(1, len(tri_indices)):
            union(tri_indices[0], tri_indices[i])

    # Count connected bodies
    return len({find(i) for i in range(len(tris))})


def compare_expect(measured: dict, expect: list[float], tol: float) -> dict:
    size = measured["size"]
    delta = [abs(size[i] - expect[i]) for i in range(3)]
    ok = all(d <= tol for d in delta)
    return {"expect": expect, "delta": delta, "tol": tol, "bbox_ok": ok}


def main() -> int:
    p = argparse.ArgumentParser(description="Measure an STL bounding box")
    p.add_argument("stl")
    p.add_argument("--expect", nargs=3, type=float, metavar=("X", "Y", "Z"))
    p.add_argument("--tol", type=float, default=1.0)
    args = p.parse_args()

    try:
        result = measure_stl(Path(args.stl))
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1

    result["ok"] = True
    if args.expect:
        result.update(compare_expect(result, list(args.expect), args.tol))
        result["ok"] = result["bbox_ok"]
        if not result["ok"]:
            print(json.dumps(result, indent=2))
            return 2

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
