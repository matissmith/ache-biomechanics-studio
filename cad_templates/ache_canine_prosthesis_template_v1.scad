// ============================================================
// Ache Innovation — Canine External Prosthesis Template v1
// Functional veterinary concept — not clinically validated
// Units: millimeters
// ============================================================

// ---------- MAIN PARAMETERS ----------
limb_type = "front";          // "front" or "rear"
side = "left";                // "left" or "right"
prosthesis_length = 180;       // ground to proximal socket rim
socket_depth = 45;             // shorter/lower socket than v0
socket_top_diam_x = 58;        // medial/lateral opening
socket_top_diam_y = 44;        // front/back opening
socket_bottom_diam_x = 42;     // distal socket width
socket_bottom_diam_y = 34;     // distal socket depth
wall = 4;
clearance = 1.3;
stay_diam = 11;                // each lateral stay diameter
stay_spacing = 34;             // distance between lateral stays
foot_length = 105;
foot_width = 42;
sole_thickness = 7;
rocker_height = 18;
strap_slot_w = 22;
strap_slot_h = 7;
$fn = 72;

// ---------- DERIVED ----------
socket_top_z = prosthesis_length;
socket_bottom_z = prosthesis_length - socket_depth;
foot_z = sole_thickness;
ankle_z = sole_thickness + rocker_height + 8;
stay_top_z = socket_bottom_z + 4;
stay_bottom_z = ankle_z;
rear_offset = limb_type == "front" ? -12 : -18;
front_offset = limb_type == "front" ? 6 : 2;

// ---------- HELPERS ----------
module ellipsoid(rx, ry, rz) { scale([rx, ry, rz]) sphere(r=1); }
module oval_cylinder(h, dx, dy, center=false) { scale([dx/2, dy/2, 1]) cylinder(h=h, r=1, center=center); }
module rounded_bar(p1, p2, r) { hull(){ translate(p1) sphere(r=r); translate(p2) sphere(r=r); } }
module slot_cut(w,h,d) { cube([w,d,h], center=true); }

// ---------- SOCKET ----------
module socket_shell() {
    difference() {
        hull() {
            translate([0, 0, socket_bottom_z]) oval_cylinder(1, socket_bottom_diam_x + wall*2, socket_bottom_diam_y + wall*2);
            translate([0, rear_offset, socket_top_z]) oval_cylinder(1, socket_top_diam_x + wall*2, socket_top_diam_y + wall*2);
        }
        hull() {
            translate([0, 0, socket_bottom_z + wall]) oval_cylinder(1, socket_bottom_diam_x + clearance, socket_bottom_diam_y + clearance);
            translate([0, rear_offset, socket_top_z + 2]) oval_cylinder(1, socket_top_diam_x + clearance, socket_top_diam_y + clearance);
        }

        // anterior relief window
        translate([0, socket_top_diam_y*0.45 + rear_offset, socket_bottom_z + socket_depth*0.50])
            rotate([90,0,0]) oval_cylinder(socket_top_diam_y*1.4, socket_top_diam_x*0.34, socket_depth*0.38, center=true);

        // strap slots through the lateral walls, not floating rings
        for (z=[socket_bottom_z + socket_depth*0.35, socket_bottom_z + socket_depth*0.68]) {
            translate([ socket_top_diam_x*0.48, rear_offset*0.45, z]) rotate([0,0,0]) slot_cut(strap_slot_h, wall*4, strap_slot_w);
            translate([-socket_top_diam_x*0.48, rear_offset*0.45, z]) rotate([0,0,0]) slot_cut(strap_slot_h, wall*4, strap_slot_w);
        }
    }
}

module socket_rim() {
    difference() {
        translate([0, rear_offset, socket_top_z]) oval_cylinder(7, socket_top_diam_x + wall*3.0, socket_top_diam_y + wall*3.0, center=true);
        translate([0, rear_offset, socket_top_z]) oval_cylinder(8, socket_top_diam_x + clearance, socket_top_diam_y + clearance, center=true);
    }
}

