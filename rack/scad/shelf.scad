
//====================================================================//
//========================= scad/shelf.scad ==========================//
//                                                                    //
// Autogenerated using py2scad. Hand editing this file is not         //
// advisable as all modifications will be lost when the program which //
// generated this file is re-run.                                     //
//====================================================================//

$fn = 50;
projection(cut=true) {
    difference() {
        union() {
            cube(size=[368.30000, 236.60000, 3.00000], center=true);
            translate(v=[171.45000, 118.30000, 0.00000]) {
                cube(size=[25.40000, 25.20000, 3.00000], center=true);
            }
            translate(v=[171.45000, -118.30000, 0.00000]) {
                cube(size=[25.40000, 25.20000, 3.00000], center=true);
            }
        }
        translate(v=[-171.45000, -62.30000, 0.00000]) {
            cylinder(h=12.00000,r1=3.26390,r2=3.26390,center=true);
        }
        translate(v=[-171.45000, 62.30000, 0.00000]) {
            cylinder(h=12.00000,r1=3.26390,r2=3.26390,center=true);
        }
    }
}

