# Brief and plan

Only for **complex** parts. Do not write these files on simple.

They live next to the entry `.scad` (same folder).

- `brief.json` — intent compressed to numbers and checks
- `plan.json` — CSG steps; fillets belong in the sketch

Units are always mm. Record the origin in the brief; measure bbox in that same frame.

## Contents

- [Research (before Brief)](#research-before-brief)
- [Brief](#brief)
- [Plan](#plan)
- [Editing an existing model](#editing-an-existing-model)

## Research (before Brief)

Mating parts need real millimetres. Do not guess. Prefer, in order: (1) sizes the user typed, (2) numbers on a user-attached dimensioned view after Confirm, (3) the **in-skill tables below**. If they attached a photo, CAD view, or drawing, read [reference-image.md](reference-image.md) **before** Brief — topology from the image; millimetres still from those three sources.

### In-skill size tables

| Part type | Example |
|---|---|
| Phone / tablet | iPhone 15 Pro: 146.6 × 70.6 × 8.25 mm |
| Connector | USB-C receptacle: 8.94 × 7.35 mm |
| Bearing | 608: 8 × 22 × 7 mm |
| Bolt / screw | M5 clearance: 5.3 mm (normal fit) |
| Keycap | Cherry MX: 18 × 18 mm top, cross socket |
| Material | PETG: 230-250°C, 0.2-0.5% shrinkage |
| Printer | Prusa MK4: 250 × 210 × 220 mm bed |

### How to cite

In `brief.json`, add a `sources` array:

```json
{
  "sources": [
    "iPhone 15 Pro: skill table 146.6 × 70.6 × 8.25 mm",
    "608 bearing: skill table 8 × 22 × 7 mm"
  ]
}
```

User-attached photos or drawings go in the same array as `user-attached: <filename>` (see [reference-image.md](reference-image.md)). A photo is not a millimetre source.

### When to skip research

- User gave all sizes
- Common knowledge (M5 bolt → 5.3mm clearance)
- Generic geometry (fillet, chamfer, rib)

An attached photo or undimensioned drawing is **not** “user gave all sizes”. Still use the in-skill table or ask for a scale size when the image has none. See [reference-image.md](reference-image.md).

### When research fails

If those sources are missing or ambiguous, ask the user for **1–3 critical sizes** plus usage context (use case, load, environment, material). State the defaults you used.

## Brief

Keep fields that compile and can be checked with a bounding box. Hole diameters and fillet radii are not hard gates.

**After writing `brief.json`, show the user a summary and wait for OK before writing SCAD.** This is the Confirm gate — do not skip it.

Show:

1. **bbox size** (L × W × H)
2. **Key features** (MUST statements in `special_features`)
3. **Visible Customizer knobs** — `key_parameters` is **only** those knobs (≤6 simple / ≤8 complex), with defaults. One extra line: Hidden literals (standard fits, `fit_gap`) vs derived in-module (`outer`, lip from `T`). Do not list every millimetre as Exposed.
4. **Print orientation** (which face on the bed, and why)
5. **Print strategy** — printable complex: one-piece vs split, with a recommendation (wall angle or hard driver). User wording (“split / easier”) is not the decision. Wait for OK before a split `plan.json`. If Confirm chose one piece, say **one piece, no split** in the summary. Simple parts skip JSON but still say one piece on delivery.
6. **Reference reading** (if they attached images) — topology you took from the picture, millimetres you did **not** take from it, and what is still unclear. Cite files in `sources` (`user-attached: front.png`). Do not skip Confirm because you saw the image. Details: [reference-image.md](reference-image.md).

Ask in the user’s language whether this is what they wanted and whether anything should change. Wait for the user to say OK. If they change something, update `brief.json` first, then write SCAD.

If a split trigger fires **after** SCAD already exists (six views, still large supports): do not add a `part` enum in place. Update `brief.json` `print`, re-Confirm, then rewrite `plan.json` and the `.scad`.

Optional `print` object (omit = one piece, current behavior):

```json
"print": {
  "strategy": "one_piece",
  "orientation": "Flange on the bed"
}
```

Split:

```json
"print": {
  "strategy": "split",
  "parts": [
    { "id": "base", "qty": 1 },
    { "id": "lid", "qty": 1 }
  ],
  "joint": "rabbet on the rim; host wall 2.0; lip 1.0 high × 0.8 wide; gap 0.25 on the groove"
}
```

| `print.strategy` | `single_body` in verification | `part` enum |
|---|---|---|
| omitted / `one_piece` | `1` — `--single-body` on the default file | none |
| `print_in_place` | **must be 0** — skip `--single-body` | none |
| `split` | do **not** set 0 to mean “the assembly is one solid”; `all` is multi-body; each token is one body | required |

`bbox_xyz_mm` is the **assembled** envelope (`part="all"`). Do not use it as `--expect` for `part="lid"`.

```json
{
  "part_name": "honeycomb-angle-bracket",
  "part_category": "L-bracket",
  "length_unit": "mm",
  "origin_convention": "corner_min",
  "primary_workplane": "XY",
  "bbox_xyz_mm": [80, 80, 80],
  "key_parameters": {
    "flange_length": 80,
    "bracket_width": 80,
    "thickness": 5,
    "hex_flat_to_flat": 12
  },
  "special_features": [
    "MUST keep a solid ring around each hole; honeycomb must not cut the boss.",
    "MUST be a single 90-degree bracket, not two separate plates."
  ],
  "verification_targets": [
    { "id": "overall-x", "kind": "overall_dimension", "axis": "x", "nominal": 80, "tol_mm": 1 },
    { "id": "overall-y", "kind": "overall_dimension", "axis": "y", "nominal": 80, "tol_mm": 1 },
    { "id": "overall-z", "kind": "overall_dimension", "axis": "z", "nominal": 80, "tol_mm": 1 },
    { "id": "compile", "kind": "compiles", "nominal": 1 },
    { "id": "single-body", "kind": "single_body", "nominal": 1 }
  ],
  "manufacturing_method": "3d_print_fdm",
  "user_request_raw": "90-degree honeycomb angle bracket, 80x80, t=5, M5 holes",
  "sources": [
    "M5 clearance hole: ISO 273 normal fit (5.3 mm)"
  ]
}
```

`origin_convention` values:

| Value | Meaning |
|---|---|
| `corner_min` | Minimum corner at the origin; +X/+Y/+Z grow the part |
| `centroid_on_base_plane` | Origin at the bed-face center; Z=0 on the bed |
| `axis_on_z` | Revolved part, axis along Z |

Each `special_features` line is a **MUST** imperative that bbox alone cannot cover.

`verification_targets` may only be: `overall_dimension` (x/y/z), `compiles`, `single_body`. Add `watertight` only as a soft declaration when needed. On split models, `overall_dimension` / `--expect` apply to `part="all"` only; per-token checks are `compiles` + `--single-body` with `-D part="…"`.

## Plan

Allowed step types: `extrude` / `revolve` / `hole` / `union` / `cut` / `pattern_linear` / `pattern_circular` / `mirror`. Fillets are described on the sketch, not as a later 3D round.

```json
{
  "plan_id": "honeycomb-angle-bracket-v1",
  "brief_id": "honeycomb-angle-bracket",
  "origin_convention": "corner_min",
  "sketches": [
    {
      "id": "flange-xy",
      "plane": "XY",
      "notes": "80x80 rectangle; inner corner offset(r=5); hex grid cut; hole bosses kept solid"
    }
  ],
  "steps": [
    { "id": "s1", "type": "extrude", "sketch_id": "flange-xy", "distance_mm": 5, "label": "Base flange" },
    { "id": "s2", "type": "extrude", "label": "Upright flange", "notes": "Same profile on XZ, thickness 5, union with s1; inner corner already rounded in 2D" },
    { "id": "s3", "type": "hole", "hole_diameter_mm": 5.3, "notes": "Two holes per flange; Ø5.3 from M5 table (Hidden), not a key_parameter" }
  ],
  "key_dimensions": { "bbox_xyz_mm": [80, 80, 80] },
  "notes": "Add first, cut second. Honeycomb is a 2D cut before extrude, not a 3D boolean after."
}
```

### Plan rules

1. Add first, subtract second. If you `cut` after a pattern or mirror, name the target in notes.
2. Fillets: `offset(r=…)`, polygon rounds, or an explicit note that `minkowski` will round the bed face.
3. Symmetry is a sketch or a `mirror` step, not a verbal “and the other side”. Orthographic reference views map onto `sketches[]`; name the source view in `notes`.
4. `notes` are geometry only (plane, direction, distance). For a split, put the cut plane and the same checkable joint string as `print.joint` (type, host wall `T`, derived size, gap on female) in `notes` — do **not** add a new step `type`.
5. Shells: inner contour then `difference`.
6. Bbox mismatch: fix plan numbers first, then SCAD. Missing body / two bodies / flipped axes → return to the plan; do not only twist parameters. On split, “two bodies” on `part="all"` is expected; two bodies on `part="lid"` is a defect.

## Editing an existing model

If the user wants a change and did not say “start over”: do not rewrite Brief/Plan. Change top-level assignments or a local module.

Packaging (info, covers, import folder) is **vary3d-package** (separate skill; do not install it for them), not this file.

Starting over: new slug folder, or replace `brief.json` / `plan.json` in place and say the old geometry is discarded.