// ---------- DOUBLE LATERAL STAYS ----------
module structural_stays() {
    // Two lateral struts; more plausible than one central pole.
    for (x=[-stay_spacing/2, stay_spacing/2]) {
        p0 = [x, front_offset, stay_bottom_z];
        p1 = [x, front_offset-4, stay_bottom_z + (stay_top_z-stay_bottom_z)*0.35];
        p2 = [x, rear_offset*0.30, stay_bottom_z + (stay_top_z-stay_bottom_z)*0.75];
        p3 = [x, rear_offset*0.18, stay_top_z];
        rounded_bar(p0,p1,stay_diam/2);
        rounded_bar(p1,p2,stay_diam*0.46);
        rounded_bar(p2,p3,stay_diam*0.42);
    }

    // Cross bridges to stop torsion
    rounded_bar([-stay_spacing/2, front_offset, stay_bottom_z], [ stay_spacing/2, front_offset, stay_bottom_z], stay_diam*0.30);
    rounded_bar([-stay_spacing/2, rear_offset*0.18, stay_top_z], [ stay_spacing/2, rear_offset*0.18, stay_top_z], stay_diam*0.32);
}

module collars() {
    translate([0, front_offset, stay_bottom_z]) oval_cylinder(9, stay_spacing + stay_diam*1.8, stay_diam*1.8, center=true);
    translate([0, rear_offset*0.18, stay_top_z]) oval_cylinder(10, stay_spacing + stay_diam*2.0, stay_diam*1.9, center=true);
}

// ---------- FUNCTIONAL ROCKER FOOT ----------
module rocker_foot_body() {
    // Main foot is a functional rocker pad: broad center, lifted toe, rounded heel.
    hull() {
        translate([0, -foot_length*0.36, sole_thickness + 7]) ellipsoid(foot_width*0.42, foot_length*0.16, 8);
        translate([0, 0, sole_thickness + 10]) ellipsoid(foot_width*0.48, foot_length*0.34, 11);
        translate([0, foot_length*0.42, sole_thickness + 15]) ellipsoid(foot_width*0.36, foot_length*0.18, 9);
    }

    // dorsal mounting boss connected to stays
    translate([0, front_offset, ankle_z-2]) oval_cylinder(14, stay_spacing + stay_diam*2.0, stay_diam*2.2, center=true);
}

module sole_pad() {
    // Replaceable flat-ish TPU/rubber contact pad.
    translate([0, 0, sole_thickness/2])
    hull() {
        translate([0, -foot_length*0.30, 0]) oval_cylinder(sole_thickness, foot_width*0.82, foot_length*0.20, center=true);
        translate([0, foot_length*0.18, 0]) oval_cylinder(sole_thickness, foot_width*0.92, foot_length*0.42, center=true);
        translate([0, foot_length*0.45, 0]) oval_cylinder(sole_thickness, foot_width*0.64, foot_length*0.16, center=true);
    }
}

module traction_grooves() {
    for (y=[-foot_length*0.18, 0, foot_length*0.18, foot_length*0.34]) {
        translate([0,y,sole_thickness+0.6]) cube([foot_width*0.78, 2.2, 2.0], center=true);
    }
}

module forward_marker() {
    translate([0, foot_length*0.35, sole_thickness + rocker_height + 8])
    linear_extrude(height=1.2)
    polygon(points=[[0,16],[-6,3],[-2,3],[-2,-9],[2,-9],[2,3],[6,3]]);
}

module foot() {
    difference() {
        union() { rocker_foot_body(); sole_pad(); }
        traction_grooves();
    }
    forward_marker();
}

// ---------- ASSEMBLY ----------
module prosthesis_v1() {
    union() {
        foot();
        collars();
        structural_stays();
        socket_shell();
        socket_rim();
    }
}

prosthesis_v1();

// ---------- NOTES ----------
// v1 removes decorative toes and floating strap rings.
// The design is a functional external prosthesis concept: socket + double lateral stays + rocker pad.
// PLA is only for visual prototypes. Use PETG/Nylon/TPU strategy after review.
