// ============================================================
// Ache Innovation — Biomechanical Canine Limb Concept v4
// Articulated external prosthesis/orthoprosthesis concept
// Units: millimeters
// ============================================================
// Goal: resemble a functional canine limb architecture:
// upper cuff + knee/hock hinge + lower shank + ankle/paw hinge + elastic tendons.
// Not clinically validated. Mechanical design requires engineering review.

$fn = 64;

// ---------- PARAMETERS ----------
limb_type = "rear";            // "rear" = knee/hock style, "front" = elbow/carpus style
prosthesis_height = 210;
upper_cuff_h = 55;
upper_cuff_w = 62;
upper_cuff_d = 48;
shank_len = 78;
shank_w = 34;
shank_d = 28;
foot_len = 92;
foot_w = 44;
foot_h = 30;
wall = 4;
hinge_d = 28;
hinge_thick = 12;
tendon_d = 5;
spring_d = 9;

// ---------- COORDINATES ----------
// Z up, Y forward, X lateral.
ground_z = 0;
foot_center_y = 20;
ankle_z = 38;
knee_z = ankle_z + shank_len;
cuff_z = knee_z + upper_cuff_h * 0.55;
rear_sweep = -18;
forward_sweep = 18;

// ---------- HELPERS ----------
module ellipsoid(rx, ry, rz) { scale([rx, ry, rz]) sphere(r=1); }
module oval_cylinder(h, dx, dy, center=false) { scale([dx/2, dy/2, 1]) cylinder(h=h, r=1, center=center); }
module rounded_bar(p1, p2, r) { hull(){ translate(p1) sphere(r=r); translate(p2) sphere(r=r); } }
module capsule(p1,p2,rx,ry,rz) { hull(){ translate(p1) ellipsoid(rx,ry,rz); translate(p2) ellipsoid(rx,ry,rz); } }

module hinge_at(p, axis="x") {
    translate(p) rotate([0,90,0]) {
        color("#202020") cylinder(h=hinge_thick, d=hinge_d, center=true);
        color("#555555") cylinder(h=hinge_thick+4, d=hinge_d*0.38, center=true);
    }
}

module spring_between(p1, p2, coils=8, radius=7, wire=1.8) {
    // Visual helical spring approximated with small connected capsules.
    steps = coils * 16;
    for (i=[0:steps-1]) {
        t1 = i/steps;
        t2 = (i+1)/steps;
        x1 = p1[0]*(1-t1)+p2[0]*t1 + radius*cos(360*coils*t1);
        y1 = p1[1]*(1-t1)+p2[1]*t1 + radius*sin(360*coils*t1);
        z1 = p1[2]*(1-t1)+p2[2]*t1;
        x2 = p1[0]*(1-t2)+p2[0]*t2 + radius*cos(360*coils*t2);
        y2 = p1[1]*(1-t2)+p2[1]*t2 + radius*sin(360*coils*t2);
        z2 = p1[2]*(1-t2)+p2[2]*t2;
        rounded_bar([x1,y1,z1],[x2,y2,z2],wire);
    }
}

// ---------- UPPER CUFF / SOCKET-LIKE THIGH/STUMP INTERFACE ----------
module upper_cuff() {
    color("#303030")
    difference() {
        hull() {
            translate([0, rear_sweep, cuff_z-upper_cuff_h/2]) oval_cylinder(1, upper_cuff_w*0.86, upper_cuff_d*0.78);
            translate([0, rear_sweep-6, cuff_z+upper_cuff_h/2]) oval_cylinder(1, upper_cuff_w, upper_cuff_d);
        }
        hull() {
            translate([0, rear_sweep, cuff_z-upper_cuff_h/2+wall]) oval_cylinder(1, upper_cuff_w*0.70, upper_cuff_d*0.58);
            translate([0, rear_sweep-6, cuff_z+upper_cuff_h/2+2]) oval_cylinder(1, upper_cuff_w*0.82, upper_cuff_d*0.70);
        }
        // front opening for fitting/soft tissue relief
        translate([0, rear_sweep+upper_cuff_d*0.42, cuff_z]) rotate([90,0,0])
            oval_cylinder(upper_cuff_d*1.2, upper_cuff_w*0.46, upper_cuff_h*0.60, center=true);
    }

    // soft rim
    color("#111111")
    difference() {
        translate([0, rear_sweep-6, cuff_z+upper_cuff_h/2]) oval_cylinder(8, upper_cuff_w+8, upper_cuff_d+8, center=true);
        translate([0, rear_sweep-6, cuff_z+upper_cuff_h/2]) oval_cylinder(9, upper_cuff_w*0.82, upper_cuff_d*0.70, center=true);
    }
}

