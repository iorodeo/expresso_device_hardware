
//====================================================================//
//==================== scad/guide_side_neg_A.scad ====================//
//                                                                    //
// Autogenerated using py2scad. Hand editing this file is not         //
// advisable as all modifications will be lost when the program which //
// generated this file is re-run.                                     //
//====================================================================//

$fn = 50;
projection(cut=true) {
    translate(v=[-130.00000, -19.50000, 0.00000]) {
        difference() {
            union() {
                translate(v=[0.00000, 4.45000, 0.00000]) {
                    difference() {
                        cube(size=[73.20000, 4.00000, 1.58750], center=true);
                    }
                }
                difference() {
                    cube(size=[61.20000, 12.90000, 1.58750], center=true);
                    translate(v=[-28.06000, -3.56000, 0.00000]) {
                        cylinder(h=6.35000,r1=1.13030,r2=1.13030,center=true);
                    }
                    translate(v=[28.06000, -3.56000, 0.00000]) {
                        cylinder(h=6.35000,r1=1.13030,r2=1.13030,center=true);
                    }
                }
            }
            translate(v=[0.00000, 12.20000, 0.00000]) {
                translate(v=[0.00000, -5.75000, 0.00000]) {
                    cube(size=[50.00000, 0.00000, 1.00000], center=true);
                }
            }
        }
    }
}

