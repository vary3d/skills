// Trapezoid helix thread (MIT). Inline male_thread / thread_tooth into model.scad.
// Do not use BOSL2 for this. Female = cut of an enlarged male (gap on the nut only).
$fa = 4;
$fs = 0.4;

/* [Thread] */

// Major diameter of the male thread (mm).
major_diameter = 20; // [10:1:40]

// Axial pitch of one turn (mm).
pitch = 2.5; // [1.5:0.5:4]

// Length of the threaded section (mm).
thread_length = 16; // [8:1:40]

/* [Nut] */

// Hex nut across-flats size (mm).
nut_across_flats = 30; // [16:1:50]

// Nut thickness along the axis (mm).
nut_height = 8; // [5:0.5:16]

/* [Rendering] */

// Mid-tone preview color.
thread_color = "#3D6B7A"; // color

// All = stud with nut preview. Pick stud or nut to export one STL.
part = "all"; // [all:All, stud:Stud, nut:Nut]

/* [Hidden] */

// Radial depth of the trapezoid tooth (mm).
thread_depth = 1.2;

// Radial clearance applied only on the female thread (mm).
fit_gap = 0.35;

// Helix segments per turn.
segs_per_turn = 24;

// Bed-face chamfer (elephant-foot relief).
bed_chamfer = 0.6;

thread_demo();

module thread_demo(
    major_diameter = major_diameter,
    pitch = pitch,
    thread_length = thread_length,
    nut_across_flats = nut_across_flats,
    nut_height = nut_height,
    thread_color = thread_color,
    part = part
) {
    if (part == "all") {
        color(thread_color) stud_print();
        color(thread_color) nut_geom();
    } else if (part == "stud") {
        color(thread_color) stud_print();
    } else if (part == "nut") {
        color(thread_color) nut_print();
    }
}

// Assembly: nut sits around the mid-height of the stud.
module nut_geom() {
    translate([0, 0, (thread_length - nut_height) / 2])
        nut_print();
}

module stud_print() {
    d_major = major_diameter;
    d_minor = d_major - 2 * thread_depth;
    union() {
        cylinder(h = thread_length, d = d_minor);
        intersection() {
            male_thread(d_major, d_minor, pitch, thread_length, true, segs_per_turn);
            cylinder(h = thread_length, d = d_major + 0.4);
        }
    }
}

module nut_print() {
    d_major = major_diameter + 2 * fit_gap;
    d_minor = major_diameter - 2 * thread_depth + 2 * fit_gap;
    af = nut_across_flats;
    difference() {
        // Point-to-point = across-flats / cos(30)
        cylinder(h = nut_height, d = af / cos(30), $fn = 6);
        translate([0, 0, -0.01])
            cylinder(h = nut_height + 0.02, d = d_minor);
        translate([0, 0, -0.01])
            intersection() {
                male_thread(d_major, d_minor, pitch, nut_height + 0.02, true, segs_per_turn);
                cylinder(h = nut_height + 0.02, d = d_major + 0.4);
            }
        cylinder(h = bed_chamfer, d1 = d_major + 0.8, d2 = d_minor);
    }
}

// --- copy from here (MIT trapezoid helix) ---

module male_thread(
    d_major,
    d_minor,
    pitch,
    length,
    right_hand = true,
    segs_per_turn = 24
) {
    turns = length / pitch;
    n = max(1, ceil(turns * segs_per_turn));
    sense = right_hand ? 1 : -1;
    for (i = [0 : n - 1]) {
        z0 = i * length / n;
        z1 = (i + 1) * length / n;
        a0 = sense * 360 * turns * (i / n);
        a1 = sense * 360 * turns * ((i + 1) / n);
        hull() {
            translate([0, 0, z0]) rotate([0, 0, a0])
                thread_tooth(d_major, d_minor, pitch);
            translate([0, 0, z1]) rotate([0, 0, a1])
                thread_tooth(d_major, d_minor, pitch);
        }
    }
}

module thread_tooth(d_major, d_minor, pitch) {
    half_p = pitch * 0.28;
    r_maj = d_major / 2;
    r_min = d_minor / 2;
    rotate([90, 0, 0])
        linear_extrude(height = 0.55, center = true)
            polygon([
                [r_min, -half_p],
                [r_maj, -half_p * 0.35],
                [r_maj,  half_p * 0.35],
                [r_min,  half_p]
            ]);
}

// --- copy until here ---
