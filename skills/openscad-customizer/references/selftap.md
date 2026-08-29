# Plastic self-tap hole (MIT)

Load this when a **machine screw taps into printed plastic** (no heat-set insert). Copy the marked block from [examples/selftap.scad](../examples/selftap.scad) into `model.scad`.

Geometry follows [OpenEng](https://gitlab.com/bath_open_instrumentation_group/openeng) (MIT): a rounded triangle (`trylinder`) at 75% tap diameter.

## What to copy

- `tap_diameter(screw_d, pitch)` / `metric_coarse_pitch(screw_d)`
- `trylinder` / `selftap_hole` / `selftap_hole_metric`

Keep the OpenEng URL in a comment next to the copy block.

## Rules

- **Not** a brass heat-set boss (that is a round insert-OD hole, undersize for knurl).
- **Not** a clearance hole (that is [polyhole.md](polyhole.md) / a round drill).
- Default `splodge` 0.2 mm (FDM extra). Hidden.
- Coarse pitch table covers M2–M6. Other sizes: pass `pitch` into `tap_diameter` yourself.
- Do not copy OpenEng `filleted_cube` (Minkowski). Bed edges stay chamfered in 2D.
