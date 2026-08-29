# Changelog

Skill versions live in each `SKILL.md` under `metadata.version` and the sibling `VERSION` file. This file summarizes user-visible changes.

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
