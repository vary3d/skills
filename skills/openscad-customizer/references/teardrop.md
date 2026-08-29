# Horizontal teardrop (MIT)

Load this when a hole runs **parallel to the bed** (shaft in XY). Copy the marked block from [examples/teardrop.scad](../examples/teardrop.scad) into `model.scad`. Do **not** `use <MCAD/teardrop.scad>`.

## What to copy

- `teardrop_2d(d)` — profile, apex on **+Y**
- `teardrop_hole(d, length)` — cutter along **+X**, apex toward **+Z** (45° roof)

Subtract `teardrop_hole` from the solid. If the hole is along Y, `rotate([0, 0, 90])` the cutter.

## Rules

- Apex must point to **+Z** in print pose (the roof). A teardrop pointing sideways still needs supports.
- Vertical holes → [polyhole.md](polyhole.md), not this.
- License is MIT (clean-room). Do not paste MCAD/Thingiverse teardrop.
