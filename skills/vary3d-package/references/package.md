# Package a model folder

Output a `packages/<slug>/` tree. **This file plus [examples/m5-flange/](../examples/m5-flange/) are the runtime authority for this skill version.** Do not fetch a remote spec at runtime — follow this page. If you know a published spec field disagrees with this page, finish the task per this page, tell the user the skill is stale, and copy the delta in with a version bump; do not invent fields the spec does not have.

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

Printable parts add a README `## Print` section (Import maps the README to Docs) — see [print.md](print.md). If the `.scad` already has a `part` enum, keep it and put Print N× in that section; do not invent a split or replace `part` with `show_*` booleans.

**Do not write:** `print` (`validate-info.py` rejects it — use README `## Print`); server-assigned fields such as `id`, `userId`, object-storage paths, `status` / `visibility`, `engineVersion`, translated-copy fields (`*I18n`), counts, or `__vary`.

Check: `python3 "$SKILL_ROOT/scripts/validate-info.py" packages/<slug>/info.json`

Worked example: [examples/m5-flange/info.json](../examples/m5-flange/info.json).

## Description

`description` is listing copy. Cards on the site show the **first sentence or two** and omit the rest, so **front-load**. Later sentences are allowed (hard cap is 800 characters, not sentence count). Do not pad to fill 800.

**First sentence (always visible on the card):** what it is + the highest-value mate or distinctive feature. Same axes as tags (object / mate / feature). This sentence must stand alone.

- Good: `Round flange with a center bore and four M5 bolt holes on a pitch circle.`
- Good: `90-degree L-bracket with honeycomb lightening and M5 clearance holes.`
- Weak: `This parametric OpenSCAD model is designed for FDM printers…` (empty lead)

**Next sentences (optional):** use, a second difference, or who it is for. Print settings, assembly, and license do **not** belong here — print goes in README `## Print`.

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
- Optional `cover` is a **relative PNG path** (e.g. `covers/m5.png`), not image bytes. `cover-variants.py` writes that field after rendering with OpenSCAD `-D` on the preview entry (so Global keys in `params.scad` apply). Do not rewrite only the entry file’s top-level assignments.
- Do not clone twenty presets that only change one number; each set needs a use case.
- Do **not** add a preset per `part` token (`part=base` / `part=lid`). Printable kinds and counts belong in README `## Print` (`Print N×`), not `variants.json`. Presets are named size / feature sets (M4 vs M5), not export switches.

After writing the file, render covers:

```bash
python3 "$SKILL_ROOT/scripts/cover-variants.py" packages/<slug>/variants.json
python3 "$SKILL_ROOT/scripts/validate-variants.py" packages/<slug>/variants.json
```

`cover-variants.py` also writes a default cover for each extra exportable build root (`covers/<stem>.png`). Extra roots are package-root `.scad` files except `params.scad` and `geometry.scad`. Model default cover remains `cover.png` from `cover.py`.

Optional **Global** (`params.scad`): only for a kit — complementary pieces on **different** files that must share wall / footprint / clearance. Kit test: opening A cannot export B’s piece (`box.scad` has no lid). Each of those roots `include <params.scad>`. Do not add it when one file already exports both via `part`, for extra Models that are each a full product, a single file, unrelated files, or libraries. Site Global sliders parse `params.scad`; the OpenSCAD GUI Customizer does **not** follow `include`. CLI `-D` on the entry overrides Global. Do not re-assign Global names on the build root. Spell this out in the package README when `params.scad` exists.

## Covers

```bash
python3 "$SKILL_ROOT/scripts/cover.py" packages/<slug>/model.scad
```

4:3, 45° diagonal orthographic. Uncolored faces use the site default `#2A9D90`; `color()` parts keep their own color. The first cover render may install a **Vary3D** color scheme into the local OpenSCAD config directory. **Open** the PNG.

`--set` / `--params-json` become OpenSCAD `-D` on that entry (end-of-file assignment). That overrides `params.scad`. Do not use `override-params.py` on the entry for Global keys.

## README.md

Long-form page (GitHub and Import Documentation). Generate after covers:

```bash
python3 "$SKILL_ROOT/scripts/generate-readme.py" packages/<slug>
```

Copy listing facts from `info.json` / `variants.json` / knobs / PNGs. Do not invent a second blurb. Do not copy the upstream README. **Preserve** an existing `## Print` section; do not read `info.print`.

Section order: title + description → Source → Files (Global / Models / Libraries) → Presets → Print → License. No top-level Parameters.

- **Fork Source:** Forked from URL, original author, upstream license, this folder (packaging only; geometry is upstream). No “Vary3D original”.
- **Original Source:** Vary3D original, no upstream CAD. No library files → `Libraries: none`.
- **Files / Global:** root `params.scad` only; three-surface note + visible knobs; no cover render.
- **Files / Models:** exportable build roots with images and that file’s visible knobs. Not `params.scad` / `geometry.scad`.
- **Files / Libraries:** `geometry.scad` and subdirectories of `.scad`; no render.
- **Presets:** not build roots. Image then name/value table.
- **Print:** author settings / orientation / why in README. Split: Print N×.

`validate-info.py` does not require README.

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

Vary3D maps `info.json` / `variants.json` / OpenSCAD / `README.md` into a **draft** (README → Documentation). It does not store those JSON documents as blobs. Guests can tweak parameters and export STL / 3MF once the model is published on the site.

The skill never publishes or reviews for you.
