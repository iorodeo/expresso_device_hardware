
//====================================================================//
//===================== scad/plunger_strip.scad ======================//
//                                                                    //
// Autogenerated using py2scad. Hand editing this file is not         //
// advisable as all modifications will be lost when the program which //
// generated this file is re-run.                                     //
//====================================================================//

$fn = 50;
projection(cut=true) {
    translate(v=[180.55000, 0.00000, 0.00000]) {
        difference() {
            difference() {
                difference() {
                    difference() {
                        difference() {
                            difference() {
                                cube(size=[11.00000, 127.00000, 3.00000], center=true);
                                translate(v=[0.00000, -57.15000, 0.00000]) {
                                    cylinder(h=12.00000,r1=1.13030,r2=1.13030,center=true);
                                }
                                translate(v=[0.00000, -12.70000, 0.00000]) {
                                    cylinder(h=12.00000,r1=1.13030,r2=1.13030,center=true);
                                }
                                translate(v=[0.00000, 12.70000, 0.00000]) {
                                    cylinder(h=12.00000,r1=1.13030,r2=1.13030,center=true);
                                }
                                translate(v=[0.00000, 57.15000, 0.00000]) {
                                    cylinder(h=12.00000,r1=1.13030,r2=1.13030,center=true);
                                }
                            }
                            translate(v=[0.00000, 50.80000, 1.50000]) {
                                cylinder(h=3.00000,r1=4.00000,r2=4.00000,center=true);
                            }
                        }
                        translate(v=[0.00000, 25.40000, 1.50000]) {
                            cylinder(h=3.00000,r1=4.00000,r2=4.00000,center=true);
                        }
                    }
                    translate(v=[0.00000, 0.00000, 1.50000]) {
                        cylinder(h=3.00000,r1=4.00000,r2=4.00000,center=true);
                    }
                }
                translate(v=[0.00000, -25.40000, 1.50000]) {
                    cylinder(h=3.00000,r1=4.00000,r2=4.00000,center=true);
                }
            }
            translate(v=[0.00000, -50.80000, 1.50000]) {
                cylinder(h=3.00000,r1=4.00000,r2=4.00000,center=true);
            }
        }
    }
}

