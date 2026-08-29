// Horizontal FDM hole (MIT). Inline teardrop_2d / teardrop_hole into model.scad.
// Apex toward +Z after teardrop_hole so the roof is 45° (no bridge).
$fa = 4;
$fs = 0.4;

/* [Block] */

// Block length along the hole axis X (mm).
block_length = 30; // [16:1:60]

// Block width along Y (mm).
block_width = 20; // [12:1:40]

// Block height along Z (mm).
block_height = 16; // [12:1:30]

// Horizontal hole diameter (mm).
hole_diameter = 8; // [4:0.5:14]

/* [Rendering] */

// Mid-tone preview color.
block_color = "#3D6B7A"; // color

/* [Hidden] */

// Bed-face chamfer (elephant-foot relief).
bed_chamfer = 0.5;

teardrop_block();

module teardrop_block(
    block_length = block_length,
    block_width = block_width,
    block_height = block_height,
    hole_diameter = hole_diameter,
    block_color = block_color,
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
        translate([-0.1, block_width / 2, block_height / 2])
            teardrop_hole(d = hole_diameter, length = block_length + 0.2);
    }
}

// --- copy from here (MIT horizontal teardrop) ---

// 2D profile in XY. Apex on +Y (45° tangents from the circle).
module teardrop_2d(d) {
    r = d / 2;
    hull() {
        circle(r = r);
        polygon([
            [0, r * sqrt(2)],
            [ r * cos(45), r * sin(45)],
            [-r * cos(45), r * sin(45)]
        ]);
    }
}

// Cutter along +X. Apex toward +Z (print roof). Subtract this from a solid.
module teardrop_hole(d, length) {
    rotate([90, 0, 90])
        linear_extrude(height = length)
            teardrop_2d(d);
}

// --- copy until here ---
