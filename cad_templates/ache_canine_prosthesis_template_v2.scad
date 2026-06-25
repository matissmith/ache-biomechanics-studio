// ============================================================
// Ache Innovation — Canine External Prosthesis Template v2
// Functional veterinary concept — iterative CAD base
// Units: millimeters
// ============================================================

// ---------- PARAMETERS ----------
limb_type = "front";
side = "left";
prosthesis_length = 180;
socket_depth = 38;             // lower socket than v1
socket_top_diam_x = 56;
socket_top_diam_y = 42;
socket_bottom_diam_x = 42;
socket_bottom_diam_y = 32;
wall = 4;
clearance = 1.4;
stay_spacing_top = 38;
stay_spacing_bottom = 30;
stay_width = 8;                // flattened stays, not tubes
stay_depth = 13;
foot_length = 96;
foot_width = 42;
sole_thickness = 7;
rocker_height = 16;
$fn = 72;

// ---------- DERIVED ----------
socket_top_z = prosthesis_length;
socket_bottom_z = prosthesis_length - socket_depth;
foot_ground_z = 0;
foot_body_z = sole_thickness + 8;
ankle_z = sole_thickness + rocker_height + 8;
stay_bottom_z = ankle_z;
stay_top_z = socket_bottom_z + 5;
rear_offset = limb_type == "front" ? -10 : -16;
front_offset = limb_type == "front" ? 6 : 2;

// ---------- HELPERS ----------
module ellipsoid(rx, ry, rz) { scale([rx, ry, rz]) sphere(r=1); }
module oval_cylinder(h, dx, dy, center=false) { scale([dx/2, dy/2, 1]) cylinder(h=h, r=1, center=center); }
module rounded_bar(p1, p2, r) { hull(){ translate(p1) sphere(r=r); translate(p2) sphere(r=r); } }
module oval_bar(p1, p2, rx, ry, rz) { hull(){ translate(p1) ellipsoid(rx,ry,rz); translate(p2) ellipsoid(rx,ry,rz); } }

// ---------- SOCKET: lower cuff, less bucket-like ----------
module socket_shell() {
    difference() {
        hull() {
            translate([0, 0, socket_bottom_z])
                oval_cylinder(1, socket_bottom_diam_x + wall*2, socket_bottom_diam_y + wall*2);
            translate([0, rear_offset, socket_top_z])
                oval_cylinder(1, socket_top_diam_x + wall*1.6, socket_top_diam_y + wall*1.6);
        }

        hull() {
            translate([0, 0, socket_bottom_z + wall])
                oval_cylinder(1, socket_bottom_diam_x + clearance, socket_bottom_diam_y + clearance);
            translate([0, rear_offset, socket_top_z + 2])
                oval_cylinder(1, socket_top_diam_x + clearance, socket_top_diam_y + clearance);
        }

        // anterior relief window, softened and smaller
        translate([0, socket_top_diam_y*0.42 + rear_offset, socket_bottom_z + socket_depth*0.52])
            rotate([90,0,0])
            oval_cylinder(socket_top_diam_y*1.2, socket_top_diam_x*0.30, socket_depth*0.32, center=true);

        // lateral strap slots
        for (z=[socket_bottom_z + socket_depth*0.40, socket_bottom_z + socket_depth*0.70]) {
            translate([ socket_top_diam_x*0.48, rear_offset*0.40, z]) cube([8, wall*5, 20], center=true);
            translate([-socket_top_diam_x*0.48, rear_offset*0.40, z]) cube([8, wall*5, 20], center=true);
        }
    }
}

module socket_rim() {
    // thin rim, not oversized ring
    difference() {
        translate([0, rear_offset, socket_top_z])
            oval_cylinder(4, socket_top_diam_x + wall*2.0, socket_top_diam_y + wall*2.0, center=true);
        translate([0, rear_offset, socket_top_z])
            oval_cylinder(5, socket_top_diam_x + clearance, socket_top_diam_y + clearance, center=true);
    }
}

