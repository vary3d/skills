#!/usr/bin/env python3
"""ASCII outline of a PNG — when the image cannot be opened as a picture.

Usage: outline.py image.png [--width 80] [--height 24]

Renders the PNG to a coarse ASCII grid so an agent can confirm shape, holes,
and openings without a working image viewer. Uses only stdlib (zlib + struct)
so it works on macOS / Linux / Windows without Pillow or ImageMagick.
"""
from __future__ import annotations

import argparse
import struct
import sys
import zlib
from pathlib import Path


def read_png(path: Path) -> tuple[int, int, bytes]:
    """Return (width, height, RGB bytes) for a non-interlaced 8-bit PNG."""
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("not a PNG")
    pos = 8
    width = height = 0
    bit_depth = color_type = None
    idat = bytearray()
    while pos < len(data):
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        ctype = data[pos + 4 : pos + 8]
        chunk = data[pos + 8 : pos + 8 + length]
        if ctype == b"IHDR":
            width, height, bit_depth, color_type, _, _, interlace = struct.unpack(">IIBBBBB", chunk)
            if bit_depth != 8 or interlace != 0:
                raise ValueError(f"unsupported PNG: bit_depth={bit_depth} interlace={interlace}")
            if color_type not in (0, 2, 4, 6):  # gray, RGB, gray+alpha, RGBA
                raise ValueError(f"unsupported color_type={color_type}")
        elif ctype == b"IDAT":
            idat.extend(chunk)
        elif ctype == b"IEND":
            break
        pos += 12 + length
    raw = zlib.decompress(bytes(idat))
    return width, height, raw, color_type


def unfilter(width: int, height: int, raw: bytes, color_type: int) -> list[bytearray]:
    """Undo PNG scanline filters; return rows of RGB tuples."""
    bpp = {0: 1, 2: 3, 4: 2, 6: 4}[color_type]
    stride = width * bpp
    rows: list[bytearray] = []
    prev = bytearray(stride)
    i = 0
    for _ in range(height):
        f = raw[i]
        i += 1
        cur = bytearray(raw[i : i + stride])
        i += stride
        if f == 1:  # Sub
            for x in range(bpp, stride):
                cur[x] = (cur[x] + cur[x - bpp]) & 0xFF
        elif f == 2:  # Up
            for x in range(stride):
                cur[x] = (cur[x] + prev[x]) & 0xFF
        elif f == 3:  # Average
            for x in range(stride):
                a = cur[x - bpp] if x >= bpp else 0
                cur[x] = (cur[x] + ((a + prev[x]) >> 1)) & 0xFF
        elif f == 4:  # Paeth
            for x in range(stride):
                a = cur[x - bpp] if x >= bpp else 0
                b = prev[x]
                c = prev[x - bpp] if x >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                cur[x] = (cur[x] + pred) & 0xFF
        rows.append(cur)
        prev = cur
    # Convert to RGB
    rgb_rows: list[bytearray] = []
    for row in rows:
        if color_type == 2:
            rgb_rows.append(row)
        elif color_type == 6:
            rgb_rows.append(bytearray(v for i in range(0, len(row), 4) for v in row[i : i + 3]))
        elif color_type == 0:
            rgb_rows.append(bytearray(v for v in row for _ in range(3)))
        elif color_type == 4:
            rgb_rows.append(bytearray(v for i in range(0, len(row), 2) for v in (row[i],) * 3))
    return rgb_rows


def outline(path: Path, cols: int, rows_out: int) -> str:
    width, height, raw, ctype = read_png(path)
    rows = unfilter(width, height, raw, ctype)
    # Downsample to cols x rows_out
    sx = max(1, width // cols)
    sy = max(1, height // rows_out)
    chars = " .:-=+*#%@"
    lines = []
    for oy in range(rows_out):
        y = min(height - 1, oy * sy)
        line = []
        for ox in range(cols):
            x = min(width - 1, ox * sx)
            i = x * 3
            r, g, b = rows[y][i], rows[y][i + 1], rows[y][i + 2]
            # Invert luminance: dark pixels get denser glyphs
            lum = (r * 299 + g * 587 + b * 114) // 1000
            idx = (255 - lum) * (len(chars) - 1) // 255
            line.append(chars[idx])
        lines.append("".join(line).rstrip())
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("png", type=Path)
    ap.add_argument("--width", type=int, default=80)
    ap.add_argument("--height", type=int, default=24)
    args = ap.parse_args()
    if not args.png.is_file():
        print(f"missing {args.png}", file=sys.stderr)
        return 1
    try:
        print(outline(args.png, args.width, args.height))
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
