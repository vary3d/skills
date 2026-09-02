# Normalize existing code

User has `.scad` and wants parameters, comments, presets, or a spec folder — **without a new design**.

- Not a one-line in-place tweak (that stays in the original file; no new `info.json` unless they asked to pack).
- Not a redesign (that is **openscad-customizer**, a separate skill — do not install it for them) with a new brief/plan.
- Default: **do not change the outside shape**. If they also want a new feature, pack first, then hand geometry to openscad-customizer.

**STL-only:** stop. Import from folder needs OpenSCAD source. Do not copy a mesh into the publish folder or `import("part.stl")` as the entry.

## Directory

**Source tree is read-only.** Write `packages/<slug>/` (same slug as the design folder). Do not modify `models/` unless the user asked to pack in place.

| Source | Action |
|---|---|
| Already `packages/<slug>/` | Fill missing listing files in place; do not duplicate |
| Already `models/<slug>/` | Copy into `packages/<slug>/`; leave `models/` untouched |
| Library / other project tree | Copy the include/use closure; do not touch the original tree |
| Folder outside the repo | Create `packages/<slug>/` under the working directory |

Skip `.openscad-preview/`, `.openscad-iter/`, `brief.json`, and `plan.json` — those belong to the design working copy, not the import folder.

Edit the original tree only when the user said “in place”, and say what you changed.

## Flow

1. **Baseline:** `validate.py` on the original entry; note `size` and `volume_mm3`; `extract-params.py` for knobs; read `use` / `include` (report cycles) and the main module. If a `part` enum exists, keep it (do not add `show_<part>`).
2. **Slug:** ASCII lowercase kebab-case. No non-ASCII folder names.
3. **Copy closure:** entry + `.scad` actually included/used + required assets. Skip STL caches, old PNG, `.DS_Store`, `.openscad-iter/`, `.vary3d-iter/`.
4. **Entry:** copy’s entry is `model.scad`. If relatives still include the old filename, one `include <old-entry.scad>` in `model.scad` — do not rewrite every path. **`params.scad` only for a kit: complementary pieces on different files that must share wall / footprint / clearance.** Kit test: opening A cannot export B’s printable piece. Then add root `params.scad` and `include <params.scad>` in those roots. Skip it when one file already exports both via `part`, for extra Models that are each a full product, a `part` split, unrelated files, and helper/library `.scad`.
5. **Tidy** (mesh unchanged):
   - Top-level parameters full `snake_case`; description on the line above; `/* [Group] */`. New copy is English unless the user asked otherwise
   - Only literals before the first module; derived expressions move inside the module
   - Add missing `_color`. Feature `show_*` only if the source already uses them for features — do not add `show_<part>` when `part` exists. Wrapping with `color()` is allowed
   - Enums `// [value:Label]` — keep machine values; keep existing Labels (do not rewrite local-language Labels to English)
   - Bare `true`/`false` → `"yes"`/`"no"` enums when packing for the site panel; update preset `params` to those strings in the same edit
   - Rename knobs and matching preset keys in the same edit
   - If a `part` enum exists, move it to the **first** top-level assignment (before Dimensions and color) so the site panel lists the part selector first. This is an order change, not a shape change
   - Do **not** rewrite existing local-language slider copy to English; the site translates after publish
6. **Listing files:** `info.json` (forks fill origin fields; never invent `parentModelId`), `cover.png`; ≥2 useful presets → `variants.json` + preset covers. `generate-readme.py` for `README.md` (GitHub + Import Docs). If an old variants file exists, point `files` keys at `model.scad` and rename `params` to the new top-level names. Do not write `info.print`.
7. **Libraries:** keep `use` / `include` the source needs. Comment `// requires: BOSL2` (or the library name). Inlined MIT gear/thread modules need no extra files. Site preview may not load BOSL2. `validate.py` fails if a `use` is missing.
8. **Do not write brief/plan** — those belong to geometry generation.

## Done

- [ ] `validate.py` on the packaged entry with `--expect` from the baseline `size` and `--tol 1`
- [ ] `volume_mm3` within ~5% of baseline
- [ ] `extract-params.py` lists only intended knobs and prints **no `warnings`** (count ceilings, deny-list names, file-scope formulas). Hiding a knob, switching to `"yes"`/`"no"` enums, or adding a missing `*_color` is **not** a shape change
- [ ] `validate-info.py` (and `validate-variants.py` if presets)
- [ ] `cover.png` (and preset covers) opened
- [ ] `README.md` generated
- [ ] Original tree `git status` clean (unless in-place)
