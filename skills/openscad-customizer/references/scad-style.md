# OpenSCAD Customizer style

Goal: the desktop Customizer can edit top-level assignments, and the CLI can compile. OpenSCAD only treats assignments **before the first `module` / `function`** as knobs. Helper parameters on the first `module` with no literal default are not sliders.

## Contents

- [File skeleton](#file-skeleton)
- [Customizer](#customizer)
- [Structure](#structure)
- [Split models: `part` enum](#split-models-part-enum)
- [Connectivity](#connectivity)
- [Color](#color)
- [Fillets and chamfers](#fillets-and-chamfers)
- [Libraries](#libraries)
- [Editing an existing file](#editing-an-existing-file)

## File skeleton

```openscad
// Short one-liner: what the part is, and a print hint if useful.
$fa = 4;
$fs = 0.4;

/* [Dimensions] */

// Length of each flange from the outer corner.
flange_length = 80; // [40:1:150]

/* [Features] */

// Cable channel through the front lip.
cable_slot = true;

/* [Rendering] */

// Mid-tone hex so a light preview does not wash out.
bracket_color = "#4A7C6F"; // color
show_honeycomb = true;

angle_bracket();

module angle_bracket(
    flange_length = flange_length,
    cable_slot = cable_slot,
    bracket_color = bracket_color
) {
    color(bracket_color)
    // Add first, cut second; fillets live in the 2D profile
    union() {
        // ...
    }
}
```

## Customizer

| Rule | How |
|---|---|
| Groups | `/* [Group Name] */` on its own line |
| Description | `// …` on the **line above** the assignment, written for the slider user |
| Numeric slider | `name = 80; // [40:1:150]` → min:step:max |
| Enum | `mode = "hex"; // [hex:Hex, square:Square]` |
| Boolean | `cable_slot = true;` is normal on desktop Customizer |
| Color | Parameter name ends with `_color`; default `"#RRGGBB"` (or an SVG color name); trailing `// color` |
| Hidden | Expert / variant overrides that must stay literals (`fit_gap`, standard OD). Not a dump for values computed from knobs |
| Names | Full `snake_case`: `flange_length`, not `fl` |

Comments, group titles, slider labels, and in-module notes are **English** unless the user explicitly asked for another language. Chat language does not count. Replies in chat still follow the user.

Assignments must be **literals**. Do not put `width = base * 2;` before the first module — that is not an editable slider. Derived values go **inside** the module (locals at the top of the body). Module arguments = visible + Hidden literals only.

**Three layers** (same table as SKILL.md Few knobs): visible knobs = product; Hidden literals = assignable overrides; derived names = module locals. Pick one side of a pair as the knob. Guard with `min` / `max`. Male/female share a nominal; `fit_gap` on the female only.

```openscad
/* [Dimensions] */

inner_length = 80; // [40:1:200]
wall = 2; // [1.6:0.2:4]

/* [Hidden] */

fit_gap = 0.25; // [0.1:0.05:0.6]
bed_chamfer = 0.6; // [0:0.1:1.2]

module box(
    inner_length = inner_length,
    wall = wall,
    fit_gap = fit_gap,
    bed_chamfer = bed_chamfer
) {
    // Derived locals — not top-level, not extra knobs
    outer_length = inner_length + 2 * wall;
    lip_w = min(0.8, wall - 1.2);
    // geometry uses outer_length / lip_w / fit_gap
}
```

**Few knobs, derived rest.** Numbers in the request are defaults, not a slider list. Visible cap: simple **≤ 6**, complex **≤ 8** (including `part` and one color) — a ceiling, not a quota (typical 3–5). Grouping does not raise it. **Mate holder** (coin / bearing / phone stand): visible sizes are the object’s mating dims only; cradle geometry is derived. Allow: SKU envelope, named feature on/off (only what they asked), shell `wall` when the shell *is* the product, one `*_color`, `part` when required. Deny unless they asked to retune it: `gap`, `reveal_ratio`, `arm_w`, `plate_t`, `lip_h`, `label_size`, `tilt_deg` / `fold_angle`, standard-part fits, `bed_chamfer` / `fit_gap`. Features you invented are not knobs. `extract-params.py` must print **no warnings** before Done.

Helper modules with no literal defaults must not be the first `module` in the file. Put helpers **after** the main module.

If the user later packs for Vary3D, labeled `"yes"` / `"no"` enums are more stable on the site panel than bare booleans. Do not rewrite working booleans just in case.

## Structure

- One main module, called once at the bottom of the file.
- Repeated features become child modules (hole grids, honeycomb, ribs, rounded boxes). Children go **after** the main module.
- **Split for print (2–4 kinds):** one `part` enum, default `"all"`. See the skeleton below and [print.md](print.md). Do not add `show_<part>` booleans. Feature on/off stays `show_honeycomb`; sections stay `cutaway`.
- One-piece assemblies that are still a single printable solid: no `part` knob. Optional `cutaway = "none"; // [none, right, front]`.
- `$fn` only for polygonal features (hex, gear). Overall resolution uses `$fa` / `$fs`.
- Preview vs render: `$fn = $preview ? 32 : 64;` only on expensive revolves.

## Split models: `part` enum

Token names match the module (`base`, `lid`, `leg`). Labels are English. Geometry for a kind is defined **once**. A printable token must not call the placer that arrays that kind.

```openscad
/* [Rendering] */

box_color = "#2A9D90"; // color

// All = assembled preview. Pick a kind to export STL (slice extras in the slicer).
part = "all"; // [all:All, base:Base, lid:Lid]

module box() {
    if (part == "all") {
        color(box_color) base_print();
        color(box_color) lid_geom();
    } else if (part == "base") {
        color(box_color) base_print();
    } else if (part == "lid") {
        color(box_color) lid_print();
    }
}

// Assembly pose only. part == "lid" uses lid_print() at the origin instead.
module lid_geom() {
    translate([0, 0, base_h]) lid_print();
}

module base_print() {
    cube([box_w, box_d, base_h]);
}

module lid_print() {
    cube([box_w, box_d, lid_h]);
}

box();
```

Identical copies (four legs): **one** dropdown value `leg`. Same `if (part == …)` shape as the box: `all` calls the placer; the printable token does not.

```openscad
part = "all"; // [all:All, top:Top, leg:Leg]

module table() {
    if (part == "all") {
        color(box_color) top_print();
        place_legs() leg_geom();
    } else if (part == "top") {
        color(box_color) top_print();
    } else if (part == "leg") {
        color(box_color) leg_print();
    }
}

module place_legs() {
    for (p = [
        [inset, inset],
        [table_w - inset, inset],
        [inset, table_d - inset],
        [table_w - inset, table_d - inset]
    ])
        translate([p[0], p[1], 0]) children();
}

module leg_geom() {
    translate([0, 0, -leg_h]) leg_print();
}

module top_print() {
    cube([table_w, table_d, top_h]);
}

module leg_print() {
    cylinder(d = leg_d, h = leg_h);
}

table();
```

Tell the user **Print 4× leg**. Chirality (left/right that cannot stack): two tokens or a `side` enum. Off-the-shelf fasteners: not a `part` value.

**Joints:** one set of named constants (from `wall` / host thickness `T`, or Hidden literals). Male uses the nominal; female adds `fit_gap` only. Put the joint in `*_print()` so the export pose is the print pose. See [print.md](print.md) Joints.

## Connectivity

Every solid must connect to the main body. Floating parts look fine in preview but fall apart when printed. On a **split** model this applies **per printable token** (`part="lid"` is one piece). Do not add columns between base and lid just to pass `--single-body` on `part="all"`.

### Common mistakes

| Mistake | Example | Fix |
|---|---|---|
| **Floating top plate** | `cube([80,80,5]); translate([0,0,50]) cube([80,80,5]);` | Add vertical columns connecting the two plates |
| **Floating boss** | `cylinder(d=40,h=5); translate([0,0,10]) cylinder(d=20,h=5);` | Boss starts at Z=5 (top of flange), not Z=10 |
| **Floating rib** | `cube([80,80,5]); translate([10,10,10]) cube([60,60,5]);` | Rib starts at Z=5 (top of base), not Z=10 |
| **Floating honeycomb** | `cube([80,80,5]); for(...) translate([x,y,10]) cube([8,8,5]);` | Honeycomb starts at Z=5 (top of base) |

### How to avoid

1. **After `union()`, ask yourself**: "If I keep only this body, would it fall?" If yes, add a connector.
2. **Use `hull()` to connect distant parts**:
   ```openscad
   hull() {
       cube([80, 80, 5]);           // base
       translate([0, 0, 50])
           cube([80, 80, 5]);       // top plate
   }
   ```
3. **Add vertical connectors**:
   ```openscad
   union() {
       cube([80, 80, 5]);           // base
       translate([0, 0, 50])
           cube([80, 80, 5]);       // top plate
       for (x = [0, 70], y = [0, 70])
           translate([x, y, 0])
               cube([10, 10, 55]);  // four columns
   }
   ```
4. **Check with `section.py`**: floating parts show as separate islands in a 2D section.
   ```bash
   python3 "$SKILL_ROOT/scripts/section.py" model.scad --plane xz --depth 0 --2d
   ```

### When multi-body is intentional

Print-in-place (hinges, chains) and **split** `part="all"` (assembled preview) are multi-body on purpose.

Print-in-place — declare in `brief.json` and **do not pass** `--single-body`:

```json
{
  "verification_targets": [
    { "id": "single-body", "kind": "single_body", "nominal": 0 }
  ]
}
```

`validate.py` does **not** read `brief.json`. Skip `--single-body` yourself when `nominal` is 0 (print-in-place) or when compiling `part="all"` on a split model. Passing the flag anyway yields exit 3.

Split — `print.strategy` is `split`; run `--single-body` only with `-D part="<token>"`. Do not `union()` the assembly.

## Color

OpenSCAD `color()` (2019.05+) accepts:

| Form | Example |
|---|---|
| `#RRGGBB` | `"#4A7C6F"` |
| Short / alpha hex | `"#F80"` / `"#5E6E4ACC"` |
| SVG name | `"olive"` |
| `[r, g, b]` | `[0.37, 0.43, 0.29]` (0–1; not a Customizer color knob) |

```openscad
/* [Rendering] */

// Hull render color.
hull_color = "#4A7C6F"; // color

color(hull_color) hull_body();
```

- Give a literal default. No `undef`, empty string, or missing assignment.
- Trailing `// color` (or `// [color]`) is required for a color picker.
- Wrap the part in `color(hull_color)`; do not hard-code hex inside geometry.
- One color per functional part; do not randomize every cube.
- STL has no color; use 3MF if the file must carry color. Preview (F5) shows `color()`.

Mid-tone defaults read better on a light background than near-white or near-black. Photoreal paint (airliner white, beige enclosure) only when the user asks.

## Fillets and chamfers

| Intent | How |
|---|---|
| 2D outer round | `offset(r = r) offset(delta = -r) square([x, y]);` |
| 2D inner round | `offset(delta = -r) offset(r = r) …` |
| Printable bed edge | **Chamfer** (trapezoid / `multmatrix`), not a spherical Minkowski on the bed face |
| Full 3D round | Avoid; if required, say the bed face will round too |

## Libraries

**Default: none.** Do not create `lib/` under the design folder. Do not `use <MCAD/…>`.

Gears, threads, and FDM holes are MIT snippets you **inline** (copy the marked block into `model.scad`):

| Need | Read | Copy from |
|---|---|---|
| Spur gears | [spur-gear.md](spur-gear.md) | [examples/spur-gear.scad](../examples/spur-gear.scad) |
| Jar / stud / nut thread | [trap-thread.md](trap-thread.md) | [examples/trap-thread.scad](../examples/trap-thread.scad) |
| Vertical FDM hole | [polyhole.md](polyhole.md) | [examples/polyhole.scad](../examples/polyhole.scad) |
| Horizontal FDM hole | [teardrop.md](teardrop.md) | [examples/teardrop.scad](../examples/teardrop.scad) |
| Plastic self-tap (no insert) | [selftap.md](selftap.md) | [examples/selftap.scad](../examples/selftap.scad) |

Fillets, rounded rects, bed chamfers, D-bores, honeycomb: write them in the file (offset / a few modules). Do not invent a helper library for those. Do not copy OpenEng `filleted_cube` (Minkowski).

BOSL2 (`attach()`, path sweeps, a thread form this snippet cannot do) **only** when the user asked or the existing file already `use`s it. Probe with `validate.py` — a missing `use` is a hard fail (`Can't open library`), even if a `cube()` still compiles. If missing: stop. Show this command for the **user** to run. Do not run git clone yourself.

User may run:

```text
git clone --depth 1 https://github.com/BelfrySCAD/BOSL2.git ~/Documents/OpenSCAD/libraries/BOSL2
```

(Linux: `~/.local/share/OpenSCAD/libraries/BOSL2`; Windows: `Documents\OpenSCAD\libraries\BOSL2`.) Wait until they have it. Header: `// requires: BOSL2`. The Vary3D site preview may not load it. Do not clone without consent. Do not pull BOSL2 only to fillet a box or to cut a spur gear.

## Editing an existing file

Before changing anything, read:

1. Every `use` / `include` (report cycles)
2. Top-level Customizer parameters (`python3 "$SKILL_ROOT/scripts/extract-params.py" file.scad`). Any `warnings` → hide, derive, or move formulas into the module before editing further.
3. The main module, `part` enum if present, and feature `show_*` (not `show_<part>`)

Then:

- Size only → top-level assignments
- New feature → new parameter + local module; keep existing group names
- User dropped an STL → `import("part.stl")` and parameterize only what they want to change
- Do not rewrite a file you do not understand
- Packing for Vary3D import is a different skill: **vary3d-package** (separate install; do not install it for them)
