"""
Creates the rack for stacking 1 to 4 IO Rodeo Expresso devices,
a 5-channel fluid-level detector for measuring the amount of liquid
inside capillary tubes.
"""
import os.path
import subprocess
from py2scad import *
from expresso_rack import *
import sys

#########################################
# Rack configuration
#########################################
# Number of devices to include
N = 5
# Desired tilt angle on the rack (typical: -45)
tilt_angle = -45 #degrees
#########################################

# Conversion constants
INCH2MM = 25.4

# Inside dimensions enclosure
x,y,z = 61.4, 8.0*INCH2MM, 0.75*INCH2MM 
wall_thickness_enc = 3.25
bottom_x_overhang = 16.3
bottom_y_overhang = 1.*INCH2MM-5.65 

x_e = x + 2.*wall_thickness_enc + 2.*bottom_x_overhang
y_e = y + 2.*wall_thickness_enc + 2.*bottom_y_overhang
z_e = z

#Inside dimensions rack
wall_thickness_rack = 6.3
x_r = N*2.5*INCH2MM
y_r = y_e
z_r = 6.*INCH2MM

hole_list = []

params = {
        # Rack parameters
        'num_devices'           : N,        
        'inner_dimensions'      : (x_r,y_r,z_r),
        'wall_thickness'        : wall_thickness_rack,
        'wall_thickness_enc'    : wall_thickness_enc,
        'x_r_overhang'          : 1.*INCH2MM,
        'y_r_overhang'          : 1.*INCH2MM-0.15*INCH2MM,
        'corner_radius'         : 1.5,
        'wall_tab_dist'         : 1.25*INCH2MM,
        'wall_tab_width'        : 1.*INCH2MM,
        'wall_hole_dia_thru'    : .2570*INCH2MM,
        'wall_hole_dia_tap'     : .2010*INCH2MM,
        'wall_hole_y_offset'    : .5*INCH2MM, # from the floors' surface
        'floor_hole_y_offset'   : .5*INCH2MM, # from the floors' end, including overhang
        'floor_hole_dia_thru'   : .2570*INCH2MM,
        'floor_hole_dia_tap'    : .2010*INCH2MM,
        'holder_height'         : 4.*INCH2MM,
        'holder_slot_size'      : (wall_thickness_enc,.6*x_e),
        'floor_slot_tol'        : (.02*INCH2MM,.01*INCH2MM),
        'tilt_angle'            : tilt_angle,
        'holder_z_offset'       : 1.*INCH2MM, # from the floors' surface
        'holder_hole_offset'    : (-1.75*INCH2MM,1.75*INCH2MM),
        'stability_rod_dia'     : .5*INCH2MM,
        'stability_rod_x_offset': .5*INCH2MM,
        'shelf_slot_pos'        : (1.5*INCH2MM,1.375*INCH2MM,1.25*INCH2MM),
        'shelf_slot_thickness'  : 3,
        'shelf_slot_num'        : 6,
        'shelf_z_offset'        : -9
        }

# -----------------------------------------------------------------------------
if __name__ == '__main__':

    rack = Expresso_Rack(params)
    rack.make()

    create_dxf=True

    part_assembly = rack.get_assembly(
            show_walls=True,
            show_floor=True,
            show_holders=True,
            show_shelf=True,
            show_bar=True,
            explode=(0,0,0),
            )

    # Write assembly scad file
    prog_assembly = SCAD_Prog()
    prog_assembly.fn = 50
    prog_assembly.add(part_assembly)
    prog_assembly.write('scad/rack_assembly.scad')

    # Write projection scad file
    projection_parts = []
    walls_projection = rack.get_walls_projection()
    floor_projection = rack.get_floor_projection()
    holders_projection = rack.get_holders_projection()
    shelf_projection = rack.get_shelf_projection()

    projection_parts.extend(walls_projection)
    projection_parts.extend(floor_projection)
    projection_parts.extend(holders_projection)
    projection_parts.extend(shelf_projection)
    
    ## Write assembly scad file
    #prog_assembly = SCAD_Prog()
    #prog_assembly.fn = 50
    #prog_assembly.add(projection_parts)
    #prog_assembly.write('scad/enclosure_projection.scad')
        
    # Write scad file for projections
    scad_projection_files = []

    parts_names = [
                    'left_wall',
                    'right_wall',
                    'floor',
                    'left_holder',
                    'right_holder',
                    'shelf',
                    'shelf_bar',
                  ]

    n = len(parts_names)
    i = 0
    #projection_parts.sort()
    for part in projection_parts:       
        filename = 'scad/'+parts_names[i]+'.scad'
        prog_projection = SCAD_Prog()
        prog_projection.fn = 50
        prog_projection.add(part)
        prog_projection.write(filename)
        scad_projection_files.append(filename)
        i+=1

    # Create dxf files
    if create_dxf:
        for scad_name in scad_projection_files:
            base_name,ext = os.path.splitext(scad_name)
            dir_name,file_name = os.path.split(base_name)
            dxf_name = 'dxf/{0}.dxf'.format(file_name)
            print '{0} -> {1}'.format(scad_name, dxf_name)
            subprocess.call(['openscad', '-x', dxf_name, scad_name])
# Legacy
#'wall_tabs'        : (1/6,1/3,1/2,2/3,5/6),
#'wall_tab_width'   : wall_tab_width,
#'floor_dimensions' : (x_floor,y_floor,z_floor),
#'deck_dimensions'  : (x_deck,y_deck,z_deck),
#'wall_holes'       : wall_hole_list,
#'floor_slot_pos'   : floor_slot_pos,
#'floor_slot_size'  : floor_slot_size,
#'floor_hole_list'  : floor_hole_list,
#'deck_slot_pos'    : deck_slot_pos,
#'deck_slot_size'   : deck_slot_size,
#'deck_hole_list'   : deck_hole_list,
#'corner_radius'    : 1.5,
#'wall_overhang'    : wall_overhang,
#'bracket_filename' : 'stl/8020-4119.stl',
#'bracket_width'    : 1.0*INCH2MM,
#'enclosure_stl_path' : '/home/cisco/Work/capillary_sensor_enclosure/stl',
#'projection_spacing' : .5*INCH2MM,
#'bs_shift_z'          : .25*INCH2MM
