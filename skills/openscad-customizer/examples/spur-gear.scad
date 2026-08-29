// Involute spur gear pair (MIT). Inline spur_gear / spur_gear_2d into model.scad.
// Do not use <MCAD> or BOSL2 for spur gears. ISO 53 full-depth; 20° pressure angle.
$fa = 4;
$fs = 0.4;

/* [Gear] */

// Metric module (mm). Same for both gears.
module_mm = 1; // [0.5:0.25:3]

// Tooth count of the pinion (small gear).
pinion_teeth = 20; // [12:1:40]

// Tooth count of the large gear.
gear_teeth = 40; // [16:1:80]

// Face width along the axis (mm).
face_width = 8; // [4:0.5:20]

// Nominal shaft diameter shared by both gears (mm).
shaft_diameter = 5; // [3:0.5:12]

/* [Rendering] */

// Mid-tone preview color.
gear_color = "#3D6B7A"; // color

// All = meshed preview only. Pick pinion or gear to export one STL.
part = "all"; // [all:All, pinion:Pinion, gear:Gear]

/* [Hidden] */

// Pressure angle (degrees). ISO 53 standard.
pressure_angle = 20;

// Circular backlash at the pitch circle (mm); split across both gears.
backlash = 0.15;

// Extra radial clearance on the shaft bore (mm).
shaft_clearance = 0.3;

// Involute samples per flank.
involute_steps = 8;

gear_pair();

module gear_pair(
    module_mm = module_mm,
    pinion_teeth = pinion_teeth,
    gear_teeth = gear_teeth,
    face_width = face_width,
    shaft_diameter = shaft_diameter,
    gear_color = gear_color,
    part = part
) {
    center_distance = spur_center_distance(module_mm, pinion_teeth, gear_teeth);
    bore = shaft_diameter + shaft_clearance;

    if (part == "all") {
        color(gear_color) pinion_print();
        color(gear_color) gear_geom(center_distance);
    } else if (part == "pinion") {
        color(gear_color) pinion_print();
    } else if (part == "gear") {
        color(gear_color) gear_print();
    }
}

// Large gear on +X. Even tooth counts need a half-pitch spin so a space faces the pinion.
module gear_geom(center_distance) {
    translate([center_distance, 0, 0])
        rotate([0, 0, spur_mesh_rotate(gear_teeth)])
            gear_print();
}

module pinion_print() {
    spur_gear(
        module_mm, pinion_teeth, face_width, shaft_diameter + shaft_clearance,
        pressure_angle, backlash, involute_steps
    );
}

module gear_print() {
    spur_gear(
        module_mm, gear_teeth, face_width, shaft_diameter + shaft_clearance,
        pressure_angle, backlash, involute_steps
    );
}

// --- copy from here (MIT involute spur gear) ---

function spur_center_distance(module_mm, z1, z2) = module_mm * (z1 + z2) / 2;

// Rotate the gear on +X so a tooth space faces the pinion (tooth on +X).
function spur_mesh_rotate(teeth) = (teeth % 2 == 0) ? 180 / teeth : 0;

module spur_gear(
    module_mm,
    teeth,
    face_width,
    bore,
    pressure_angle = 20,
    backlash = 0.15,
    involute_steps = 8
) {
    difference() {
        linear_extrude(height = face_width, convexity = 10)
            spur_gear_2d(module_mm, teeth, pressure_angle, backlash, involute_steps);
        translate([0, 0, -0.1])
            cylinder(h = face_width + 0.2, d = bore, $fn = max(24, ceil(bore * 8)));
    }
}

module spur_gear_2d(
    module_mm,
    teeth,
    pressure_angle = 20,
    backlash = 0.15,
    involute_steps = 8
) {
    pitch_r = module_mm * teeth / 2;
    base_r = pitch_r * cos(pressure_angle);
    tip_r = pitch_r + module_mm;
    root_r = pitch_r - 1.25 * module_mm;
    // Tooth + space = 360/teeth; backlash thins this gear by a quarter of the circular amount.
    backlash_deg = backlash / pitch_r * 180 / PI;
    half_thick_deg = (360 / teeth - backlash_deg) / 4;
    steps = max(involute_steps, 5);

    union() {
        circle(r = root_r, $fn = max(teeth * 2, 48));
        for (k = [0 : teeth - 1])
            rotate([0, 0, k * 360 / teeth])
                polygon(_sg_tooth_pts(
                    base_r, root_r, tip_r, pitch_r, half_thick_deg, steps
                ));
    }
}

function _sg_involute_xy(base_r, roll_deg) =
    let (t = roll_deg * PI / 180)
    [
        base_r * (cos(roll_deg) + t * sin(roll_deg)),
        base_r * (sin(roll_deg) - t * cos(roll_deg))
    ];

function _sg_roll_deg(base_r, r) =
    r <= base_r + 1e-9 ? 0 : sqrt((r / base_r) * (r / base_r) - 1) * 180 / PI;

function _sg_rot2(p, ang) = [
    p[0] * cos(ang) - p[1] * sin(ang),
    p[0] * sin(ang) + p[1] * cos(ang)
];

function _sg_flank(base_r, r0, r1, spin, steps) = [
    for (i = [0 : steps])
        _sg_rot2(
            _sg_involute_xy(base_r, _sg_roll_deg(base_r, r0 + (r1 - r0) * i / steps)),
            spin
        )
];

function _sg_tooth_pts(base_r, root_r, tip_r, pitch_r, half_thick_deg, steps) =
    let (
        r0 = max(base_r, root_r),
        pp = _sg_involute_xy(base_r, _sg_roll_deg(base_r, pitch_r)),
        spin = half_thick_deg - atan2(pp[1], pp[0]),
        left = _sg_flank(base_r, r0, tip_r, spin, steps),
        right = [for (i = [steps : -1 : 0]) [left[i][0], -left[i][1]]],
        a0 = atan2(left[steps][1], left[steps][0]),
        a1 = atan2(right[0][1], right[0][0]),
        tip = [
            for (i = [1 : 3])
                let (a = a0 + (a1 - a0) * i / 4)
                [tip_r * cos(a), tip_r * sin(a)]
        ],
        ray0 = atan2(left[0][1], left[0][0]),
        stub = root_r + 1e-9 < r0
    )
    concat(
        stub ? [[root_r * cos(ray0), root_r * sin(ray0)]] : [],
        left,
        tip,
        right,
        stub ? [[root_r * cos(-ray0), root_r * sin(-ray0)]] : []
    );

// --- copy until here ---
