
//====================================================================//
//======================= scad/guide_top.scad ========================//
//                                                                    //
// Autogenerated using py2scad. Hand editing this file is not         //
// advisable as all modifications will be lost when the program which //
// generated this file is re-run.                                     //
//====================================================================//

$fn = 50;
projection(cut=true) {
    translate(v=[-203.85000, 0.00000, 0.00000]) {
        difference() {
            cube(size=[61.20000, 25.30000, 1.58750], center=true);
            translate(v=[-28.06000, -10.11000, 0.00000]) {
                cylinder(h=6.35000,r1=1.13030,r2=1.13030,center=true);
            }
            translate(v=[-28.06000, 10.11000, 0.00000]) {
                cylinder(h=6.35000,r1=1.13030,r2=1.13030,center=true);
            }
            translate(v=[28.06000, -10.11000, 0.00000]) {
                cylinder(h=6.35000,r1=1.13030,r2=1.13030,center=true);
            }
            translate(v=[28.06000, 10.11000, 0.00000]) {
                cylinder(h=6.35000,r1=1.13030,r2=1.13030,center=true);
            }
        }
    }
}
