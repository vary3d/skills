# Verify

The hard gate must pass before you deliver. The soft gate is required when you can render; if you cannot, say “no images” and why.

The user should be able to open the result in the **desktop OpenSCAD app** (F5 preview, Customizer panel). Prefer no third-party library (inlined `examples/` MIT modules are fine). If BOSL2 is required, the header must say `// requires: BOSL2`. `validate.py` treats `Can't open library` as a compile failure.

## Contents

- [Open the desktop app for the user](#open-the-desktop-app-for-the-user)
- [Hard: compile + bbox](#hard-compile-bbox)
- [Soft: six views](#soft-six-views)
- [Confirm with the user](#confirm-with-the-user)
- [Fallback: still cannot open PNGs](#fallback-still-cannot-open-pngs)
- [Iteration snapshots](#iteration-snapshots)
- [Section](#section)
- [Common parts (required to finish)](#common-parts-required-to-finish)
- [Print-in-place / interference](#print-in-place-interference)
- [Slow or failed renders](#slow-or-failed-renders)
- [Handoff: open the desktop app](#handoff-open-the-desktop-app)

## Open the desktop app for the user

Launch the GUI with the file loaded so the user can inspect it:

```bash
python3 "$SKILL_ROOT/scripts/open-gui.py" model.scad
```

Cross-platform: macOS uses `open -a`, Linux runs the CLI binary, Windows starts `openscad.exe`. Uses the executable `find-openscad.py` found (including a portable install).

Tell the user how to check it:

- **F5** preview (fast), **F6** full render. Drag to orbit, scroll to zoom, right-drag to pan.
- **Window → Customizer** to open the slider panel; the intended knobs are there, `[Hidden]` collapsed. Before Done, `extract-params.py` must print **no `warnings`**.
- **View → Thrown together / CGAL** to compare preview vs render when a boolean looks wrong.
- **File → Export → STL / 3MF** when the shape is right.
- If the app errors on a `use`/`include`, the file needs that library installed (header lists it). Do not ship a new model that way unless the user asked for BOSL2.

`SKILL_ROOT` is this skill’s directory (the folder that contains `SKILL.md`).

Confirm the CLI first (do not install until the user agrees):

```bash
python3 "$SKILL_ROOT/scripts/find-openscad.py"
```

If the CLI is missing: **stop**, show the script hint (package-manager commands are for the **user**). Do not pass `--ensure` until they agree. `--ensure` only installs a portable build (no administrator rights). Still missing: hard gate fails; write “no images”.

## Hard: compile + bbox

```bash
python3 "$SKILL_ROOT/scripts/validate.py" model.scad
python3 "$SKILL_ROOT/scripts/validate.py" model.scad --expect 80 80 5 --tol 1
```

JSON includes `ok`, `stl`, `size`, `triangles`, `volume_mm3`, `openscad_log_tail`. Exit **0** pass; **1** compile fail; **2** bbox miss; **3** multi-body (`--single-body`).

| Failure | Action |
|---|---|
| Exit 1 (error / empty STL) | Fix SCAD; if a boolean ate the part, start from a cube and add features back |
| Exit 2 (bbox miss) | Check plan numbers and origin, then SCAD |
| Exit 3 (multi-body) | One-piece: floating parts — fix connectors. Print-in-place: declare `single_body: 0` and skip the flag. Split: **expected** on `part="all"` — do not `--single-body` the default root; run `--single-body` per token. Do **not** `union()` the assembly to pass the check |
| volume ≈ 0 | Difference removed the solid |

On complex, `--expect` uses Brief `bbox_xyz_mm` in the `origin_convention` axis order X Y Z. Default tolerance 1 mm. That envelope is the **default file** (one-piece solid, or `part="all"` assembled bbox). Do not use it as `--expect` for `part="lid"`.

Simple must at least compile. If the user gave overall sizes, compare bbox too.

**`--single-body` is opt-in.** `validate.py` never reads `brief.json`. Choose:

| Model | `--single-body` | `--expect` |
|---|---|---|
| One-piece | Required on the default file | Overall bbox if known |
| Print-in-place (`single_body: 0`) | **Skip** | Overall bbox |
| Split, default (`part="all"`) | **Skip** (multi-body is the assembly) | Assembled bbox |
| Split, each printable token | **Required** `--openscad-arg=-D --openscad-arg='part="lid"'` | **Skip** overall `--expect` |

```bash
# One-piece
python3 "$SKILL_ROOT/scripts/validate.py" model.scad --expect 80 80 5 --tol 1 --single-body

# Split
python3 "$SKILL_ROOT/scripts/validate.py" model.scad --expect 80 80 40 --tol 1
python3 "$SKILL_ROOT/scripts/validate.py" model.scad --single-body \
  --openscad-arg=-D --openscad-arg='part="base"'
python3 "$SKILL_ROOT/scripts/validate.py" model.scad --single-body \
  --openscad-arg=-D --openscad-arg='part="lid"'
```

Do not wrap `all` in `union()` to fake a single body. Six views of the default file show the assembly (or the one piece). Split: also open one iso of each printable token in **print pose** — do not edit the file default; pass `-D`:

```bash
python3 "$SKILL_ROOT/scripts/preview.py" model.scad .openscad-preview/lid-iso.png iso \
  --openscad-arg=-D --openscad-arg='part="lid"'
```

`--check-floating` on `part="all"` will treat the lid as a second island. Run it per token:

```bash
python3 "$SKILL_ROOT/scripts/section.py" model.scad --check-floating \
  --openscad-arg=-D --openscad-arg='part="lid"'
```

Do not export STL from `part="all"` as the print file.

If the CLI can render, six views are required (simple and complex). If it cannot, state “no images” and why.

## Soft: six views

**Write PNGs under the workspace**, not `/tmp`. Many agent image viewers only accept paths inside the project workspace. `/tmp/...` often fails even when the PNG is valid.

Default output directory (when you omit `outdir`):

```text
model.scad
.openscad-preview/          # six views + _probe.png; add to .gitignore
  model-iso.png
  ...
```

Smoke test before batch-rendering:

```bash
python3 "$SKILL_ROOT/scripts/multi-preview.py" --probe model.scad
# → .openscad-preview/_probe.png (kept on disk so you can open it)
```

Open that probe. If it fails, check the path is **workspace-relative**, not `/tmp`. Then batch-render:

```bash
python3 "$SKILL_ROOT/scripts/multi-preview.py" model.scad
# or explicitly:
python3 "$SKILL_ROOT/scripts/multi-preview.py" model.scad .openscad-preview
```

Do **not** use `/tmp/model-views` unless you will copy PNGs into the workspace before opening them.

Writes `iso` `front` `back` `left` `right` `top` at 800×800 8-bit RGB (no alpha, non-interlaced). **Open** each PNG; do not trust filenames.

Append extra views when needed:

```bash
python3 "$SKILL_ROOT/scripts/multi-preview.py" model.scad .openscad-preview iso top bottom
python3 "$SKILL_ROOT/scripts/preview.py" model.scad .openscad-preview/model-front.png front
```

| Feature | Prefer |
|---|---|
| Holes, arrays, honeycomb | `top` or the face that has the feature |
| Height, walls, cavities | `front` / `left` |
| Flat bed, chamfer | `bottom` (extra image) |
| Overall likeness | `iso` |

Open for:

- [ ] Overall shape matches the request (a cup is a cup)
- [ ] Named features are present (holes, slots, handle, honeycomb)
- [ ] **No floating parts** — every solid connects to the main body (check with `section.py` if unsure)
- [ ] No breaks, floaters, or difference cuts through the part
- [ ] Proportions are not a sheet or a brick unless asked
- [ ] Printable parts have a bed face; overhangs look < 45° or you stated supports / reorient / split
- [ ] Split models: each `part` token looks like one printable piece on the bed (not the assembled pose)
- [ ] Split models: **assembled section through the joint** (2D) opened — remaining wall is not a knife edge; male seats in female with a gap
- [ ] Colored parts did not swallow each other

Fix only what the current PNG shows. Same issue for 3 rounds without converging → stop and ask.

## Confirm with the user

After rendering six views, **show the user iso + top** and ask in the user’s language:

> Does the shape look right? Anything to change?
>
> Check especially: any floating parts? (Looks attached, but is actually separate.)

If they attached a **reference image**, show that image together with iso + top and ask whether the shape **matches the photo or drawing** — not only whether it “looks right”. Details: [reference-image.md](reference-image.md).

Wait for the user to say OK. If they say it is wrong, go back to Plan (complex) or rethink geometry (simple). If large supports remain and a split trigger fires, return to Confirm (`brief.json` `print`), then rewrite plan and SCAD — do not add `part` in place. If it stays one piece, **say “one piece, no split”** in that same turn. Do not mark Done until the user confirms.

**Why**: the agent can spot broken geometry and wrong hole positions, but cannot spot "user wanted round, the agent made it square". The user is the only judge of design intent.

## Fallback: still cannot open PNGs

When workspace PNGs still cannot be opened after fixing the path (not `/tmp`), use this checklist — do not block on images alone:

1. **Hard gate still runs.** `validate.py` (compile + bbox) does not need images. It must pass.
2. **2D sections** (also default to `.openscad-preview/`):

```bash
python3 "$SKILL_ROOT/scripts/section.py" model.scad --plane xy --depth 10 --2d
```

3. **Pixel outline** — `outline.py` reads PNG bytes from disk (works even when the image viewer cannot):

```bash
python3 "$SKILL_ROOT/scripts/outline.py" .openscad-preview/model-top.png
python3 "$SKILL_ROOT/scripts/outline.py" .openscad-preview/model-iso.png
```

4. **Tell the user** what you checked and that opening the PNG failed despite workspace paths.

A failed open on a `/tmp` path is usually a **path mistake**, not a broken viewer. Fix the output directory first; reserve this fallback for genuine open failures.

## Iteration snapshots

The working copy stays the `.scad` you are editing. History is per **round** under `.openscad-iter/NNN/` in that file’s folder. Do not rename the working file to `model_003.scad`.

```text
models/m5-flange/model.scad
models/m5-flange/.openscad-iter/
  001/
    model.scad
    model-iso.png
    model-top.png
    note.txt
```

`.scad` and PNGs in one round directory must be **the same round’s bytes**. Do not edit `001/` later. Do not `git add` `.openscad-iter/`. Store only files you touched this round plus the images you used to judge.

### When to snapshot

| Case | Action |
|---|---|
| Complex, after every render | Snapshot (including round 1) |
| Simple, first pass succeeded | Optional |
| About to change geometry a second time | Snapshot the current render first if 001 does not exist |
| Top-level numbers only, no new geometry intent | Skip |
| This round used a section | Pass the section PNG into snapshot too |

A round is one defect, one edit, one render — not every slider nudge.

```bash
python3 "$SKILL_ROOT/scripts/snapshot.py" path/to/model.scad --reason "shift holes +5 X" \
  .openscad-preview/model-iso.png .openscad-preview/model-top.png
```

`snapshot.py` needs at least one PNG. Default **iso + the view used to judge**. stdout `pngs=` / `prev_pngs=` are the paths to open.

### Compare

1. Open `pngs=` for this round
2. If `prev_dir` is set, open `prev_pngs=` (same view names)
3. Tell the user in one sentence what changed and whether the image improved
4. Not good enough → edit the working `.scad` → render → snapshot a new number

## Section

**One-piece:** optional — use when six views still hide cavities, wall thickness, through-holes, or honeycomb cutting a solid ring.

**Split:** a gate. Open one **assembled section through the joint** (`part="all"`, `--2d`). Depth is the cut plane from the Plan (must sit inside the bbox). Do not skip this because six views exist. Do not measure millimetres off the PNG; look for remaining wall, lip/pin thickness, and a mating seam (not fused, not a void).

```bash
# Split — assembled section through the joint (required)
python3 "$SKILL_ROOT/scripts/section.py" model.scad --plane xz --depth <joint> --2d
# One-piece cavity / wall when six views are not enough
python3 "$SKILL_ROOT/scripts/section.py" model.scad --plane xy --depth 10 --2d
# Optional 3D cutaway (camera faces the cut; not a wall drawing)
python3 "$SKILL_ROOT/scripts/section.py" model.scad --plane xz --depth 0 --3d
```

| Flag | Meaning |
|---|---|
| `--plane xy\|xz\|yz` | OpenSCAD **Z-up**: xy cuts z, xz cuts y, yz cuts x |
| `--depth` | Position on that axis (mm), default 0 |
| `--invert` | Keep the greater-or-equal side instead of less-or-equal |
| `--2d` | **Default.** `projection(cut=true)` true 2D cut, upright (z up on xz/yz) |
| `--3d` | Half-space cutaway. Default camera **faces the cut** (xz→back, yz→left, xy→top) |
| `--view` | Override camera. `--2d` still defaults to `top` |
| `--check-floating` | Auto-generate 9 sections (3 per axis) and detect floating parts |

**Use `--2d` for cavities, wall thickness, rabbets, and lid joints.** `--3d` is a leftover half of the solid (F6 `intersection` with a huge cube). The cut is capped; it is not a GPU clip and not a hatched drawing. Combined with the old default `iso` camera, a hollow box reads as an intact exterior with one face squared off (rounded front, flat back). Do not treat that PNG as the cavity check. If you still want a 3D cutaway, pass `--3d` and leave the camera on the facing default — do not pass `--view iso` unless you mean to look at the uncut shell.

Coordinates are OpenSCAD Z-up.

If a boolean section is slow or fails, confirm `--depth` is inside the bbox (`validate.py` `min`/`max`).

### Floating parts detection

`--check-floating` generates 9 sections (25%, 50%, 75% of each axis) and counts isolated regions in each 2D section. A single connected part should show 1 region per section; floating parts create multiple regions.

```bash
python3 "$SKILL_ROOT/scripts/section.py" model.scad --check-floating
# Split token (do not run on part="all"):
python3 "$SKILL_ROOT/scripts/section.py" model.scad --check-floating \
  --openscad-arg=-D --openscad-arg='part="lid"'
```

Output:
- `✓ No floating parts detected` — all sections show single connected region
- `⚠ Floating parts detected` — multiple sections show isolated regions; check PNGs in `.openscad-preview/`

**How it works**: Sections are rendered upright (z up) with the short axis stretched (≤20×) so flat parts stay readable — a 40×4 flange side view otherwise renders as a hairline where holes are 1–2 px wide. Stretching preserves topology, so connectivity checks stay valid. Holes (bolt holes, slots) create multiple regions in a *single* section, but not across *multiple* sections of the same plane. Floating parts create multiple regions in *most* sections of a plane. The tool uses majority vote: if >50% of sections in a plane show multiple regions, it's likely floating.

**When to use**: After `validate.py --single-body` reports multi-body (exit 3) on a **one-piece** file or a **printable token**. Do not use `--check-floating` on split `part="all"` (separate bodies are the assembly). Pass `--openscad-arg` for the token.

**Limitations**: Cannot detect floating parts that are perfectly aligned with section planes (rare). Use `validate.py --single-body` as the primary check; `--check-floating` is a diagnostic tool.

## Common parts (required to finish)

| Type | Must see |
|---|---|
| Cup / vase | Cavity, bottom, opening; handle connected if present |
| Flange / washer | OD, ID, thickness; bolt holes on the PCD |
| Angle bracket / stand | Two wings connected; holes did not cut the boss if the design has one |
| Enclosure / box | Walls, opening, inner cavity; lid has clearance. Confirm with `--2d` section, not `--3d` iso |
| Split box + lid | `part="all"` assembled; `part="base"` / `part="lid"` each one body, bed face; **assembled section through the joint** (2D) shows remaining wall, not a knife edge |
| Phone stand | Slot ≥ thickness + gap; backrest; base that does not tip |
| Threaded jar / screw | Matching handedness; runout or chamfer |
| V-assembly | Correct angle; moving parts can rotate (`crank_angle` or similar) |
| **Multi-level part** | **Vertical connectors between levels** (no floating top plate) |
| **Bracket with boss** | **Boss connects to base** (not floating above it) |

## Print-in-place / interference

When two parts must move, add a debug switch and paint overlap red:

```openscad
module check_collision() {
    if (show_overlap)
        color("red", 0.8) intersection() { children(0); children(1); }
    %children(0);
    children(1);
}
```

Red in the motion range → increase clearance (see print.md). Do not scale the whole model to hide a clash.

## Slow or failed renders

`--viewall --autocenter` still black or cropped: check the model is near the origin and sizes are non-zero. Fix geometry before chasing cameras.

STL is slower than PNG. Locate shape with PNG first, then `validate.py`. If the local OpenSCAD has a Manifold backend:

```bash
python3 "$SKILL_ROOT/scripts/validate.py" model.scad --openscad-arg=--backend=Manifold
```

If that flag errors on an old build, drop it and continue.

## Handoff: open the desktop app

After the Done-when checklist passes, **do not stop at the file path**. Launch the GUI so the user lands on the part, not on a file-manager window:

```bash
python3 "$SKILL_ROOT/scripts/open-gui.py" model.scad
```

Then tell the user in one line: "Opened in OpenSCAD — F5 to preview, Window → Customizer for the knobs." If the user already said they do not want the GUI (headless CI, remote session), skip and say so.

**Ask the user to confirm** in their language whether they can see it and whether the shape looks right. If they report a problem, do NOT mark Done — fix and re-verify. Only mark Done when the user says OK.
