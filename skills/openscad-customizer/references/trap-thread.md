# Trapezoid helix thread (MIT)

Load this when the part needs a **printable screw thread** (jar lid, stud, nut). Copy the marked modules from [examples/trap-thread.scad](../examples/trap-thread.scad) into `model.scad`. Do **not** pull BOSL2 only for this.

## What to copy

From `// --- copy from here` through `// --- copy until here ---`:

- `male_thread(d_major, d_minor, pitch, length, right_hand, segs_per_turn)`
- `thread_tooth(d_major, d_minor, pitch)`

The demo stud / nut is a sample. Clip the helix with `intersection() { male_thread(…); cylinder(h=length, d=d_major+…); }`.

## Rules

- **Female** = `difference` of an **enlarged** `male_thread` (add `2 * fit_gap` to both diameters). Gap on the nut / lid only — same handedness.
- `fit_gap` about 0.3–0.4 mm for FDM; Hidden.
- Right-hand is the default (`right_hand = true`).
- This is a trapezoid approximation, not a full ISO 68-1 table. Fine / NPT / ACME: use a size table or ask; still use this helix unless the user asked for BOSL2.
- License is MIT. Do not `use <BOSL2/threading.scad>` for a jar or stud.
