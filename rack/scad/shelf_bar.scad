
//====================================================================//
//======================= scad/shelf_bar.scad ========================//
//                                                                    //
// Autogenerated using py2scad. Hand editing this file is not         //
// advisable as all modifications will be lost when the program which //
// generated this file is re-run.                                     //
//====================================================================//

$fn = 50;
projection(cut=true) {
    difference() {
        union() {
            cube(size=[22.40000, 258.80000, 3.00000], center=true);
            translate(v=[11.20000, 0.00000, 0.00000]) {
                cube(size=[3.00000, 258.80000, 3.00000], center=true);
            }
            translate(v=[-11.20000, 0.00000, 0.00000]) {
                cube(size=[3.00000, 258.80000, 3.00000], center=true);
            }
            translate(v=[0.00000, 129.40000, 0.00000]) {
                cube(size=[22.40000, 3.00000, 3.00000], center=true);
            }
            translate(v=[0.00000, -129.40000, 0.00000]) {
                cube(size=[22.40000, 3.00000, 3.00000], center=true);
            }
            translate(v=[-11.20000, -129.40000, 0.00000]) {
                cylinder(h=3.00000,r1=1.50000,r2=1.50000,center=true);
            }
            translate(v=[-11.20000, 129.40000, 0.00000]) {
                cylinder(h=3.00000,r1=1.50000,r2=1.50000,center=true);
            }
            translate(v=[11.20000, -129.40000, 0.00000]) {
                cylinder(h=3.00000,r1=1.50000,r2=1.50000,center=true);
            }
            translate(v=[11.20000, 129.40000, 0.00000]) {
                cylinder(h=3.00000,r1=1.50000,r2=1.50000,center=true);
            }
        }
        translate(v=[0.00000, -62.30000, 0.00000]) {
            cylinder(h=12.00000,r1=2.55270,r2=2.55270,center=true);
        }
        translate(v=[0.00000, 62.30000, 0.00000]) {
            cylinder(h=12.00000,r1=2.55270,r2=2.55270,center=true);
        }
    }
}