// ---------- ARTICULATED SHANK ----------
module lower_shank() {
    // two side plates, not rods; swept like a limb segment
    for (side=[-1,1]) {
        x = side * shank_w/2;
        color("#242424")
        capsule([x, rear_sweep*0.55, knee_z], [x*0.80, forward_sweep*0.35, ankle_z], 5, 8, 5);

        // inner lighter reinforcing rib
        color("#4A4A4A")
        capsule([x*0.78, rear_sweep*0.50, knee_z-8], [x*0.62, forward_sweep*0.30, ankle_z+8], 2.5, 4, 2.5);
    }

    // cross members
    color("#1A1A1A") {
        rounded_bar([-shank_w/2, rear_sweep*0.55, knee_z], [shank_w/2, rear_sweep*0.55, knee_z], 4);
        rounded_bar([-shank_w*0.40, forward_sweep*0.35, ankle_z], [shank_w*0.40, forward_sweep*0.35, ankle_z], 4);
    }
}

// ---------- FOOT / PAW MECHANISM ----------
module articulated_foot() {
    // main boot-like paw pad: curved toe and heel, not human shoe
    color("#1E1E1E")
    hull() {
        translate([0, foot_center_y-foot_len*0.42, 12]) ellipsoid(foot_w*0.36, foot_len*0.16, 11);
        translate([0, foot_center_y-foot_len*0.05, 14]) ellipsoid(foot_w*0.52, foot_len*0.32, 14);
        translate([0, foot_center_y+foot_len*0.40, 20]) ellipsoid(foot_w*0.40, foot_len*0.18, 12);
    }

    // flexible sole/contact pad
    color("#050505")
    translate([0, foot_center_y-foot_len*0.02, 5])
    hull() {
        translate([0, -foot_len*0.28, 0]) oval_cylinder(8, foot_w*0.70, foot_len*0.16, center=true);
        translate([0, 0, 0]) oval_cylinder(8, foot_w*0.95, foot_len*0.38, center=true);
        translate([0, foot_len*0.34, 0]) oval_cylinder(8, foot_w*0.70, foot_len*0.16, center=true);
    }

    // toe flex plate / rocker front
    color("#303030")
    capsule([0, foot_center_y+foot_len*0.10, 22], [0, foot_center_y+foot_len*0.48, 29], foot_w*0.30, 7, 4);

    // ankle mounting saddle
    color("#222222")
    translate([0, forward_sweep*0.35, ankle_z-4]) ellipsoid(shank_w*0.62, 14, 9);
}

// ---------- HINGES + TENDON SYSTEM ----------
module joints_and_tendons() {
    // knee/hock hinge
    hinge_at([0, rear_sweep*0.55, knee_z]);
    // ankle/paw hinge
    hinge_at([0, forward_sweep*0.35, ankle_z]);

    // posterior elastic tendon/spring from cuff to heel/ankle
    color("#111111") {
        rounded_bar([0, rear_sweep-22, cuff_z+10], [0, rear_sweep*0.55-14, knee_z-6], tendon_d/2);
        rounded_bar([0, rear_sweep*0.55-14, knee_z-6], [0, forward_sweep*0.35-16, ankle_z+4], tendon_d/2);
    }

    color("#777777")
    spring_between([0, rear_sweep*0.55-18, knee_z-12], [0, forward_sweep*0.35-18, ankle_z+12], 7, spring_d, 1.4);

    // anterior flexor cable/spring to lift toe
    color("#161616")
    rounded_bar([0, forward_sweep*0.35+10, ankle_z], [0, foot_center_y+foot_len*0.42, 28], tendon_d/2);

    color("#808080")
    spring_between([0, forward_sweep*0.35+13, ankle_z-2], [0, foot_center_y+foot_len*0.28, 24], 5, 5, 1.2);

    // mechanical extension stops
    color("#111111") {
        translate([-shank_w/2-4, rear_sweep*0.55, knee_z-10]) cube([6, 16, 10], center=true);
        translate([ shank_w/2+4, rear_sweep*0.55, knee_z-10]) cube([6, 16, 10], center=true);
    }
}

// ---------- ASSEMBLY ----------
module biomech_limb_v4() {
    upper_cuff();
    lower_shank();
    articulated_foot();
    joints_and_tendons();
}

biomech_limb_v4();

// Notes:
// - This is a biomechanical architecture concept, not a single rigid prosthetic foot.
// - Real version requires hinge sizing, spring constants, load testing, fatigue testing and veterinary fitting.
