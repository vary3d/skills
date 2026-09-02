---
name: vary3d-package
description: >-
  Wrap existing OpenSCAD into a Vary3D importable folder: info.json,
  variants.json, cover images, README.md, LICENSE, and ORIGIN.md. Does not invent
  geometry. Use when the user asks to import to Vary3D, Import from folder,
  publish a model folder, info.json, variants.json, Forked from,
  or normalize an existing .scad into the spec layout.
version: "1.22"
license: MIT
compatibility: Requires OpenSCAD CLI and Python 3. Works on macOS, Linux, and native Windows (no WSL needed). Windows users install OpenSCAD from the site or winget, then set OPENSCAD if it is not on PATH. First cover render may write a Vary3D color scheme into the local OpenSCAD config directory.
metadata:
  author: vary3d
  version: "1.22"
  related_skills: vary3d/skills@openscad-customizer
---

# Vary3D model package

## Software prerequisites (check first)

Before packaging, confirm the tools. Covers and the shape check need them.

- **OpenSCAD CLI** — required for `cover.py` and `validate.py`. Find it:
  `python3 "$SKILL_ROOT/scripts/find-openscad.py"`
  If missing: **stop**, show the install hint, and wait for the user. Only after they agree run `OPENSCAD_INSTALL=1 python3 "$SKILL_ROOT/scripts/find-openscad.py" --ensure` (portable archive in the user directory — no administrator rights).
- **Python 3** — required for every script in `scripts/`. Check `python3 --version`. If it is missing: **stop**, show python.org (Windows: winget package `Python.Python.3`) and wait. Do not install Python yourself.

Optional soft check (not a gate): if the user asks whether this skill is current, or `VARY3D_SKILL_CHECK=1` is set, run `python3 "$SKILL_ROOT/scripts/check-skill-version.py"`. It needs network; if unreachable, it prints a note and skips. Do not block the task on this check and do not auto-update.

## Language

- **Chat** follows the user’s language.
- **New file copy** (`info.json` name/description/tags, variant titles, Customizer groups and slider `//` lines you add, `README.md`) defaults to **English**. Switch only when the user **explicitly** asks (e.g. “listing in Japanese”, or any other language they name). Chatting in another language is **not** that request.
- **Existing Customizer copy:** keep it. Do **not** rewrite local-language slider labels to English for packaging. The site translates after publish. Set `info.sourceLocale` to match the listing copy (`en` by default). Machine enum **values** stay as they were; only human labels follow this rule.

