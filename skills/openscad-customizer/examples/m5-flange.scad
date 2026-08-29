// M5 bolt flange: OD 40, thickness 4, PCD 28, four clearance holes.
$fa = 4;
$fs = 0.4;

/* [Dimensions] */

// Outer diameter of the flange.
outer_dia = 40; // [20:1:80]

// Plate thickness.
thickness = 4; // [2:0.5:12]

// Center bore.
inner_dia = 10; // [4:0.5:24]

// Bolt circle diameter.
pcd = 28; // [16:1:70]

// Number of bolt holes.
bolt_count = 4; // [3:1:12]

/* [Hidden] */

// M5 clearance (ISO 273 normal fit). Standard-part — not a main knob.
bolt_clearance_dia = 5.3; // [3:0.1:8]

// Bed-face chamfer (elephant-foot relief). Print detail — most users keep the default.
bed_chamfer = 0.6; // [0:0.1:1.2]

/* [Rendering] */

flange_color = "#4A7C6F"; // color

flange();

module flange(
    outer_dia = outer_dia,
    thickness = thickness,
    inner_dia = inner_dia,
    pcd = pcd,
    bolt_count = bolt_count,
    bolt_clearance_dia = bolt_clearance_dia,
    bed_chamfer = bed_chamfer,
    flange_color = flange_color
) {
    color(flange_color)
    difference() {
        union() {
            cylinder(d = outer_dia, h = thickness - bed_chamfer);
            translate([0, 0, thickness - bed_chamfer])
                cylinder(d1 = outer_dia, d2 = outer_dia - 2 * bed_chamfer, h = bed_chamfer);
        }
        translate([0, 0, -1])
            cylinder(d = inner_dia, h = thickness + 2);
        for (i = [0 : bolt_count - 1])
            rotate(i * 360 / bolt_count)
                translate([pcd / 2, 0, -1])
                    cylinder(d = bolt_clearance_dia, h = thickness + 2);
    }
}