// ---------- SIDE BLADES / STAYS ----------
module side_stays() {
    // flattened, slightly curved lateral blades instead of vertical rods
    for (side=[-1,1]) {
        x0 = side * stay_spacing_bottom/2;
        x1 = side * stay_spacing_top/2;
        p0 = [x0, front_offset, stay_bottom_z];
        p1 = [side*(stay_spacing_bottom/2 + 2), front_offset-5, stay_bottom_z + (stay_top_z-stay_bottom_z)*0.34];
        p2 = [side*(stay_spacing_top/2 - 2), rear_offset*0.20, stay_bottom_z + (stay_top_z-stay_bottom_z)*0.72];
        p3 = [x1, rear_offset*0.14, stay_top_z];
        oval_bar(p0,p1, stay_width/2, stay_depth/2, stay_width/2);
        oval_bar(p1,p2, stay_width/2, stay_depth/2, stay_width/2);
        oval_bar(p2,p3, stay_width/2, stay_depth/2, stay_width/2);
    }

    // slim bridges, not big blocks
    oval_bar([-stay_spacing_bottom/2, front_offset, stay_bottom_z], [stay_spacing_bottom/2, front_offset, stay_bottom_z], 4, 7, 4);
    oval_bar([-stay_spacing_top/2, rear_offset*0.14, stay_top_z], [stay_spacing_top/2, rear_offset*0.14, stay_top_z], 4, 7, 4);
}

module smooth_transitions() {
    // organic saddles between foot/stays and socket/stays
    translate([0, front_offset, stay_bottom_z])
        ellipsoid(stay_spacing_bottom/2 + 8, 13, 7);
    translate([0, rear_offset*0.14, stay_top_z])
        ellipsoid(stay_spacing_top/2 + 9, 12, 7);
}

// ---------- PAW-PAD ROCKER FOOT ----------
module paw_rocker_body() {
    // compact pad, not shoe; front lifted, rear rounded
    hull() {
        translate([0, -foot_length*0.34, sole_thickness + 7])
            ellipsoid(foot_width*0.36, foot_length*0.16, 7);
        translate([0, -foot_length*0.02, sole_thickness + 10])
            ellipsoid(foot_width*0.50, foot_length*0.32, 10);
        translate([0, foot_length*0.36, sole_thickness + 14])
            ellipsoid(foot_width*0.38, foot_length*0.18, 8);
    }

    // subtle metacarpal pad bulge; not decorative toes
    translate([0, foot_length*0.22, sole_thickness + 17])
        ellipsoid(foot_width*0.34, foot_length*0.16, 5);
}

module sole_pad() {
    // flat replaceable contact pad underneath
    translate([0, 0, sole_thickness/2])
    hull() {
        translate([0, -foot_length*0.30, 0]) oval_cylinder(sole_thickness, foot_width*0.72, foot_length*0.18, center=true);
        translate([0,  foot_length*0.02, 0]) oval_cylinder(sole_thickness, foot_width*0.90, foot_length*0.38, center=true);
        translate([0,  foot_length*0.34, 0]) oval_cylinder(sole_thickness, foot_width*0.58, foot_length*0.16, center=true);
    }
}

module traction_channels() {
    // shallow grooves cut from the bottom pad
    for (y=[-foot_length*0.18, 0, foot_length*0.18]) {
        translate([0,y,sole_thickness+0.8]) cube([foot_width*0.72, 2.2, 2.0], center=true);
    }
}

module foot() {
    difference() {
        union(){ sole_pad(); paw_rocker_body(); }
        traction_channels();
    }
}

// ---------- ASSEMBLY ----------
module prosthesis_v2() {
    union() {
        foot();
        smooth_transitions();
        side_stays();
        socket_shell();
        socket_rim();
    }
}

prosthesis_v2();

// v2 design notes:
// - lower cuff socket
// - no fake toes
// - side blades instead of straight poles
// - paw-pad rocker support
// - strap slots instead of floating rings
