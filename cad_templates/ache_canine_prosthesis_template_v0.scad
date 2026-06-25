// ============================================================
// Ache Innovation — Canine External Prosthesis Template v0
// Parametric OpenSCAD base template
// Units: millimeters
// ============================================================
// This is a functional CAD starting point, not a clinically validated device.
// Review with veterinarian/orthotist before real use.

// ---------- MAIN PARAMETERS ----------
limb_type = "front";          // "front" or "rear"
side = "left";                // "left" or "right"
prosthesis_length = 180;       // total height ground to socket rim
socket_depth = 55;             // stump insertion depth
socket_top_diam_x = 62;        // socket opening width medial/lateral
socket_top_diam_y = 48;        // socket opening front/back
socket_bottom_diam_x = 38;     // distal socket width
socket_bottom_diam_y = 32;     // distal socket depth
wall = 4;
clearance = 1.2;
pylon_diam = 22;
foot_length = 95;
foot_width = 46;
sole_thickness = 6;
strap_width = 10;
strap_thickness = 3;
$fn = 72;

// ---------- DERIVED ----------
socket_top_z = prosthesis_length;
socket_bottom_z = prosthesis_length - socket_depth;
foot_top_z = sole_thickness + 18;
pylon_top_z = socket_bottom_z + 3;
pylon_bottom_z = foot_top_z;
rear_offset = limb_type == "front" ? -10 : -16;
front_offset = limb_type == "front" ? 8 : 4;
mirror_side = side == "left" ? 1 : -1;

// ---------- HELPERS ----------
module ellipsoid(rx, ry, rz) {
    scale([rx, ry, rz]) sphere(r=1);
}

module oval_cylinder(h, dx, dy, center=false) {
    scale([dx/2, dy/2, 1]) cylinder(h=h, r=1, center=center);
}

module rounded_bar(p1, p2, r) {
    hull() {
        translate(p1) sphere(r=r);
        translate(p2) sphere(r=r);
    }
}

// ---------- SOCKET ----------
module socket_outer() {
    hull() {
        translate([0, 0, socket_bottom_z])
            oval_cylinder(1, socket_bottom_diam_x + wall*2, socket_bottom_diam_y + wall*2);
        translate([0, rear_offset, socket_top_z])
            oval_cylinder(1, socket_top_diam_x + wall*2, socket_top_diam_y + wall*2);
    }
}

module socket_inner() {
    hull() {
        translate([0, 0, socket_bottom_z + wall])
            oval_cylinder(1, socket_bottom_diam_x + clearance, socket_bottom_diam_y + clearance);
        translate([0, rear_offset, socket_top_z + 2])
            oval_cylinder(1, socket_top_diam_x + clearance, socket_top_diam_y + clearance);
    }
}

module relief_window() {
    // anterior soft tissue inspection / relief window
    translate([0, socket_top_diam_y*0.45 + rear_offset, socket_bottom_z + socket_depth*0.48])
        rotate([90,0,0])
        oval_cylinder(socket_top_diam_y*1.2, socket_top_diam_x*0.42, socket_depth*0.38, center=true);
}

module strap_band(z) {
    difference() {
        translate([0, rear_offset*0.55, z])
            oval_cylinder(strap_width, socket_top_diam_x + wall*5, socket_top_diam_y + wall*5, center=true);
        translate([0, rear_offset*0.55, z])
            oval_cylinder(strap_width + 1, socket_top_diam_x + wall*1.5, socket_top_diam_y + wall*1.5, center=true);
    }
}

module socket() {
    difference() {
        socket_outer();
        socket_inner();
        relief_window();
        // lateral strap slots
        for (z=[socket_bottom_z + socket_depth*0.35, socket_bottom_z + socket_depth*0.68]) {
            translate([0, rear_offset*0.5, z]) rotate([0,90,0])
                cylinder(h=socket_top_diam_x*2, d=7, center=true);
        }
    }
    strap_band(socket_bottom_z + socket_depth*0.35);
    strap_band(socket_bottom_z + socket_depth*0.68);
}

// ---------- STRUCTURAL PYLON ----------
module pylon() {
    // Slight posterior/anterior curve in sagittal plane.
    p0 = [0, front_offset, pylon_bottom_z];
    p1 = [0, 0, pylon_bottom_z + (pylon_top_z-pylon_bottom_z)*0.35];
    p2 = [0, rear_offset*0.35, pylon_bottom_z + (pylon_top_z-pylon_bottom_z)*0.72];
    p3 = [0, rear_offset*0.15, pylon_top_z];
    rounded_bar(p0, p1, pylon_diam/2);
    rounded_bar(p1, p2, pylon_diam*0.46);
    rounded_bar(p2, p3, pylon_diam*0.40);

    // twin side stays for stability
    for (x=[-pylon_diam*0.55, pylon_diam*0.55]) {
        rounded_bar([x, front_offset-2, pylon_bottom_z], [x, rear_offset*0.12, pylon_top_z], pylon_diam*0.13);
    }
}

module transition_collars() {
    translate([0, front_offset, pylon_bottom_z])
        oval_cylinder(10, pylon_diam*2.0, pylon_diam*1.55, center=true);
    translate([0, rear_offset*0.12, pylon_top_z])
        oval_cylinder(10, pylon_diam*2.1, pylon_diam*1.7, center=true);
}

// ---------- FOOT / PAW PAD ----------
module prosthetic_foot() {
    // Main rocker foot: long pad, front toe rocker, rear heel.
    hull() {
        translate([0, -foot_length*0.28, sole_thickness + 8]) ellipsoid(foot_width*0.40, foot_length*0.22, 10);
        translate([0, foot_length*0.18, sole_thickness + 10]) ellipsoid(foot_width*0.46, foot_length*0.36, 11);
        translate([0, foot_length*0.50, sole_thickness + 15]) ellipsoid(foot_width*0.34, foot_length*0.18, 9);
    }

    // Toe lobes: functional contact hints, not decorative human toes.
    for (x=[-0.30, -0.10, 0.10, 0.30]) {
        translate([x*foot_width, foot_length*0.60, sole_thickness + 12])
            ellipsoid(foot_width*0.09, foot_length*0.11, 6);
    }

    // Replaceable sole/contact surface.
    translate([0, foot_length*0.08, sole_thickness/2])
        oval_cylinder(sole_thickness, foot_width*0.92, foot_length*0.86, center=true);
}

module alignment_arrow() {
    // Small embossed arrow showing forward direction.
    translate([0, foot_length*0.08, sole_thickness + 22])
    linear_extrude(height=1.2)
    polygon(points=[[0,14],[-5,3],[-2,3],[-2,-10],[2,-10],[2,3],[5,3]]);
}

// ---------- ASSEMBLY ----------
module prosthesis() {
    union() {
        prosthetic_foot();
        transition_collars();
        pylon();
        socket();
        alignment_arrow();
    }
}

prosthesis();

// ---------- PRINTING NOTES ----------
// Suggested prototype materials:
// - PLA only for visual prototype
// - PETG/Nylon for structural prototype
// - TPU or rubber insert for sole/contact surface
// Suggested orientation: evaluate in slicer; likely side orientation with supports.
// Minimum: 4 walls, 35-45% gyroid infill for prototypes.
