"""
Creates the rack for stacking 1 to 4 IO Rodeo Expresso devices,
a 5-channel fluid-level detector for measuring the amount of liquid
inside capillary tubes.
"""
import os.path
import subprocess
from py2scad import *
from expresso_rack import *
import math, sys
#from arrayed_enclosure import Arrayed_Enclosure
#from make_enclosure import params as arrayed_enclosure_params

# Conversion constants
INCH2MM = 25.4
DEG2RAD = math.pi/180
RAD2DEG = 180/math.pi

# Inside dimensions enclosure
x,y,z = 61.4, 8.0*INCH2MM, 0.75*INCH2MM 
wall_thickness_enc = 3.
bottom_x_overhang = 14.3
bottom_y_overhang = 1.*INCH2MM-5.65 

x_e = x + 2.*wall_thickness_enc + 2.*bottom_x_overhang
y_e = y + 2.*wall_thickness_enc + 2.*bottom_y_overhang
z_e = z

#Inside dimensions rack
N = 5
wall_thickness_enc = 6.
x_r = N*2.5*INCH2MM
y_r = y_e
z_r = 6.*INCH2MM

hole_list = []

params = {
        # Rack parameters
        'inner_dimensions'      : (x_r,y_r,z_r),
        'wall_thickness'        : wall_thickness_enc,
        'x_r_overhang'          : 1.*INCH2MM,
        'y_r_overhang'          : 1.*INCH2MM,
        'num_devices'           : N,        
  #'wall_tab_width'   : wall_tab_width,
  #'floor_dimensions' : (x_floor,y_floor,z_floor),
  #'deck_dimensions'  : (x_deck,y_deck,z_deck),
  #'wall_tabs'        : (1/6,1/3,1/2,2/3,5/6),
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
  #'tilt_angle'         : -45,
  #'projection_spacing' : .5*INCH2MM,
  #'bs_shift_z'          : .25*INCH2MM
        }

# -----------------------------------------------------------------------------
if __name__ == '__main__':

    rack = Expresso_Rack(params)
    rack.make()

    create_dxf=False

    part_assembly = rack.get_assembly(
            show_walls=True,
            explode=(0,0,4),
            )

    # Write assembly scad file
    prog_assembly = SCAD_Prog()
    prog_assembly.fn = 50
    prog_assembly.add(part_assembly)
    prog_assembly.write('scad/rack_assembly.scad')
