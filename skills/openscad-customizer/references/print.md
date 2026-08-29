# FDM defaults (0.4 mm nozzle)

Read this before writing geometry for a printable part. Numbers are a starting point; user printer / material overrides them.

## Contents

- [Structure](#structure)
- [Orientation](#orientation)
- [Print strategy (do not split by default)](#print-strategy-do-not-split-by-default)
- [`part` enum (2–4 printable meshes)](#part-enum-2-4-printable-meshes)
- [Joints (split only)](#joints-split-only)
- [Export](#export)
- [What to tell the user](#what-to-tell-the-user)

## Structure

| Quantity | Default | Notes |
|---|---|---|
| Wall | ≥ 1.2 mm (2.0 is better) | Thinner walls leak |
| Layer height | 0.2 mm | Align fine features to layer multiples |
| Sliding clearance | 0.3–0.5 mm | Print-in-place 0.4–0.5 |
| Press / snap | Try 0.15–0.25 mm | Start loose; let the user tune |
| Overhang | ≤ 45° | Else reorient, chamfer, **split** (print.md ladder), or declare supports |
| Bed edge | Chamfer 0.4–0.8 mm | Do not fillet the bed (elephant foot + poor adhesion) |
| Holes (vertical) | `polyhole` — inscribed circle = nominal; then +0.2–0.3 if clearance | [polyhole.md](polyhole.md) |
| Holes (horizontal) | `teardrop_hole`, apex +Z | [teardrop.md](teardrop.md) |
| Plastic tap | `selftap_hole_metric` — not a heat-set boss | [selftap.md](selftap.md) |
| Holes (clearance round) | +0.2–0.3 mm over nominal | M3→3.2, M4→4.3, M5→5.3 |
| Min post / rib | ≥ 1.5 mm | Thinner breaks |

Mating to a real object: use user millimetres or the in-skill tables, then add 0.3–0.5 mm envelope (enclosures). User measurements beat the tables.

## Orientation

Prefer a large flat on the bed. Brackets can print on a side to skip supports (one line in the file header; English unless the user asked otherwise).

Unavoidable bridges / overhangs: say so on delivery. Do not claim “support-free” if it is not.

## Print strategy (do not split by default)

Decide in this order. Stop at the first step that works.

1. **Reorient** — largest flat on the bed; put load in XY when you can.
2. **Change geometry** — chamfer to ≤ 45°, bridges, self-supporting roofs.
3. **Split for print** — 2–4 printable meshes plus a joint (parametric, not a mesh chop).
4. **Declare supports** — say so in the delivery lines. Do not claim support-free.

**Default is one piece.** “Design an X” stays one solid. `print.strategy` comes from the ladder + Confirm, **not** from the user’s wording. “Split so it prints easier” is a **hypothesis** — often they assume supports, not a hard need.

**Say it out loud when it stays one piece.** Printable parts always get one explicit line in the user’s language: either **one piece, no split** (plus why: wall angle, bed face) or **split** (`Print N× <token>`). Do not silently skip the split; do not silently split. A flange that was never going to split still gets “One piece; flange on the bed; no supports.”

### Drivers (user said “split”)

Treat that as **enter Confirm**, not skip Confirm. Ask the real reason if it is unclear.

| Kind | Examples | What to do |
|---|---|---|
| **Hard** | Bed too small; shipping / packing; different materials; closed interior roof or downward arm that cannot lie on the bed after reorient / chamfer; user needs one STL per kind as a kit | Recommend **split**. Still wait for OK. Then complex + split `plan.json`. |
| **Soft** | “No supports”, “easier to print”, “split it up”, “more convenient” | Estimate one-piece first (numbers below). Recommend **one piece** when it works. Wait. Honor a later “split anyway” (small bed, gift kit). |

“Export one STL per kind” as a **kit/workflow** ask is hard. The same words meaning “so I don’t need supports” are soft.

Mentioning split does **not** by itself promote to complex. If Confirm picks one piece, route on geometry (a funnel can stay simple).

### One-piece check (before SCAD — from sizes, not a mesh)

Use Brief / user numbers. Overhang is **from vertical** (0° = wall, 90° = shelf). Self-supporting target ≤ 45°.

| Shape | Estimate |
|---|---|
| Cone / funnel / taper (revolve) | `atan(\|r_top − r_bottom\| / height)` in degrees. Wide end on the bed: that is the **inner** wall. |
| Rectangular taper | Same with half-width instead of radius. |
| L-bracket on its back | Upright wing is ~0°; do not split a simple flange. |

**Recommend one piece** when a bed face exists and this angle is ≤ 45°, and there is no closed interior roof / downward arm. **Recommend split** when the angle stays > 45° after reorient / chamfer, or a hard driver applies.

Do not parse `.scad` or slice to decide Confirm. After six views, if large support area remains: ask once; if they agree to split, **return to Confirm** — set `print.strategy` to `split`, wait, rewrite `plan.json` and SCAD. Do not add `part` in place. Do **not** ask on a simple flange.

### Confirm (one-piece vs split)

Ask in the user’s language. Do **not** ask “how many pieces?” first. Binary choice + recommendation + one number:

> Wall ~30° from vertical; one piece, wide end on the bed, no supports. Split only helps a small bed or packing. **One piece (recommended)** or split?

Wait. Split `plan.json` only after they pick split. If they pick one piece: no `part` enum; still **state “one piece, no split”** on Confirm and on delivery.

“No supports” / “support-free” alone is **not** a split trigger — ladder first, then this Confirm.

**Print-in-place and split are mutually exclusive.** Print-in-place: one export, motion gaps 0.4–0.5 mm, `single_body: 0`, no `part` enum. Split: `part` dropdown, joints, separate STLs.

Do not run a mesh “chopper”. Splits are CSG in the `.scad` (modules + `part`).

## `part` enum (2–4 printable meshes)

OpenSCAD exports **whatever is currently visible** as one file. There is no assembly tree. For 2–4 **kinds** of STL, expose one enum — not a part tree.

```openscad
/* [Rendering] */

// Which bodies to build. All = assembled preview; pick one kind to export STL.
part = "all"; // [all:All, base:Base, lid:Lid]
```

| Rule | Detail |
|---|---|
| When | Only if there are 2–4 **kinds** of mesh to export |
| Knob | One enum named `part`, group `Rendering`, default `"all"` |
| Values | `all` plus one token per printable kind (same as the module short name: `base`, `lid`, `leg`) |
| Labels | English: `All`, `Base`, `Lid` |
| One-piece | **Do not** add `part` |
| Instances | Count **kinds**, not copies. `all` places every instance. `part="leg"` draws **one** copy in **print pose** at the origin |
| Quantity | Delivery lines and packaged `info.print`: `Print 4× leg`. Not `variants.json` |
| Mirror that cannot stack | Two tokens, or a `side` enum — not four instance names |
| Hardware | Off-the-shelf screws stay out of the dropdown |

**Hard boundary:** if the file has `part`, do **not** also add `show_base` / `show_lid` (or any `show_<part>` boolean). `show_*` is for **features** (`show_honeycomb`). Section views use `cutaway = "none"; // [none, right, front]`. “Lid plus screws” as an arbitrary combo is a debug view → `/* [Hidden] */`, not the default panel. More than four printable kinds → extra build roots or Hidden switches — **do not** turn the default Customizer into a part tree.

**Code shape:** one module per kind. `*_print()` is the export / bed pose (origin). `*_geom()` is assembly pose only (`translate` / `rotate` then `*_print()`). `place_*() children()` arrays instances in `all`. A printable token calls `*_print()` only — **never** `place_*()`. Do not duplicate geometry.

Prefer **one file + `part`**. Extra files only for shared `params.scad` or a part that must be its own build root. `open-gui.py` opens the root with default `part="all"`.

## Joints (split only)

Do not invent three sliders. Derive joint sizes from the **host wall** thickness `T` at the cut (local section, not the assembled bbox). Compute lip / pin from `T` in the module — do **not** put `lip_h` / `pin_d` as independent Hidden literals. `fit_gap` 0.2–0.3 mm: Hidden, or a module constant (the only joint value that may stay a Hidden literal). Apply the gap **only on the female** (groove / hole). Same named numbers on male and female — do not write two sets, do not `scale()` to make clearance. Cut through a non-structural region. Each printable token must be a single body.

If `T` cannot hold the joint, move the cut, add a local boss, or pick another type. Do not cut a knife-edge lip.

### Pick a type

```
T < 1.8 mm     → rabbet/pin will not leave a remaining wall; move the cut, boss + screw, or do not split
Shell / lid    → rabbet (default)
Alignment      → pin (≥2 pins, or pin + rabbet against rotation)
Load / service → screw (lookup hole + boss)
Dovetail/snap  → not the default menu
```

A U-channel / outer skirt that **adds** overlap instead of eating `T` is still a rabbet: keep host wall `T`, size the skirt from `wall`, put `fit_gap` on the channel.

### Derive (0.4 mm nozzle, 0.2 mm layer)

Prefer the larger number; the minimum is the refuse line.

| Joint | Prefer | Minimum (else change type / cut / boss) |
|---|---|---|
| **Rabbet** | Lip width ≥ 1.2 and remaining `T − width` ≥ 1.2. Lip height 1.0–1.5 (≥ 2 layers, layer multiple) | Width ≥ 0.8, remaining ≥ 1.0, height ≥ 0.8. Typical 2 mm wall: width 0.8, remaining 1.2, height 1.0 |
| **Pin** | `D` ≥ 3; `L` = 1.5–2.5×`D`; hole depth = `L`+0.3–0.5 (must seat); hole = `D`+`fit_gap`; ≥ 1.2 radial solid around the pin | `D` < 3 or remaining radial < 1.2 → boss or another type |
| **Screw** | Skill table (M3→3.2). Plastic engagement ≥ 2.5× nominal, or heat-set OD from the table / the user. ≥ 1.2 solid around the hole | Thin wall: boss first, then the hole |

Lead-in chamfer 0.3–0.5 mm on the pin tip / lip mouth (assembly, not mold draft).

Do **not** expose `rabbet_h`, `rabbet_w`, `pin_d`, or `joint_depth` on the default panel.

### Angles (four different things)

| Kind | Rule |
|---|---|
| Cut plane | World-axis aligned. Each half still has a large bed face. A diagonal cut makes overhangs on both sides |
| Joint in print pose | Lip, pin, and screw hole must be ≤ 45° in that token’s `*_print()` pose. If one half would hang, put the feature on the other half or change type — do not bring supports back via the joint |
| Lead-in | The 0.3–0.5 mm chamfer above |
| Load | Do not cut a member so tension peels layers apart. Prefer a screw through the cut (plastic in compression) |

Pin axis = print Z of that token (round in XY). If it cannot stand up, do not use a round pin.

### Brief string (checkable)

Not prose. Type + where + host wall `T` + derived size + where the gap sits:

```text
rabbet on the rim; host wall 2.0; lip 1.0 high × 0.8 wide; gap 0.25 on the groove
pin; host wall 8.0; two Ø3 × 6; hole depth 6.4; gap 0.25 on holes
screw M3 through the flange; host wall 4.0; boss Ø8; engagement 8; clearance 3.2; gap 0.2 on holes
```

Copy the same sentence into `plan.json` `notes` with the cut plane. Do **not** add a new CSG step `type`. Joint numbers are not a second Confirm — they go in the Plan after the user picks split.

## Export

Do **not** export STL while `part="all"` and call that the print file. Change `part` (or pass `-D`) per kind:

```bash
openscad -o base.stl -D 'part="base"' model.scad
openscad -o lid.stl  -D 'part="lid"'  model.scad
```

Quantity is for the slicer (duplicate `leg.stl`), not extra solids in one STL.

## What to tell the user

In the reply (and optionally in the `.scad` header). Do not dump every slicer checkbox.

Always:

- Settings: material, layer, walls, infill, supports
- Orientation: which face on the bed
- Why: why that pose or recipe
- **One piece or split** — say it even when you did not split. One-piece: `One piece; no split.` plus the wall/bed reason. Split: `Print N× <token>` for each kind; `part="all"` is preview only (not a print export)

If the user later packs for the site, those lines map to `info.print` (`settings` / `orientation` / `why` — put counts or “One piece; no split” in `orientation` or `why`).

Examples of when to leave the defaults:

- Load-bearing hook: 3–4 walls, 25–40% infill, maybe PETG
- Vase / thin wall: 1 wall or vase mode
- Tall skinny: brim
- Outdoor / heat: PETG or ASA, not PLA
- TPU: slow, few supports, extra clearance

Do not promise food-contact safety or an IP waterproof rating unless the user only wants splash resistance and accepts separate seals.

This skill does **not** write `info.json`. If the user wants the print notes as listing Docs on vary3d.com, see **vary3d-package** (separate skill; do not install it for them).
