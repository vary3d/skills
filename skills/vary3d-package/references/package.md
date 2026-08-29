# Package a model folder

Output a `packages/<slug>/` tree. **This file plus [examples/m5-flange/](../examples/m5-flange/) are the runtime authority.** Do not fetch a remote spec. If a published spec disagrees, follow this page and mention the mismatch.

## Customizer comments

Minimum for the site panel: `/* [Group] */` groups, a description line above each exposed assignment, same-line `// [min:step:max]` or `// [value:Label]` enums. Keep existing Labels. New labels default to English unless the user asked otherwise. Machine enum values stay as they were.

## Listing (`info.json`)

`format` must be `vary3d.info`, `version` `1`. `sourceLocale` matches the listing copy (`en` by default).

Write every time: `slug`, `name`, `description`, `category`, `tags`, `license`, `originType`, `engineType` (`openscad`), `entry` (`model.scad`), `cover` (`cover.png`).

Categories (only these): `practical_gadgets` · `maker_kits` · `mechanical_structures` · `educational_models` · `interactive_toys` · `general_assets`

Rules of thumb:

- `name` ≤100, `description` ≤800. Lead with what the card must show; extra sentences are fine. Not a slice recipe — see Description below.
- `tags` about 3 (max 5). Pick from the four axes below; do not pad. English unless the user asked otherwise.
- Default `license` `MIT`. Do not use ND.
- Finish `description` and `cover.png` after the cover render, so the blurb matches the part.

Forks: `originType` `fork` plus `sourceUrl` / `originalAuthor` / `sourceLicense` / `attribution` when known. Keep the upstream `LICENSE`.

**Never invent `parentModelId`.** Omit it unless it is a real Vary3D model id you already have.

Printable parts add `print` (shown as Docs after import) — see [print.md](print.md). If the `.scad` already has a `part` enum, keep it and put Print N× in `info.print`; do not invent a split or replace `part` with `show_*` booleans.

**Do not write:** server-assigned fields such as `id`, `userId`, object-storage paths, `status` / `visibility`, `engineVersion`, translated-copy fields (`*I18n`), counts, or `__vary`.

Check: `python3 "$SKILL_ROOT/scripts/validate-info.py" packages/<slug>/info.json`

Worked example: [examples/m5-flange/info.json](../examples/m5-flange/info.json).

## Description

`description` is listing copy. Cards on the site show the **first sentence or two** and omit the rest, so **front-load**. Later sentences are allowed (hard cap is 800 characters, not sentence count). Do not pad to fill 800.

**First sentence (always visible on the card):** what it is + the highest-value mate or distinctive feature. Same axes as tags (object / mate / feature). This sentence must stand alone.

- Good: `Round flange with a center bore and four M5 bolt holes on a pitch circle.`
- Good: `90-degree L-bracket with honeycomb lightening and M5 clearance holes.`
- Weak: `This parametric OpenSCAD model is designed for FDM printers…` (empty lead)

**Next sentences (optional):** use, a second difference, or who it is for. Print settings, assembly, and license do **not** belong here — print goes in `info.print`.

Finish `description` after the cover render so the blurb matches the part.

## Tags

Tags are search axes, not a keyword dump. **About 3, never more than 5.** Leave a slot empty rather than filling it with a weak word.

Take **0 or 1** from each axis, in this order. Object + mate + distinctive feature is the usual three.

| Axis | Question | Take when | Examples |
|---|---|---|---|
| **Object** | What is it? | Always | `flange`, `bracket`, `washer`, `enclosure`, `stand`, `hinge`, `knob`, `case` |
| **Mate** | What does it fit? | Standard part or real object | `m5`, `m3`, `608`, `usb-c`, `mx`, `go-pro` |
| **Feature** | How does it differ from others of that object? | Only if it changes shape or use | `honeycomb`, `print-in-place`, `magnetic`, `adjustable`, `threaded` |
| **Scene** | Who / where is it for? | Only if the object name is too generic | `phone`, `prusa`, `ikea`, `keycap` |

Form: lowercase English, one token (`print-in-place` is fine), singular (`bracket` not `brackets`). Use the word a user would type (`m5` not `iso-4762`). Several bolt sizes in presets → tag the **primary** size only; presets live in `variants.json`.

| Part | Tags |
|---|---|
| M5 flange | `flange`, `m5`, `bolt` |
| Honeycomb angle bracket | `bracket`, `honeycomb`, `m5` |
| 608 bearing holder | `bearing`, `608`, `holder` |
| Phone case | `case`, `iphone`, `phone` |
| Print-in-place hinge | `hinge`, `print-in-place` |

**Do not tag:** the category name; site-wide words (`openscad`, `parametric`, `customizer`, `3d-print`, `stl`, `fdm`); filler (`diy`, `maker`, `useful`); print details everyone has (`chamfer`); color, license, or author.

Check: `python3 "$SKILL_ROOT/scripts/validate-info.py" packages/<slug>/info.json`

## Presets (`variants.json`)

Write when there are **at least two useful** named sets. `format` `vary3d.variants`, `version` `1`.

- Keys in `files` are bundle-relative paths (entry `model.scad`).
- `params` keys must match top-level Customizer names exactly (`cover-variants.py` errors on typos).
- No `__vary`. Prefer no keys that start with `_`.
- Preset `name` / `description` English unless the user asked otherwise.
- Optional `cover` is a **relative PNG path** (e.g. `covers/m5.png`), not image bytes. `cover-variants.py` writes that field after rendering.
- Do not clone twenty presets that only change one number; each set needs a use case.
- Do **not** add a preset per `part` token (`part=base` / `part=lid`). Printable kinds and counts belong in `info.print` (`Print N×`), not `variants.json`. Presets are named size / feature sets (M4 vs M5), not export switches.

After writing the file, render covers:

```bash
python3 "$SKILL_ROOT/scripts/cover-variants.py" packages/<slug>/variants.json
python3 "$SKILL_ROOT/scripts/validate-variants.py" packages/<slug>/variants.json
```

Model default cover remains `cover.png` from `cover.py` — one image does not stand in for every preset.

Optional shared parameters: root `params.scad` plus `include <params.scad>` in the build root (see SKILL.md rule 3).

## Covers

```bash
python3 "$SKILL_ROOT/scripts/cover.py" packages/<slug>/model.scad
```

4:3, 45° diagonal orthographic. Uncolored faces use the site default `#2A9D90`; `color()` parts keep their own color. The first cover render may install a **Vary3D** color scheme into the local OpenSCAD config directory. **Open** the PNG.

## ORIGIN.md (forks)

```markdown
# Origin

- Forked from: https://example.com/original
- Original author: Name
- Upstream license: MIT (see LICENSE)
- This folder: Customizer comments, listing text, and named presets. Geometry is upstream.
- Libraries: none / BOSL2 (site preview may not include this library). Inlined spur-gear / trap-thread modules are not a third-party `use`.
```

Do not claim original design when it is not.

## Import from folder

Vary3D maps `info.json` / `variants.json` / OpenSCAD into a **draft**. It does not store those JSON documents as blobs. Guests can tweak parameters and export STL / 3MF once the model is published on the site.

The skill never publishes or reviews for you.
