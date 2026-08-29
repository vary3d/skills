# Involute spur gear (MIT)

Load this when the part needs **spur gears**. Copy the marked modules from [examples/spur-gear.scad](../examples/spur-gear.scad) into `model.scad`. Do **not** `use <MCAD/…>` or BOSL2 for this.

## What to copy

From `// --- copy from here` through `// --- copy until here ---`:

- `spur_gear()` / `spur_gear_2d()`
- `spur_center_distance()` / `spur_mesh_rotate()`
- `_sg_*` helpers (keep the prefix so names do not clash)

The demo `gear_pair` / `part` enum is a sample, not required.

## Rules

- ISO 53 full-depth: addendum `1×m`, dedendum `1.25×m`, pressure angle 20°.
- Tooth on +X. Place the mating gear at `+X` center distance; rotate it by `spur_mesh_rotate(teeth)` so a space faces the pinion (even counts need a half pitch).
- Default `backlash` 0.15 mm at the pitch circle (split across both gears). FDM mesh clearance — Hidden, not a main knob.
- Minimum about **12 teeth**. Fewer undercuts; do not add profile shift in this snippet.
- Straight spur only. Helical / bevel / herringbone: stop and ask (or BOSL2 if the user named it).
- License is MIT (clean-room). Do not paste Frost/MCAD `involute_gears` or `frost_*` names.
