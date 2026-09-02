# Changelog

Skill versions live in each `SKILL.md` (`version` and `metadata.version`) and the sibling `VERSION` file. This file summarizes user-visible changes.

## openscad-customizer 1.27 / vary3d-package 1.22 — 2026-09-02

- Cover fill default is 80% of the limiting side (listing-card size). `OPENSCAD_COVER_FILL` still overrides.

## openscad-customizer 1.26 / vary3d-package 1.21 — 2026-09-02

- Cover/preview PNG: composite the object onto a centered white canvas of the same aspect (4:3 for covers). Fill about 80% of the limiting side so the margin is even, not a minimum crop. `OPENSCAD_COVER_FILL` overrides the fill (0.4–0.92). `OPENSCAD_NO_CROP=1` still skips.

## openscad-customizer 1.25 / vary3d-package 1.20 — 2026-09-02

- `preview.py` / `cover.py` tight-crop OpenSCAD `--viewall` whitespace after render. The crop keeps the source aspect (cover stays 4:3). Skip with `OPENSCAD_NO_CROP=1`.

## vary3d-package 1.19 — 2026-09-02

- `generate-readme.py` no longer inserts “Play on vary3d.com (Import from folder). Or open `model.scad` in OpenSCAD.” Title goes straight to description, then Source.

## openscad-customizer 1.24 / vary3d-package 1.18 — 2026-09-02

- Kit test for `params.scad`: opening file A cannot export the piece that only lives in file B. Dropped the parenthetical “each file is still a complete article if opened alone” — that phrasing made agents add Global when a second Model already includes the box and exports both pieces via `part`. Extra complete products in one package are extra Models, not a kit.

## openscad-customizer 1.23 / vary3d-package 1.17 — 2026-09-01

- Spec/skill layering pass. spec/customizer.md keeps only parsing rules; knob caps, mate-holder, and split-of-one-article stay in the openscad-customizer skill (not a format gate). spec/variants.md `files` keys are build roots, not library files.
- spec/directory.md separates the three uses: Import ignores the parent directory; skill defaults are `models/` (design) and `packages/` (Import-ready); the official catalog repo stores the same Import contents under `models/<slug>/`.
- vary3d-package/package.md is the runtime excerpt for this skill version; a known spec delta is reported + bumped, not used to invent fields.
- Examples unified on `#2A9D90`; packaging keeps an existing source `*_color` and only fills the default when missing.
- `validate-info.py` rejects `parentModelId` and `originType: null`. `extract-params.py` deny list adds `corner_radius`, `fold_angle`, `tilt_deg`, `pin_d`. normalize.md Done aligns with SKILL.md: `extract-params` must print no warnings; hiding knobs / yes-no / adding color is not a shape change. scad-style.md notes an `import("….stl")` design file cannot be the Import entry.
- `part` enum, when present, is the first top-level assignment (before Dimensions and color) so the part selector leads the Customizer panel. print.md gains a "Split-part parameters at a glance" section.
- `params.scad` trigger reworded from "independent products that must share" to "a kit — parts that assemble and must share wall / footprint / clearance to mate". spec/params-scad.md example replaced: bracket+spacer (unrelated, degenerate) → box+lid kit where the lid mates on shared `wall` + `clearance`.

## openscad-customizer 1.22 / vary3d-package 1.16 — 2026-09-01

- One article, 2–4 printable kinds: one file + `part`; knobs are envelope + `wall` (derive the rest). Extra build roots + `params.scad` only when ≥2 roots are independent products that share wall / footprint. Do not add Global for a `part` split, a single file, or unrelated files.

## vary3d-package 1.15 — 2026-09-01

- `validate-info.py` rejects `print` (use README `## Print`). Original Source with no library files ends with `Libraries: none`.

## vary3d-package 1.14 — 2026-09-01

- `README.md` is the long-form page (GitHub and Import Documentation). No `info.print`. Files split into Global (`params.scad`), Models (rendered), Libraries (not rendered). `generate-readme.py` preserves `## Print` and does not invent print copy. GFM images (no HTML hero).

