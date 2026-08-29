# Vertical polyhole (MIT)

Load this when a **vertical** FDM hole must match a bolt (shaft along print Z). Copy the marked block from [examples/polyhole.scad](../examples/polyhole.scad) into `model.scad`. Do **not** `use <MCAD/polyholes.scad>`.

## What to copy

`polyhole_sides()` and `polyhole(h, d, center)`.

A regular n-gon is circumscribed around diameter `d`, so the **inscribed** circle is `d`. Plain `cylinder($fn=…)` inscribes the polygon and prints small.

## Rules

- Vertical holes only. Horizontal → [teardrop.md](teardrop.md).
- Clearance still applies on top (M3 → 3.2) if it is a slip fit, not a tap. Then `polyhole(h, d = 3.2)`.
- License is MIT (clean-room). Do not paste Nophead/MCAD files.