Turn an existing `.scad` into a folder that **Import from folder** on [vary3d.com](https://vary3d.com) can map into a draft. This skill does **not** upload. It does **not** invent geometry.

If there is no working Customizer `.scad` yet, stop. The user needs **openscad-customizer**. Do not install it for them.

Runtime field rules are [references/package.md](references/package.md) plus [examples/m5-flange/](examples/m5-flange/). Do not fetch or follow a remote spec at runtime. If package.md and a published spec disagree, follow package.md and mention the mismatch.

Default output: `packages/<slug>/` relative to the repo root (or the working directory outside a repo). Use the path the user names if they give one. Keep the same `<slug>` as the design folder (`models/<slug>/`). Do **not** edit `models/` unless the user asked to pack in place.

If a Node project already uses `packages/` for npm, the user path still wins; CAD-first trees use `packages/<slug>/`.

```text
packages/<slug>/
  model.scad          # entry (required)
  info.json           # listing seed (required to publish)
  cover.png           # 4:3 cover from cover.py
  variants.json       # when there are ≥2 useful presets
  covers/<preset>.png # one cover per preset
  covers/<stem>.png   # default cover per extra build root
  params.scad         # kit only: complementary pieces on different files
  README.md           # Long-form; GitHub + Import → Docs
  LICENSE             # upstream text, unmodified (forks)
  ORIGIN.md           # Forked from, original author, what this folder changed
```

Do not ship `.openscad-iter/`, `.openscad-preview/`, `.vary3d-iter/`, `brief.json`, `plan.json`, `*.stl`, or `.DS_Store`. Extra `.scad` pulled in by `use` / `include` stays in the bundle.

**STL-only is not an import package.** The site will not accept `import("….stl")` as the entry. If the user only has a mesh, stop and say they need OpenSCAD source.

## When to read which file

This file is enough to start:

- How to copy and tidy without changing shape → [references/normalize.md](references/normalize.md)
- Listing copy, covers, README, ORIGIN → [references/package.md](references/package.md)
- Print notes in README `## Print` → [references/print.md](references/print.md)
- Samples → [examples.md](examples.md)

Customizer comment minimum: [package.md](references/package.md#customizer-comments).

## Rules

1. **Source tree is read-only** unless the user said “edit in place”. Copy the include/use closure into `packages/<slug>/`. Do not modify `models/` by default.
2. **Do not change the outside shape.** Compare bbox with `validate.py --expect … --tol 1` (1 mm). If `volume_mm3` moves by more than about 5%, you redesigned it — go back. Wrapping parts in `color()` is allowed. **Do not invent a split** or a `part` enum. If the source already has `part = "all"`, keep it — do not convert it to `show_*` booleans. Do not add `variants.json` presets that only switch `part`.
3. Entry file in the copy is `model.scad`. If other files `include` the old name, add one forwarding `include <old-entry.scad>` instead of rewriting every path. **`params.scad` only for a kit: complementary pieces on different files that must share wall / footprint / clearance.** Kit test: opening A cannot export B’s printable piece (`box.scad` has no lid). Then root `params.scad` plus `include <params.scad>` in those roots (see package.md). **Do not** add it when one file already exports both mating pieces via `part` (a tray file with `part=box` is a split, not a kit), for extra Models that are each a full product, a single file, unrelated files, or `geometry.scad` / library subdirs.
4. Listing strings (`name`, `description`, tags, variant titles) default to **English**. Switch only if the user explicitly asked. Chat language does not count. Set `sourceLocale` to match. The site translates after publish. **`description`:** ≤800; cards show the first sentence or two, so lead with object + mate/feature. More sentences are fine; print notes go in README `## Print`. See [package.md](references/package.md#description). **Tags: about 3, never more than 5.** Pick 0–1 from each axis — **object** (what it is), **mate** (what it fits), **feature** (what makes it different), **scene** (who it is for, only if the object name is generic). Do not repeat the category; do not pad with `openscad` / `parametric` / `diy`. See [package.md](references/package.md#tags).
5. Keep existing Customizer labels. Do not rewrite them to English. New labels you add are English unless the user asked otherwise. Machine enum values stay as they were.
6. Default single-part color `"#2A9D90"` (site viewer face color) unless the user asked for paint. Keep an existing `*_color` from the source; only fill the default when the source has none. Parameter names for colors end with `_color`; trailing `// color`.
7. Prefer `"yes"` / `"no"` enums over bare booleans so the site panel stays labeled. Converting `true`/`false` to those enums is **not** a shape change; update `variants.json` `params` to the new strings in the same edit.
8. Renaming knobs to `snake_case` is allowed for packaging; rename matching keys in presets in the same edit.
9. `info.slug` matches the folder name. It is a folder hint; the site assigns the public URL slug after review.
10. Do not write server-assigned fields: `id`, `userId`, object-storage paths, `status`, `visibility`, `__vary`. Do not write `print` (`validate-info.py` rejects it; use README `## Print`). **Never invent `parentModelId`** — omit it unless you already have a real Vary3D id.
11. Forks: keep upstream `LICENSE`; write `ORIGIN.md`; set `originType` to `fork` and fill source fields you know. Do not rebrand the design as Vary3D.
12. Third-party `use` / `include` (BOSL2, …): keep them if the source needs them. Inlined spur-gear / trap-thread modules stay inside `model.scad` (not a `lib/` folder). Note `// requires: BOSL2` in the header and in the reply when that library is used. `validate.py` fails on `Can't open library`. The site preview may not have that library.

## OpenSCAD CLI

Covers and the shape check need the CLI. First **find** it; do not install until the user agrees.

```bash
python3 "$SKILL_ROOT/scripts/find-openscad.py"
```

After they agree, `--ensure` installs a portable build into the user directory (no admin). Package-manager commands are in the script hint for the **user** to run.

```bash
OPENSCAD_INSTALL=1 python3 "$SKILL_ROOT/scripts/find-openscad.py" --ensure
```

Windows: no WSL or Git Bash needed. The user may install from [openscad.org](https://openscad.org/downloads.html) (default `C:\Program Files\OpenSCAD\openscad.exe`) or winget. If it is not on PATH, set `OPENSCAD` to the full path of `openscad.exe`. `--ensure` uses a portable zip under `%LOCALAPPDATA%\OpenSCAD-portable`. If the CLI is still missing, stop — do not fake a cover.

The first `cover.py` / `preview.py` **cover** view may write `Vary3D.json` into the user’s OpenSCAD color-scheme folder so uncolored faces match the site (`#2A9D90`). Say so if you run it.

## Commands

`SKILL_ROOT` is the directory that contains this `SKILL.md`.

```bash
# Shape baseline (source), then packaged entry with the same size ±1 mm
python3 "$SKILL_ROOT/scripts/validate.py" path/to/original.scad
python3 "$SKILL_ROOT/scripts/validate.py" packages/<slug>/model.scad --expect X Y Z --tol 1

# Top-level knobs
python3 "$SKILL_ROOT/scripts/extract-params.py" packages/<slug>/model.scad

# Listing / presets (no network)
python3 "$SKILL_ROOT/scripts/validate-info.py" packages/<slug>/info.json
python3 "$SKILL_ROOT/scripts/validate-variants.py" packages/<slug>/variants.json

# Default cover: 4:3, 45° diagonal. Open the PNG
python3 "$SKILL_ROOT/scripts/cover.py" packages/<slug>/model.scad

# One cover per preset (-D on the entry, including Global keys) plus extra build roots
python3 "$SKILL_ROOT/scripts/cover-variants.py" packages/<slug>/variants.json

# Long-form README (GitHub + Import Documentation)
python3 "$SKILL_ROOT/scripts/generate-readme.py" packages/<slug>
```

`--expect X Y Z` is `size` from the source JSON. Open `cover.png`. If there are many preset covers, open at least the default plus the two that change the silhouette most.

## Done when

- [ ] Packaged `model.scad` compiles; bbox matches source with `--tol 1`; volume is the same order
- [ ] `extract-params.py` lists only intended knobs and prints **no `warnings`** (count ceilings, deny-list names, file-scope formulas, debug `part`; standard-part fits and print details hidden or derived)
- [ ] `validate-info.py` passes (`vary3d.info` v1); `description` leads with object + mate/feature; tags about 3 (max 5), from object / mate / feature / scene — not padded
- [ ] `cover.png` was written and opened
- [ ] ≥2 useful presets → `validate-variants.py` passes plus preset covers opened (if `params.scad` exists, confirm a Global preset actually changed the silhouette)
- [ ] Extra build roots have `covers/<stem>.png` and were opened
- [ ] `generate-readme.py` wrote `README.md` (Files buckets; fork vs original Source; Global three-surface note only when `params.scad` exists)
- [ ] Forks: `LICENSE` + `ORIGIN.md` + source fields
- [ ] Printable parts: README `## Print` (split: Print N× per `part` token; `all` is preview only; no preset per token)
- [ ] Original tree `git status` is clean (unless in-place mode)
- [ ] No STL entry, no generator scratch in the folder

Deliver: the model folder path. Remind the user that **Import from folder** on vary3d.com maps these files into a draft; this skill does not publish for them. Guests can still tweak parameters in the browser and export STL / 3MF after the model is on the site.