## vary3d-package 1.13 / openscad-customizer 1.21 — 2026-09-01

- Package `README.md` is the GitHub view of listing facts (Import ignores it). `generate-readme.py` writes it from `info.json` / presets / knobs / covers. Fork and original Source differ. If `params.scad` exists, README states the three surfaces: site Global sliders, OpenSCAD GUI Customizer does not follow `include`, CLI `-D` on the entry overrides Global.
- Preset covers use OpenSCAD `-D` on the preview entry so Global keys apply. `cover-variants.py` also renders extra build roots. Do not rewrite only the entry file to set Global.
- openscad-customizer must not write `README.md` (same as `info.json` / covers).

## Docs — 2026-08-30

- Human guides (`docs/*.md`) aligned with SKILL.md gates and verify commands: `--expect` is not always; `extract-params.py` before six views; package JSON validators before `cover.py`; `$SKILL_ROOT` on copy-paste commands.
- Publish hygiene: LICENSE third-party path (no doubled `skills/`); README License + platform badges; SKILL.md top-level `version` kept in sync with `metadata.version`.

## openscad-customizer 1.20 / vary3d-package 1.12 — 2026-08-29

- **Mate holder** rule: a stand / cradle / pocket for a known object exposes that object’s mating sizes only; arms, lip, reveal, `gap`, invented features, and debug `part` tokens are not Customizer knobs. `examples.md` has a coin-stand walkthrough (including the 14-slider anti-pattern).
- `extract-params.py` also warns on deny-list names on the default panel, formulas at file scope, non-English group titles, and `part` values like `assembly` / `coin` / `section` / `interference`. Any warning blocks Done (still not a `validate.py` fail).

## openscad-customizer 1.19 — 2026-08-29

- Three layers in Few knobs: visible knobs (product), Hidden literals (overrides / `-D` / presets), derived **module locals**. No formulas in the Customizer window. `scad-style.md` has a box snippet (`outer` / `lip_w` from `inner` + `wall`).

## openscad-customizer 1.18 / vary3d-package 1.11 — 2026-08-29

- Few knobs is a **ceiling** (simple ≤ 6, complex ≤ 8 including `part` and one color), not a quota. Request millimetres are defaults, not a Customizer list. Standard-part fits (e.g. M5 clearance on the sample flange) go in `[Hidden]`; extra colors and joint lip/pin literals do too, or are derived from host wall `T`.
- `extract-params.py` reports `visible_count` / `hidden_count` and warns when visible knobs exceed those caps or when more than one `*_color` is on the default panel.
- Confirm `key_parameters` lists only visible knobs. Sample flange and package example hide `bolt_clearance_dia`.

## openscad-customizer 1.17 / vary3d-package 1.10 — 2026-08-29

- Install hints no longer print `sudo`. Missing Python: stop and show the user python.org / winget package name; do not install it. Version check uses anonymous fetch only (no token header).

## openscad-customizer 1.16 / vary3d-package 1.9 — 2026-08-29

- Security audit pass: Research uses user sizes, in-skill tables, then Confirm-gated candidates (no “search and extract”). Packaging runtime authority is `package.md`, not a remote spec. `--ensure` installs a portable OpenSCAD only (no sudo, no package manager). Version soft-check reads `VERSION`, not remote `SKILL.md`. Sister-skill `npx` commands stay in README/docs, not skill bodies.

## openscad-customizer 1.15 — 2026-08-29

- User-attached photos, CAD three-views, screenshots, and drawings are **input**. Read them before Brief. Topology from the image; millimetres from text, datasheet, or a question. Confirm the reading; verify iso+top against the reference. Not image-to-mesh.

## openscad-customizer 1.14 — 2026-08-29

- FDM hole snippets to **inline** (MIT): `examples/polyhole.scad` (vertical), `examples/teardrop.scad` (horizontal, apex +Z), `examples/selftap.scad` (plastic tap after OpenEng MIT). No MCAD.

