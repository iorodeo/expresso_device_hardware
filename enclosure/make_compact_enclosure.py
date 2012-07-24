"""
Creates an enclosure
"""
import os.path
import subprocess
from py2scad import *
from compact_enclosure import *
import glob, os

INCH2MM = 25.4
SLOT_TOL = .254
create_dxf=True

# Inside dimensions
x,y,z = 61.4, 8.0*INCH2MM, 0.75*INCH2MM 
capillary_diam = 1.0
hole_list = []

params = {
        'inner_dimensions'                   : (x,y,z), 
        'inner_dimension_offset'             : 0.5*INCH2MM,
        'number_of_sensors'                  : 5,
        'sensor_spacing'                     : 1.0*INCH2MM,
        'bottom_mount_hole_diam'             : 0.2010*INCH2MM, 
        'bottom_mount_hole_spacing'          : 1.0*INCH2MM,
        'bottom_mount_hole_inset'            : 0.5*INCH2MM,
        'wall_thickness'                     : 3.0, 
        'lid_radius'                         : 1.5,  
        'top_x_overhang'                     : 1.5,
        'top_y_overhang'                     : 1.5,
        'bottom_x_overhang'                  : 16.0,
        'bottom_y_overhang'                  : 1.0*INCH2MM-5.65, 
        'lid2front_tabs'                     : (0.25,0.75),
        'lid2side_tabs'                      : (0.41, 0.77),
        'side2side_tabs'                     : (0.5,),
        'lid2front_tab_width'                : 7.0,
        'lid2side_tab_width'                 : 7.0, 
        'side2side_tab_width'                : 7.0,
        'standoff_diameter'                  : 0.1895*INCH2MM,
        'standoff_offset'                    : 0.05*INCH2MM,
        'standoff_hole_diameter'             : 0.089*INCH2MM, 
        'capillary_diam'                     : capillary_diam,
        'capillary_hole_size'                : (9,1.5,0.2),  
        'capillary_hole_offset'              : 0.05*INCH2MM,
        'capillary_length'                   : 5*INCH2MM,
        'capillary_clamp_thru_hole_diam'     : 0.12*INCH2MM,
        'capillary_clamp_tap_hole_diam'      : 0.089*INCH2MM,
        'capillary_clamp_thru_hole_offset_x' : 5,
        'capillary_clamp_thru_hole_offset_y' : -2.5,
        'capillary_clamp_tap_hole_offset_y'  : -2.5,
        'capillary_clamp_length'           : 18.0,
        'capillary_clamp_width'            : 7.0,
        'capillary_clamp_radius'           : 1.5,
        'sensor_width'                     : 12.95,
        'sensor_length'                    : 61.33,
        'sensor_padding'                   : .254,
        'sensor_dimensions'                : (61.33,12.95,3.3),
        'sensor_ypos_offset'               : .5*INCH2MM, #from end of pcb
        'sensor_hole_offset'               : 0.685,
        'sensor_mount_hole_space'          : 57.40, 
        'sensor_mount_hole_diam'           : 0.11*INCH2MM, 
        'led_pcb_dimensions'               : (61.0, 7*25.4, 1.7),
        'led_pcb_thru_hole_diam'           : 0.0890*INCH2MM,
        'led_pcb_tap_hole_diam'            : 0.0641*INCH2MM,
        'led_pcb_hole_offset_x'            : 0.1*INCH2MM,
        'led_pcb_hole_offset_y'            : 0.1*INCH2MM,
        'led_cable_hole_size'              : (6.0,4.0),
        'led_cable_hole_y_offset'          : 0.5*INCH2MM,
        'diffuser_dimensions'              : (61.0 ,5*25.4, 1.5),
        'diffuser_standoff_height'         : (7/32.0)*INCH2MM,
        'diffuser_standoff_diam'           : (3/16.0)*INCH2MM,
        'diffuser_offset'                  : 0.9*INCH2MM,
        'hole_list'                        : hole_list,
        'guide_plate_dimensions'           : (x-0.2, 0.5*INCH2MM-.5*capillary_diam, 0.0625*INCH2MM),
        'guide_thru_hole_diam'             : 0.0890*INCH2MM,
        'guide_tap_hole_diam'              : 0.0641*INCH2MM,
        'guide_hole_offset'                : 0.11*INCH2MM,
        'guide_plate_asym'                 : (.7,),
        'guide_plate_cutout_y'             : (0,.25),
        'guide_plate_cutout_x'             : 50,
        'maple_y_offset'                   : 1.25*INCH2MM, #from end of pcb
        'maple_width'                      : 0.72*INCH2MM,
        'maple_length'                     : 2.02*INCH2MM,
        'maple_hole_size'                  : (1.4,1.4,0.2),  
        'usb_hole_size'                    : (7.8,4.4,.2),
        'usb_pos'                          : 15.3,
        'power_y_offset'                   : .5315*INCH2MM, #from end of pcb
        'power_width'                      : 0.317*INCH2MM,
        'power_plug_offset'                : 1.5,
        'power_length'                     : 0.366*INCH2MM,
        'power_height'                     : 8.6,
        'connector_length'                 : 10,
        'connector_width'                  : 4.5,
        'vial_holder_offset_x'             : 0.25*INCH2MM,
        'vial_holder_offset_y'             : 1.0*INCH2MM,
        'vial_diam'                        : 10.5,
        'vial_length'                      : 42,
        'vial_holder_tab_length'           : 7,
        'vial_holder_slot_length'          : 7-SLOT_TOL,
        'vial_holder_slot_width'           : 3-SLOT_TOL,
        'vial_holder_rail_length'          : 30,
        'vial_holder_rail_width'           : 2.8,
        'vial_holder_spacer_length'        : 6.35,
        'vial_holder_spacer_diam'          : 3,
        'vial_holder_wall_size'            : (2*9.85,2*9.85),
        'vial_holder_wall_thickness'       : 3,
        'vial_holder_dimensions'           : (61.0 ,5.5*25.4, .125*INCH2MM), 
        'rails_y_offset'                   : .25*INCH2MM
        }

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    
    enclosure = Compact_Enclosure(params)
    enclosure.make()
    
    part_assembly = enclosure.get_assembly(
            show_top=False,
            show_bottom=False, 
            show_front=False,
            show_back=False,
            show_left=False,
            show_right=False,
            show_standoffs=False,
            show_capillary=False,
            show_sensor=False,
            show_diffuser=False,
            show_vial_holder=False,
            show_vial=False,
            show_diffuser_standoffs=False,
            show_led_pcb=False,
            show_guide_plates=True,
            show_guide_top=False,
            show_clamp=False,
            gen_stl=False,
            explode=(0,0,0),
            )
    
    #print enclosure.standoff_xy_pos
    projection_parts = []
    box_projection = enclosure.get_box_projection()
    diffuser_projection = enclosure.get_diffuser_projection()
    top_guide_projection = enclosure.get_top_guide_projection()
    side_guide_projection = enclosure.get_side_guide_projection()
    #vial_holder_projection = enclosure.get_vial_holder_projection()

    projection_parts.extend(box_projection)
    projection_parts.extend(diffuser_projection)
    projection_parts.extend(top_guide_projection)
    projection_parts.extend(side_guide_projection)
    #projection_parts.extend(vial_holder_projection)
    
    # Write assembly scad file
    prog_assembly = SCAD_Prog()
    prog_assembly.fn = 50
    #prog_assembly.add(part_assembly)
    prog_assembly.add(projection_parts)
    prog_assembly.write('compact_assembly.scad')
    
    # Write scad file for projections
    scad_projection_files = []

    cnt = 0
    #projection_parts = []
    #side_guide_projection = enclosure.get_side_guide_projection()
    #projection_parts.extend(side_guide_projection)
    #part = projection_parts

    parts_names = [
                    'top',
                    'bottom',
                    'left_wall',
                    'right_wall',
                    'front',
                    'back',
                    'ref_cube',
                    'clamp',
                    'diffuser',
                    'guide_top',
                    'guide_side_pos_A',
                    'guide_side_neg_A',
                    'guide_side_pos_B',
                    'guide_side_neg_B',
                  ]
    n = len(parts_names)

    if 1:
        for part in projection_parts:       
            cnt+=1
            if (cnt > n) or (cnt < (n-1)):
                continue
            filename = 'dxf/'+parts_names[cnt-1]+'.scad'
            prog_projection = SCAD_Prog()
            prog_projection.fn = 50
            prog_projection.add(part)
            prog_projection.write(filename)
            scad_projection_files.append(filename)

    # Create dxf files
    if create_dxf:
        for scad_name in scad_projection_files:
            base_name, ext = os.path.splitext(scad_name)
            dxf_name = '{0}.dxf'.format(base_name)
            print '{0} -> {1}'.format(scad_name, dxf_name)
            subprocess.call(['openscad', '-x', dxf_name, scad_name])
