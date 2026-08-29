# Contributing

This repository ships **agent skills**. Each skill folder is self-contained so `npx skills add vary3d/skills@<name>` works without the rest of the tree.

## Scripts

Each skill carries its **own copy** of `scripts/`. When you change a shared script, mirror the change into the other skill:

`find-openscad.py`, `install-portable.py`, `preview.py`, `multi-preview.py`, `outline.py`, `bbox.py`, `extract-params.py`, `override-params.py`, `validate.py`, `section.py`, `check-skill-version.py`

**Cross-platform:** the real implementations are `*.py` and run on macOS, Linux, and native Windows (no WSL / Git Bash). The `*.sh` files are thin compatibility shims that `exec python3` the matching `.py`. Keep both in sync.

`find-openscad.py` searches `OPENSCAD`, PATH, Homebrew, `/Applications`, Linux system paths, and on Windows `Program Files` / `LOCALAPPDATA` / winget / choco. `preview.py` writes the Vary3D color scheme to the platform config dir (`%APPDATA%\OpenSCAD\...` on Windows).

**Portable `--ensure`:** after the user agrees, `--ensure` runs `install-portable.py` only — official archive from files.openscad.org (sha256-checked) into a user dir. Never `sudo`, never brew/winget/apt. Package-manager commands stay in `hints()` for the user to copy-paste. Windows `%LOCALAPPDATA%\OpenSCAD-portable`, macOS `~/Applications/OpenSCAD-portable`, Linux `~/.local/share/openscad-portable` (AppImage). No admin needed.

## Versions

Each skill folder has a one-line `VERSION` file (same number as `metadata.version` in `SKILL.md`). The optional soft check (`VARY3D_SKILL_CHECK=1`, or when the user asks) runs `scripts/check-skill-version.py`, which compares those one-line files. It is not a hard gate and never auto-updates; it skips quietly when the network is unreachable. Do not fetch remote `SKILL.md`.

**Bump `VERSION` and `metadata.version` together** on behavior changes so the soft check stays meaningful. Note the bump in [CHANGELOG.md](CHANGELOG.md).

When [vary3d/spec](https://github.com/vary3d/spec) changes a field the packager must follow, **copy the delta into `vary3d-package/references/package.md`** and bump that skill. Runtime skills must not fetch the spec.

## Language

Chat replies follow the user. Copy written into `.scad` / `info.json` / presets defaults to **English**; switch only if the user explicitly asks (chat language is not that request). Packaging must **not** rewrite existing local-language Customizer labels to English — the site translates after publish. Set `info.sourceLocale` to match the listing copy.

Skill files themselves are English only (no locale-specific sample prompts). Ask confirmation questions in the user’s language at runtime.

## Modeling rules

- **Two trees:** design writes `models/<slug>/model.scad`; packaging writes `packages/<slug>/`. Do not put `info.json` / covers in `models/`, and do not edit `models/` while packaging unless the user asked in-place.
- **Split for print:** user saying “split” / “easier” → Confirm with a recommendation, not auto-split. If it stays one piece, **tell the user**. After they pick split: 2–4 kinds → one `part` enum, default All. No `show_<part>`. `--single-body` per token, not on `all`.
- **Few knobs:** millimetres in the request are defaults, not sliders. Visible cap: simple ≤ 6, complex ≤ 8. Mate holder: object sizes only. Three layers: visible knobs, Hidden literals, derived locals inside the module. `extract-params.py` warnings block Done.
- **Opens in the desktop app:** prefer no third-party `use`/`include`; inline `examples/` MIT snippets instead of MCAD. If BOSL2 is required, note `// requires: BOSL2` in the header. `validate.py` fails on a missing library. `open-gui.py` launches the app with the file loaded.
- **Preview PNGs in workspace:** `multi-preview.py` and `section.py` default to `.openscad-preview/` beside the `.scad`. Many agent image viewers accept workspace paths only — not `/tmp`. Use `outline.py` only when opening a workspace PNG still fails.

## Validators

- `validate-info.py` does not require `cover`: covers are rendered after packaging with `cover.py`. Add `cover.png` before publishing.
- `validate-info.py` rejects `ND` (no-derivatives) licenses; default is `MIT`.
- `validate-variants.py` fails on `__vary` but only **warns** on params keys starting with `_` (spec wording is "prefer no").
- `extract-params.py` reports `visible_count` / `hidden_count` and a `warnings` array: count ceilings, extra `*_color`, deny-list names on the default panel, formulas at file scope, non-English group titles, debug `part` tokens, and assignments after the first `module` / `function`. Warnings are an agent Done gate, not a `validate.py` fail.

## Docs

- `README.md` is the public index. Keep it short.
- `docs/<skill-name>.md` is the human guide; keep it in sync with that skill’s `SKILL.md` (gates, verify commands).
- `SKILL.md` and `references/` are runtime instructions. Do not name a specific agent product or image-tool.
