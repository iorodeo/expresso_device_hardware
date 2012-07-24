"""
Creates a rack for an array of capillary sensors
"""
from __future__ import division
from py2scad import *
from capillary_rack import *
import subprocess
import math, sys

sys.path.append('/home/cisco/repos/iorodeo/capillary_sensor_enclosure')
#sys.path.append('/home/xisco/Work/IORodeo/capillary_sensor_enclosure')
from arrayed_enclosure import Arrayed_Enclosure
from make_enclosure import params as arrayed_enclosure_params

INCH2MM = 25.4
DEG2RAD = math.pi/180
RAD2DEG = 180/math.pi

create_dxf = True

def main():
    #   Array     
    #  _______   
    # |       |y  
    # |_______|   
    #     x      
    
    x_arr = 10.236*INCH2MM
    y_arr = 3.283*INCH2MM
    z_arr = .125*INCH2MM

    num_decks = 5
    wall_overhang = 1.*INCH2MM
    x_wall = 7*INCH2MM
    y_wall = num_decks*y_arr+wall_overhang
    z_wall = 6
    wall_tab_width = y_arr/4
    wall_hole_list = [(x_wall/2.-.5*INCH2MM,y_wall*.25,.2*INCH2MM), #bracket holes
                      (x_wall/2.-.5*INCH2MM,-y_wall*.25,.2*INCH2MM)]
    wall_deck_hole_y = [-1./3.,-1./6.,0.,1./6.,1./3.]
    for i in range(num_decks):
        wall_hole_list.append((-1.5*INCH2MM,wall_deck_hole_y[i]*y_wall,.2*INCH2MM))
        wall_hole_list.append(( 1.25*INCH2MM,wall_deck_hole_y[i]*y_wall,.2*INCH2MM))
    # Adding holes for stabilizing rods
    wall_hole_list.append((0,y_wall/2-.375*INCH2MM,.25*INCH2MM))
    wall_hole_list.append((0,-y_wall/2+.375*INCH2MM,.25*INCH2MM))

    floor_overhang  = 1.*INCH2MM
    x_floor = x_arr+2.*floor_overhang
    y_floor = y_wall
    z_floor = .25*INCH2MM
    floor_slot_x = x_arr/2.-z_wall/2.
    floor_slot_y = [-1./3.,-1./6.,0.,1./6.,1./3.]
    floor_slot_pos = []
    floor_slot_size = []
    depth_adjust = .254 # 1/10 of an inch adjust
    for i in range(5):
        floor_slot_pos.append((floor_slot_x,floor_slot_y[i]*y_floor)) 
        floor_slot_pos.append((-floor_slot_x,floor_slot_y[i]*y_floor)) 
        floor_slot_size.append((z_wall-depth_adjust,wall_tab_width-depth_adjust))
        floor_slot_size.append((z_wall-depth_adjust,wall_tab_width-depth_adjust))

    floor_hole_list = [( floor_slot_x-.5*INCH2MM-z_wall/2.,y_wall*.25,.2*INCH2MM), #bracket holes
                       (-floor_slot_x+.5*INCH2MM+z_wall/2.,y_wall*.25,.2*INCH2MM),
                       ( floor_slot_x-.5*INCH2MM-z_wall/2.,-y_wall*.25,.2*INCH2MM),
                       (-floor_slot_x+.5*INCH2MM+z_wall/2.,-y_wall*.25,.2*INCH2MM),
                       (0,-1.25*INCH2MM,.2*INCH2MM), #usb hub holes
                       (0,1.25*INCH2MM,.2*INCH2MM)]

    x_deck = 4*INCH2MM
    y_deck = y_arr*.75
    # Thicker decks will prevent the enclosures from dropping
    z_deck = 6
    deck_slot_pos = [(-x_deck*7./16.,y_deck/4)]
    deck_slot_size = [(y_arr+2*depth_adjust,1.*INCH2MM/8)]
    # The holes on the decks should be thru holes
    deck_hole_list = [(-1.75*INCH2MM,0,.25*INCH2MM), #deck-to-wall holes
                      (1.*INCH2MM,0,.25*INCH2MM)]

    params = {
              'array_dimensions' : (x_arr,y_arr,z_arr),
              'wall_dimensions'  : (x_wall,y_wall,z_wall),
              'wall_tab_width'   : wall_tab_width,
              'floor_dimensions' : (x_floor,y_floor,z_floor),
              'deck_dimensions'  : (x_deck,y_deck,z_deck),
              'wall_tabs'        : (1/6,1/3,1/2,2/3,5/6),
              'wall_holes'       : wall_hole_list,
              'floor_slot_pos'   : floor_slot_pos,
              'floor_slot_size'  : floor_slot_size,
              'floor_hole_list'  : floor_hole_list,
              'deck_slot_pos'    : deck_slot_pos,
              'deck_slot_size'   : deck_slot_size,
              'deck_hole_list'   : deck_hole_list,
              'corner_radius'    : 1.5,
              'wall_overhang'    : wall_overhang,
              'bracket_filename' : 'stl/8020-4119.stl',
              'bracket_width'    : 1.0*INCH2MM,
              'enclosure_stl_path' : '/home/cisco/Work/capillary_sensor_enclosure/stl',
              'tilt_angle'         : -45,
              'projection_spacing' : .5*INCH2MM,
              'bs_shift_z'          : .25*INCH2MM
            }

    rack = Capillary_Rack(params)
    rack.make()
    part_assembly = rack.get_assembly(
            gen_stl=False,
            include_brackets=False,
            include_enclosure=True,
            explode=(0,0,0)
        )
    prog_assembly = SCAD_Prog()
    prog_assembly.fn = 100 # Raised to 100 or otherwise STL won't show
    prog_assembly.add(part_assembly)
    prog_assembly.write('rack_assembly.scad')

    part_projection = rack.get_projection()
    prog_projection = SCAD_Prog()
    prog_projection.fn = 50 # Raised to 100 or otherwise STL won't show
    prog_projection.add(part_projection)
    prog_projection.write('rack_projection.scad')
    
    subprocess.call(['openscad', '-x', 'dxf/rack_projection.dxf', 'rack_projection.scad'])

    if create_dxf:
        print "try"
        cnt = 0
        scad_projection_files = []
        for part in rack.get_projection(): 
            cnt+=1
            if (cnt < 0):
                continue
            filename = 'dxf/'+str(cnt)+'.scad'
            prog_projection = SCAD_Prog()
            prog_projection.fn = 50
            prog_projection.add(part)
            prog_projection.write(filename)
            scad_projection_files.append(filename)

        for scad_name in scad_projection_files:
            base_name, ext = os.path.splitext(scad_name)
            dxf_name = '{0}.dxf'.format(base_name)
            print '{0} -> {1}'.format(scad_name, dxf_name)
            subprocess.call(['openscad', '-x', dxf_name, scad_name])

if __name__ == "__main__":
    main()
