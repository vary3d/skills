// Plastic self-tap hole (MIT). Inline selftap_hole into model.scad.
// Geometry after OpenEng (MIT): https://gitlab.com/bath_open_instrumentation_group/openeng
// Machine screw into printed plastic — not a heat-set insert.
$fa = 4;
$fs = 0.4;

/* [Block] */

// Block length along X (mm).
block_length = 20; // [12:1:40]

// Block width along Y (mm).
block_width = 16; // [12:1:32]

// Block height along Z (mm).
block_height = 10; // [6:0.5:20]

// Metric screw size the hole should tap (mm). M3 → 3.
screw_nominal = 3; // [2:0.5:6]

/* [Rendering] */

// Mid-tone preview color.
block_color = "#3D6B7A"; // color

/* [Hidden] */

// Extra diameter for FDM squish (mm).
splodge = 0.2;

// Bed-face chamfer (elephant-foot relief).
bed_chamfer = 0.5;

selftap_block();

module selftap_block(
    block_length = block_length,
    block_width = block_width,
    block_height = block_height,
    screw_nominal = screw_nominal,
    block_color = block_color,
    splodge = splodge,
    bed_chamfer = bed_chamfer
) {
    color(block_color)
    difference() {
        hull() {
            cube([block_length, block_width, block_height - bed_chamfer]);
            translate([bed_chamfer, bed_chamfer, 0])
                cube([
                    block_length - 2 * bed_chamfer,
                    block_width - 2 * bed_chamfer,
                    block_height
                ]);
        }
        translate([block_length / 2, block_width / 2, -0.1])
            selftap_hole_metric(screw_nominal, h = block_height + 0.2, splodge = splodge);
    }
}

// --- copy from here (MIT self-tap; after OpenEng) ---

function metric_coarse_pitch(screw_d) =
    screw_d <= 2 ? 0.4 :
    screw_d <= 2.5 ? 0.45 :
    screw_d <= 3 ? 0.5 :
    screw_d <= 4 ? 0.7 :
    screw_d <= 5 ? 0.8 : 1.0;

// 75% thread engagement tap diameter (OpenEng).
function tap_diameter(screw_d, pitch) = screw_d - pitch * sqrt(3) * 0.75 * 0.75;

module trylinder(r = 1, flat = 1, h = 1, center = false) {
    hull()
        for (a = [0, 120, 240])
            rotate([0, 0, a])
                translate([0, flat / sqrt(3), 0])
                    cylinder(r = r, h = h, center = center, $fn = 12);
}

module selftap_hole(nominal_d, h = 10, center = false, splodge = 0.2) {
    r = (nominal_d + splodge) / 2;
    flat = (r / 2) * (2 * sqrt(3));
    trylinder(r = r / 2, flat = flat, h = h, center = center);
}

module selftap_hole_metric(screw_d, h = 10, center = false, splodge = 0.2) {
    selftap_hole(
        tap_diameter(screw_d, metric_coarse_pitch(screw_d)),
        h = h,
        center = center,
        splodge = splodge
    );
}

// --- copy until here ---
