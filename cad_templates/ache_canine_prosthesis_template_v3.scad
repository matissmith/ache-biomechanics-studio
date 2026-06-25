// ============================================================
// Ache Innovation — Canine External Prosthesis Template v3
// Functional veterinary orthoprosthetic concept
// Units: millimeters
// ============================================================
// Goal v3: stop looking like a cup + sticks + shoe.
// Short cuff, lateral fork frame, compact rocker pad.

limb_type = "front";
side = "left";
prosthesis_length = 175;

// Cuff/socket: shorter and more orthotic, less bucket-like
cuff_height = 32;
cuff_top_x = 58;
cuff_top_y = 44;
cuff_bottom_x = 46;
cuff_bottom_y = 34;
wall = 4;
clearance = 1.4;

// Frame
frame_width_top = 44;
frame_width_bottom = 34;
rail_w = 9;
rail_d = 15;

// Foot / rocker pad
foot_length = 88;
foot_width = 40;
sole_thickness = 7;
pad_height = 18;
$fn = 72;

// Derived
cuff_top_z = prosthesis_length;
cuff_bottom_z = prosthesis_length - cuff_height;
pad_z = sole_thickness + 9;
ankle_z = sole_thickness + pad_height + 8;
frame_top_z = cuff_bottom_z + 4;
frame_bottom_z = ankle_z;
rear_offset = limb_type == "front" ? -8 : -14;
front_offset = limb_type == "front" ? 4 : 0;

// ---------- helpers ----------
module ellipsoid(rx, ry, rz) { scale([rx, ry, rz]) sphere(r=1); }
module oval_cylinder(h, dx, dy, center=false) { scale([dx/2, dy/2, 1]) cylinder(h=h, r=1, center=center); }
module oval_bar(p1, p2, rx, ry, rz) { hull(){ translate(p1) ellipsoid(rx,ry,rz); translate(p2) ellipsoid(rx,ry,rz); } }
module rounded_rect_block(x,y,z,r=4) {
    hull() {
        for (sx=[-1,1], sy=[-1,1]) translate([sx*(x/2-r), sy*(y/2-r), 0]) cylinder(h=z, r=r, center=true);
    }
}

// ---------- short open cuff ----------
module cuff_shell() {
    difference() {
        hull() {
            translate([0, 0, cuff_bottom_z]) oval_cylinder(1, cuff_bottom_x + wall*2, cuff_bottom_y + wall*2);
            translate([0, rear_offset, cuff_top_z]) oval_cylinder(1, cuff_top_x + wall*1.4, cuff_top_y + wall*1.4);
        }
        hull() {
            translate([0, 0, cuff_bottom_z + wall]) oval_cylinder(1, cuff_bottom_x + clearance, cuff_bottom_y + clearance);
            translate([0, rear_offset, cuff_top_z + 2]) oval_cylinder(1, cuff_top_x + clearance, cuff_top_y + clearance);
        }
        // Large anterior opening: makes it read as cuff/orthosis, not bucket
        translate([0, cuff_top_y*0.46 + rear_offset, cuff_bottom_z + cuff_height*0.55])
            rotate([90,0,0]) oval_cylinder(cuff_top_y*1.8, cuff_top_x*0.58, cuff_height*0.72, center=true);
        // side strap slots
        for (z=[cuff_bottom_z + cuff_height*0.38, cuff_bottom_z + cuff_height*0.68]) {
            translate([ cuff_top_x*0.48, rear_offset*0.35, z]) cube([8, wall*5, 18], center=true);
            translate([-cuff_top_x*0.48, rear_offset*0.35, z]) cube([8, wall*5, 18], center=true);
        }
    }
}

module cuff_rim() {
    difference() {
        translate([0, rear_offset, cuff_top_z]) oval_cylinder(3.5, cuff_top_x + wall*1.6, cuff_top_y + wall*1.6, center=true);
        translate([0, rear_offset, cuff_top_z]) oval_cylinder(4.5, cuff_top_x + clearance, cuff_top_y + clearance, center=true);
    }
}

// ---------- lateral fork frame ----------
module lateral_frame() {
    // two broad rails, slightly swept back, not round poles
    for (side=[-1,1]) {
        x0 = side * frame_width_bottom/2;
        x1 = side * frame_width_top/2;
        p0 = [x0, front_offset, frame_bottom_z];
        p1 = [side*(frame_width_bottom/2 + 1), front_offset-5, frame_bottom_z + (frame_top_z-frame_bottom_z)*0.35];
        p2 = [side*(frame_width_top/2 - 2), rear_offset*0.18, frame_bottom_z + (frame_top_z-frame_bottom_z)*0.75];
        p3 = [x1, rear_offset*0.10, frame_top_z];
        oval_bar(p0,p1, rail_w/2, rail_d/2, rail_w/2);
        oval_bar(p1,p2, rail_w/2, rail_d/2, rail_w/2);
        oval_bar(p2,p3, rail_w/2, rail_d/2, rail_w/2);
    }
    // integrated yokes
    oval_bar([-frame_width_bottom/2, front_offset, frame_bottom_z], [frame_width_bottom/2, front_offset, frame_bottom_z], 5, 8, 5);
    oval_bar([-frame_width_top/2, rear_offset*0.10, frame_top_z], [frame_width_top/2, rear_offset*0.10, frame_top_z], 5, 8, 5);
}

module transitions() {
    translate([0, front_offset, frame_bottom_z]) ellipsoid(frame_width_bottom/2 + 8, 12, 6);
    translate([0, rear_offset*0.10, frame_top_z]) ellipsoid(frame_width_top/2 + 8, 11, 6);
}

// ---------- compact rocker pad ----------
module rocker_pad() {
    // Main compact paw-pad form: flatter, shorter, less shoe-like
    hull() {
        translate([0, -foot_length*0.32, sole_thickness + 6]) ellipsoid(foot_width*0.36, foot_length*0.14, 6);
        translate([0, -foot_length*0.02, sole_thickness + 8]) ellipsoid(foot_width*0.48, foot_length*0.28, 8);
        translate([0, foot_length*0.34, sole_thickness + 11]) ellipsoid(foot_width*0.34, foot_length*0.15, 6);
    }
    // mounting saddle, blended upward
    translate([0, front_offset, ankle_z-4]) ellipsoid(frame_width_bottom/2 + 10, 12, 7);
}

module sole() {
    translate([0, -foot_length*0.02, sole_thickness/2])
    hull() {
        translate([0, -foot_length*0.28, 0]) oval_cylinder(sole_thickness, foot_width*0.68, foot_length*0.15, center=true);
        translate([0, 0, 0]) oval_cylinder(sole_thickness, foot_width*0.88, foot_length*0.34, center=true);
        translate([0, foot_length*0.30, 0]) oval_cylinder(sole_thickness, foot_width*0.58, foot_length*0.14, center=true);
    }
}

module grooves() {
    for (y=[-foot_length*0.16, 0, foot_length*0.16])
        translate([0,y,sole_thickness+0.8]) cube([foot_width*0.66, 2.0, 2.0], center=true);
}

module foot() {
    difference() { union(){ sole(); rocker_pad(); } grooves(); }
}

module prosthesis_v3() {
    union() {
        foot();
        transitions();
        lateral_frame();
        cuff_shell();
        cuff_rim();
    }
}

prosthesis_v3();

// v3 notes:
// - short open cuff instead of bucket
// - lateral fork frame instead of vertical tubes
// - compact rocker pad, no fake toes
// - intended as CAD base for iteration, not clinical final
