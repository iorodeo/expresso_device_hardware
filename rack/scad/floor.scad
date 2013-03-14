
//====================================================================//
//========================= scad/floor.scad ==========================//
//                                                                    //
// Autogenerated using py2scad. Hand editing this file is not         //
// advisable as all modifications will be lost when the program which //
// generated this file is re-run.                                     //
//====================================================================//

$fn = 50;
projection(cut=true) {
    difference() {
        difference() {
            union() {
                cube(size=[365.30000, 301.98000, 6.30000], center=true);
                translate(v=[182.65000, 0.00000, 0.00000]) {
                    cube(size=[3.00000, 301.98000, 6.30000], center=true);
                }
                translate(v=[-182.65000, 0.00000, 0.00000]) {
                    cube(size=[3.00000, 301.98000, 6.30000], center=true);
                }
                translate(v=[0.00000, 150.99000, 0.00000]) {
                    cube(size=[365.30000, 3.00000, 6.30000], center=true);
                }
                translate(v=[0.00000, -150.99000, 0.00000]) {
                    cube(size=[365.30000, 3.00000, 6.30000], center=true);
                }
                translate(v=[-182.65000, -150.99000, 0.00000]) {
                    cylinder(h=6.30000,r1=1.50000,r2=1.50000,center=true);
                }
                translate(v=[-182.65000, 150.99000, 0.00000]) {
                    cylinder(h=6.30000,r1=1.50000,r2=1.50000,center=true);
                }
                translate(v=[182.65000, -150.99000, 0.00000]) {
                    cylinder(h=6.30000,r1=1.50000,r2=1.50000,center=true);
                }
                translate(v=[182.65000, 150.99000, 0.00000]) {
                    cylinder(h=6.30000,r1=1.50000,r2=1.50000,center=true);
                }
            }
            translate(v=[-127.00000, -127.75000, 0.00000]) {
                cube(size=[24.89200, 6.04600, 12.60000], center=true);
            }
            translate(v=[-127.00000, 127.75000, 0.00000]) {
                cube(size=[24.89200, 6.04600, 12.60000], center=true);
            }
            translate(v=[-63.50000, -127.75000, 0.00000]) {
                cube(size=[24.89200, 6.04600, 12.60000], center=true);
            }
            translate(v=[-63.50000, 127.75000, 0.00000]) {
                cube(size=[24.89200, 6.04600, 12.60000], center=true);
            }
            translate(v=[0.00000, -127.75000, 0.00000]) {
                cube(size=[24.89200, 6.04600, 12.60000], center=true);
            }
            translate(v=[0.00000, 127.75000, 0.00000]) {
                cube(size=[24.89200, 6.04600, 12.60000], center=true);
            }
            translate(v=[63.50000, -127.75000, 0.00000]) {
                cube(size=[24.89200, 6.04600, 12.60000], center=true);
            }
            translate(v=[63.50000, 127.75000, 0.00000]) {
                cube(size=[24.89200, 6.04600, 12.60000], center=true);
            }
            translate(v=[127.00000, -127.75000, 0.00000]) {
                cube(size=[24.89200, 6.04600, 12.60000], center=true);
            }
            translate(v=[127.00000, 127.75000, 0.00000]) {
                cube(size=[24.89200, 6.04600, 12.60000], center=true);
            }
        }
        translate(v=[-95.25000, 139.79000, 0.00000]) {
            cylinder(h=25.20000,r1=2.55270,r2=2.55270,center=true);
        }
        translate(v=[-95.25000, -139.79000, 0.00000]) {
            cylinder(h=25.20000,r1=2.55270,r2=2.55270,center=true);
        }
        translate(v=[-31.75000, 139.79000, 0.00000]) {
            cylinder(h=25.20000,r1=2.55270,r2=2.55270,center=true);
        }
        translate(v=[-31.75000, -139.79000, 0.00000]) {
            cylinder(h=25.20000,r1=2.55270,r2=2.55270,center=true);
        }
        translate(v=[31.75000, 139.79000, 0.00000]) {
            cylinder(h=25.20000,r1=2.55270,r2=2.55270,center=true);
        }
        translate(v=[31.75000, -139.79000, 0.00000]) {
            cylinder(h=25.20000,r1=2.55270,r2=2.55270,center=true);
        }
        translate(v=[95.25000, 139.79000, 0.00000]) {
            cylinder(h=25.20000,r1=2.55270,r2=2.55270,center=true);
        }
        translate(v=[95.25000, -139.79000, 0.00000]) {
            cylinder(h=25.20000,r1=2.55270,r2=2.55270,center=true);
        }
    }
}

