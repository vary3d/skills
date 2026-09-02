#!/usr/bin/env python3
"""Write packages/<slug>/README.md from listing JSON, knobs, and cover PNGs.

Does not invent blurb. Import maps this file to site Documentation.
Regenerating preserves an existing ## Print section.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


extract_params = _load("extract_params", "extract-params.py")

THREE_SURFACES = """\
Shared sizes live in `params.scad` (Global on vary3d.com).

- vary3d.com: Global sliders on any file that includes `params.scad`.
- OpenSCAD app: opening the build root does not list those sliders (Customizer does not follow `include`). Edit `params.scad`, or use the site.
- OpenSCAD CLI: `openscad -D 'body_z=70.5' model.scad` on the entry file.
"""

COPYRIGHT_RE = re.compile(r"^Copyright \(c\) .+$", re.M)
ORIGIN_LINE = re.compile(r"^-\s*(.+)$", re.M)
PRINT_SECTION = re.compile(r"(^## Print\n.*?)(?=^## |\Z)", re.M | re.S)

SKIP_MODEL_NAMES = frozenset({"params.scad", "geometry.scad"})


def load_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else None


def visible_params(scad: Path) -> list[dict]:
    text = scad.read_text(encoding="utf-8")
    params, _warnings = extract_params.extract(text)
    vis, _hid = extract_params.split_visible(params)
    return vis


def md_cell(value) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def param_table(rows: list[dict], *, with_range: bool) -> str:
    if with_range:
        lines = [
            "| Name | Default | Range | What it does |",
            "|---|---|---|---|",
        ]
        for p in rows:
            hint = (p.get("hint") or "").strip()
            lines.append(
                "| {name} | {val} | {hint} | {desc} |".format(
                    name=md_cell(p.get("name")),
                    val=md_cell(p.get("value")),
                    hint=md_cell(hint),
                    desc=md_cell(p.get("description")),
                )
            )
        return "\n".join(lines)
    lines = ["| Name | Value |", "|---|---|"]
    for p in rows:
        lines.append(
            "| {name} | {val} |".format(
                name=md_cell(p.get("name")),
                val=md_cell(p.get("value")),
            )
        )
    return "\n".join(lines)


def title_from_stem(stem: str) -> str:
    title = stem.replace("-", " ").replace("_", " ").title()
    return re.sub(r"(\d)X(\d)", r"\1x\2", title)


def origin_fields(origin_md: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not origin_md.is_file():
        return out
    text = origin_md.read_text(encoding="utf-8")
    for raw in ORIGIN_LINE.findall(text):
        if ":" not in raw:
            continue
        key, val = raw.split(":", 1)
        out[key.strip().lower()] = val.strip()
    return out


def copyright_line(license_path: Path) -> str:
    if not license_path.is_file():
        return ""
    match = COPYRIGHT_RE.search(license_path.read_text(encoding="utf-8"))
    return match.group(0).strip() if match else ""


def existing_print(pkg: Path) -> str:
    readme = pkg / "README.md"
    if not readme.is_file():
        return ""
    match = PRINT_SECTION.search(readme.read_text(encoding="utf-8"))
    return match.group(1).rstrip() if match else ""


def iter_variant_items(data: dict):
    files = data.get("files") or {}
    if isinstance(files, dict):
        for rel, items in files.items():
            if not isinstance(items, list):
                continue
            for item in items:
                if isinstance(item, dict):
                    yield "file", rel, item
    package = data.get("package") or []
    if isinstance(package, list):
        for item in package:
            if isinstance(item, dict):
                rel = item.get("previewEntryPath") or "model.scad"
                yield "package", rel, item


def extra_roots(pkg: Path, entry: str) -> list[Path]:
    skip = set(SKIP_MODEL_NAMES)
    skip.add(entry)
    return [path for path in sorted(pkg.glob("*.scad")) if path.name not in skip]


def library_entries(pkg: Path, origin: dict[str, str]) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    if (pkg / "geometry.scad").is_file():
        rows.append(("geometry.scad", "Module helpers. Not a build root."))
    lib_blurb = (origin.get("libraries") or "").strip()
    for child in sorted(pkg.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        if not any(child.rglob("*.scad")):
            continue
        note = lib_blurb if lib_blurb and lib_blurb.lower() != "none" else (
            "Vendored library. Not a build root."
        )
        rows.append((f"{child.name}/", note))
    return rows


def file_image(pkg: Path, rel: str, entry: str) -> str:
    if rel == entry and (pkg / "cover.png").is_file():
        return "cover.png"
    stem = Path(rel).stem
    candidate = pkg / "covers" / f"{stem}.png"
    if candidate.is_file():
        return f"covers/{stem}.png"
    if rel == entry and (pkg / "cover.png").is_file():
        return "cover.png"
    return ""


def source_section(info: dict, origin: dict[str, str], has_libs: bool) -> str:
    origin_type = info.get("originType") or "original"
    this_folder = origin.get("this folder") or ""
    if origin_type == "fork":
        url = info.get("sourceUrl") or origin.get("forked from") or ""
        author = info.get("originalAuthor") or origin.get("original author") or ""
        lic = info.get("sourceLicense") or origin.get("upstream license") or info.get("license") or "MIT"
        lines = ["## Source", ""]
        if url:
            lines.append(f"Forked from {url}")
        if author:
            lines.append(f"by {author}. Upstream license: {lic.split('(')[0].strip()}.")
        else:
            lines.append(f"Upstream license: {lic.split('(')[0].strip()}.")
        lines.append("")
        if this_folder:
            lines.append(this_folder)
        else:
            lines.append(
                "This folder adds Customizer comments, listing text, and named presets. Geometry is upstream."
            )
        return "\n".join(lines)

    lines = [
        "## Source",
        "",
        "Vary3D original. No upstream CAD.",
        "",
    ]
    if this_folder:
        lines.append(this_folder)
    else:
        lines.append("This folder is the import package: entry file, listing copy, and presets when present.")
    if not has_libs:
        lines.append("")
        lines.append("Libraries: none")
    return "\n".join(lines)


def model_block(pkg: Path, path: Path, entry: str, package_name: str) -> list[str]:
    rel = path.name
    img = file_image(pkg, rel, entry)
    title = package_name if rel == entry else title_from_stem(path.stem)
    block = [f"#### {title}", "", f"`{rel}`", ""]
    if img:
        block += [f"![{title}]({img})", ""]
    vis = visible_params(path)
    if vis:
        block += [param_table(vis, with_range=True), ""]
    return block


def build() -> str:
    if len(sys.argv) < 2:
        print("usage: generate-readme.py packages/<slug>/", file=sys.stderr)
        return ""
    pkg = Path(sys.argv[1]).resolve()
    info = load_json(pkg / "info.json")
    if not info:
        print(f"missing info.json in {pkg}", file=sys.stderr)
        sys.exit(1)
    entry = str(info.get("entry") or "model.scad")
    name = str(info.get("name") or pkg.name)
    description = str(info.get("description") or "").strip()
    origin = origin_fields(pkg / "ORIGIN.md")
    has_params = (pkg / "params.scad").is_file()
    variants = load_json(pkg / "variants.json") or {}
    roots = [pkg / entry] if (pkg / entry).is_file() else []
    roots.extend(extra_roots(pkg, entry))
    libs = library_entries(pkg, origin)

    parts: list[str] = [f"# {name}", ""]
    if (pkg / "cover.png").is_file():
        parts += [f"![{name}](cover.png)", ""]
    if description:
        parts += [description, ""]

    parts += [
        source_section(info, origin, bool(libs)),
        "",
    ]
    file_parts: list[str] = []

    if has_params:
        file_parts += ["### Global", "", "`params.scad`", "", THREE_SURFACES.rstrip(), ""]
        gvis = visible_params(pkg / "params.scad")
        if gvis:
            file_parts += [param_table(gvis, with_range=True), ""]

    model_bits: list[str] = []
    seen: set[str] = set()
    for path in roots:
        if path.name in seen:
            continue
        seen.add(path.name)
        model_bits += model_block(pkg, path, entry, name)
    if model_bits:
        file_parts += ["### Models", ""]
        if len(roots) > 1:
            file_parts += ["Export the file you need.", ""]
        file_parts += model_bits

    if libs:
        file_parts += ["### Libraries", ""]
        for rel, note in libs:
            file_parts += [f"`{rel}`", "", note, ""]

    if file_parts:
        parts += ["## Files", ""] + file_parts

    items = list(iter_variant_items(variants)) if variants else []
    if items:
        parts += ["## Presets", ""]
        if any(kind == "package" for kind, _rel, _item in items):
            parts.append("Package presets set Global parameters. They still apply after you switch build root.")
            parts.append("")
        for kind, rel, item in items:
            title = str(item.get("name") or "Preset")
            desc = str(item.get("description") or "").strip()
            cover = str(item.get("cover") or "")
            params = item.get("params") if isinstance(item.get("params"), dict) else {}
            parts += [f"### {title}", ""]
            if desc:
                parts += [desc, ""]
            if cover:
                parts += [f"![{title}]({cover})", ""]
            if params:
                rows = [{"name": k, "value": v} for k, v in params.items()]
                parts += [param_table(rows, with_range=False), ""]
            if kind == "package":
                parts.append(f"Preview file: `{rel}`.")
                parts.append("")

    print_sec = existing_print(pkg)
    if print_sec:
        parts += [print_sec, ""]

    lic_name = str(info.get("license") or "MIT")
    copy = copyright_line(pkg / "LICENSE")
    parts += ["## License", "", lic_name + ("." if not lic_name.endswith(".") else "")]
    if copy:
        parts += ["", copy]
    parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def main() -> int:
    text = build()
    if not text:
        return 2
    pkg = Path(sys.argv[1]).resolve()
    out = pkg / "README.md"
    out.write_text(text, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