## openscad-customizer 1.13 / vary3d-package 1.8 — 2026-08-29

- Spur gears and trapezoid threads: MIT reference implementations to **inline** (`examples/spur-gear.scad`, `examples/trap-thread.scad`). No `models/<slug>/lib/`, no `use <MCAD>`.
- BOSL2 only when the user asked; if missing, stop and show a clone into OpenSCAD libraries. Do not clone without consent.
- `validate.py` fails on `Can't open library` even when leftover geometry still compiles (mirrored in vary3d-package).

## openscad-customizer 1.12 — 2026-08-28

- Split joints: derive lip / pin / screw sizes from host wall thickness `T` (recipe table). Same named constants; `fit_gap` on the female only. Checkable `print.joint` string. Assembled 2D section through the joint is a gate.

## openscad-customizer 1.11 — 2026-08-28

- `section.py` defaults to a 2D true cut (`--2d`). `--3d` is the half-space cutaway; its camera faces the cut (xz→back), not iso. A 3D iso cutaway of a hollow box looks like an intact shell with one square face — that is not the cavity/joint check.

## openscad-customizer 1.10 — 2026-08-28

- “Split / easier to print” enters Confirm with a recommendation; it does not auto-split. Estimate wall angle from sizes (from vertical, ≤45°). If it stays one piece, **say so** on Confirm and delivery. Split `plan.json` only after the user picks split.

## openscad-customizer 1.9 / vary3d-package 1.7 — 2026-08-28

- Print ladder: reorient, then geometry, then split-for-print, then supports. Do not split by default. “No supports” alone is not a split trigger.
- 2–4 printable kinds: one `part` enum, default All. No `show_<part>` booleans. `--single-body` per token, not on `all`. `preview.py` / `section.py` accept `--openscad-arg` (`-D part="lid"`).
- Packaging does not invent a split; keep an existing `part` enum and put Print N× in `info.print`. Cover render stays on `part="all"`. Do not add presets that only switch `part`.

## openscad-customizer 1.8 / vary3d-package 1.6 — 2026-08-27

- Default design tree: `models/<slug>/model.scad` (openscad-customizer). No `packages/`, `info.json`, or covers.
- Default import tree: `packages/<slug>/` (vary3d-package). Copy from `models/`; do not edit the design folder unless asked in-place.
- Official catalog layout is `packages/<slug>/` ([vary3d/spec directory.md](https://github.com/vary3d/spec/blob/main/directory.md)).

## vary3d-package 1.5 — 2026-08-27

- `info.json` tags: about 3, hard max 5 (`validate-info.py`). Name from object / mate / feature / scene; do not pad.
- `description`: lead with object + mate/feature (listing cards truncate after the first sentences); more sentences allowed, ≤800.

## openscad-customizer 1.7 / vary3d-package 1.4 — 2026-08-27

- English-only skill files. Chat still follows the user; confirmation questions are asked in the user’s language.
- Neutral wording for image viewers and datasheet lookup (no product-specific tool names).
- Human guides aligned with runtime gates (floating-parts check, `validate.py` exit 3).
- Public repo hygiene: slimmer README, CONTRIBUTING, this changelog.

## openscad-customizer 1.6

- Research gate: look up datasheets / standard-part sizes before Brief.
- Confirm gates: wait for the user after the brief, after six views, and after opening the GUI.
- Floating-parts detection: `validate.py --single-body` (exit 3) and `section.py --check-floating`.
- Preview PNGs default to `.openscad-preview/` beside the `.scad` (workspace path, not `/tmp`).
- `open-gui.py` is the default handoff.

## vary3d-package 1.3

- Same OpenSCAD install / Windows / portable fallback as openscad-customizer.
- Mirrored preview, outline, bbox, and validate scripts.

## Earlier

- 1.x: Customizer style (few knobs, English file copy), native Windows, portable OpenSCAD install, skill-version soft check, desktop-only customizer vs site packaging split.
