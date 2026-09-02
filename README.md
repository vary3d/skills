# Vary3D Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: macOS | Linux | Windows](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)](README.md)

Official **agent skills**: desktop OpenSCAD Customizer, and an optional folder layout for [vary3d.com](https://vary3d.com).

This repository is not the website, not an STL dump, and not an OpenSCAD include library (BOSL2 / MCAD). Skills do not upload models for you.

## Skills

| Skill | Install | Guide | For |
|---|---|---|---|
| [`openscad-customizer`](skills/openscad-customizer/SKILL.md) | `npx skills add vary3d/skills@openscad-customizer` | [docs/openscad-customizer.md](docs/openscad-customizer.md) | Write and check Customizer `.scad` in **desktop OpenSCAD** under `models/<slug>/`. No `info.json`. |
| [`vary3d-package`](skills/vary3d-package/SKILL.md) | `npx skills add vary3d/skills@vary3d-package` | [docs/vary3d-package.md](docs/vary3d-package.md) | Wrap existing `.scad` into `packages/<slug>/` for **Import from folder** (change numbers, export STL / 3MF). |

Install one skill at a time unless you need both:

```bash
npx skills add vary3d/skills@openscad-customizer
npx skills add vary3d/skills@vary3d-package
```

`npx skills add vary3d/skills` installs every skill in this repo.

## Documentation

Human guides (workflow, core ideas, when to use which skill):

- [OpenSCAD Customizer](docs/openscad-customizer.md) — from user request to verified `.scad` and desktop GUI
- [Vary3D model package](docs/vary3d-package.md) — from existing `.scad` to Import-from-folder layout

Runtime instructions stay in each skill’s `SKILL.md` and `references/`. Guides are for contributors and installers.

Related repositories:

- **[vary3d/spec](https://github.com/vary3d/spec)** — publish format (`info.json`, `variants.json`, Customizer comments, `params.scad`, package `README.md`)
- **[vary3d/library](https://github.com/vary3d/library)** — catalog models

Forks keep the **upstream license**. Fill Forked from; do not rebrand the design as Vary3D.

## Layout

```text
skills/<skill-name>/
  SKILL.md          # runtime entry (do not duplicate as README here)
  scripts/          # optional
  references/       # optional
docs/
  <skill-name>.md   # human guide (workflow + links back to SKILL.md)
```

Folder name matches the skill `name` in frontmatter. Skill folders have no README — use `docs/<skill-name>.md` instead. Repo root `README.md` is the index.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for script mirroring, version bumps, and language rules. See [CHANGELOG.md](CHANGELOG.md) for skill versions.

## Issues

Use Issues for skills in this repository.

Do not file site, account, payment, or moderation bugs here.

## License

MIT. See [LICENSE](LICENSE).

The self-tap hole snippet in `openscad-customizer` follows [OpenEng](https://gitlab.com/bath_open_instrumentation_group/openeng) (MIT). Keep that URL in the comment when inlining. Other inlined examples (gears, threads, polyhole, teardrop) are original to this skill — no extra credit line.

## Security

See [SECURITY.md](SECURITY.md). Email **security@vary3d.com**. Do not post proofs of concept in public issues.
