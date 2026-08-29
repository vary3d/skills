// Vertical FDM hole (MIT). Inline polyhole into model.scad.
// Circumscribed n-gon so the inscribed circle matches the nominal diameter.
$fa = 4;
$fs = 0.4;

/* [Plate] */

// Plate length along X (mm).
plate_length = 70; // [40:1:120]

// Plate width along Y (mm).
plate_width = 18; // [12:1:40]

// Plate thickness (mm).
thickness = 4; // [2:0.5:8]

/* [Rendering] */

// Mid-tone preview color.
plate_color = "#3D6B7A"; // color

/* [Hidden] */

// Bed-face chamfer (elephant-foot relief).
bed_chamfer = 0.5;

polyhole_gauge();

module polyhole_gauge(
    plate_length = plate_length,
    plate_width = plate_width,
    thickness = thickness,
    plate_color = plate_color,
    bed_chamfer = bed_chamfer
) {
    holes = [3, 4, 6, 8];
    color(plate_color)
    difference() {
        hull() {
            cube([plate_length, plate_width, thickness - bed_chamfer]);
            translate([bed_chamfer, bed_chamfer, 0])
                cube([plate_length - 2 * bed_chamfer, plate_width - 2 * bed_chamfer, thickness]);
        }
        for (i = [0 : len(holes) - 1]) {
            d = holes[i];
            x = 10 + i * (plate_length - 20) / (len(holes) - 1);
            translate([x, plate_width / 2, -0.1])
                polyhole(h = thickness + 0.2, d = d);
        }
    }
}

// --- copy from here (MIT vertical polyhole) ---

function polyhole_sides(d) = max(ceil(d * 2), 3);

// Cutter along +Z. Inscribed circle diameter is d (FDM vertical holes print undersize).
module polyhole(h, d, center = false) {
    n = polyhole_sides(d);
    cylinder(h = h, r = (d / 2) / cos(180 / n), $fn = n, center = center);
}

// --- copy until here ---
