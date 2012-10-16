"""
Creates the enclosure for an array of 5x1 TAOS TSL1406R Linear Array sensors,
which are used to measure the fluid levels on a capillary tube placed atop 
the sensors.
"""
import os.path
import subprocess
from py2scad import *
from expresso_enclosure import *
import glob, os

# Conversion constants
INCH2MM = 25.4

# Inside dimensions
x,y,z = 61.4, 8.0*INCH2MM, 0.75*INCH2MM 

# TO-DO: Should be able to produce an enclosure for a range
# of capillary diameters
capillary_diam = 1.0
hole_list = []

params = {
        # Basic Enclosure parameters
        'inner_dimensions'                   : (x,y,z), 
        'wall_thickness'                     : 3., 
        'lid2front_tab_width'                : 7.,
        'lid2side_tab_width'                 : 7., 
        'side2side_tab_width'                : 7.,
        'lid2side_tabs'                      : (0.41, 0.77),
        'side2side_tabs'                     : (0.5,),
        'lid2front_tabs'                     : (0.25,0.75),
        'top_x_overhang'                     : 1.5,
        'top_y_overhang'                     : 1.5,
        'bottom_x_overhang'                  : 16.3,
        'bottom_y_overhang'                  : 1.*INCH2MM-5.65, 
        'lid_radius'                         : 1.5,  
        'standoff_diameter'                  : 0.1895*INCH2MM,
        'standoff_offset'                    : 0.05*INCH2MM,
        'standoff_hole_diameter'             : 0.089*INCH2MM, 

        # Expresso Enclosure parameters
        'hole_list'                          : hole_list,
        'number_of_sensors'                  : 5,
        'sensor_spacing'                     : 1.0*INCH2MM,
        'sensor_dimensions'                  : (61.33,12.95,3.3),
        'sensor_ypos_offset'                 : .5*INCH2MM, #from end of pcb
        'capillary_hole_size'                : (9,1.6,0.2),  
        'capillary_hole_offset'              : 0.05*INCH2MM, # physical offset of sensor 'cells' relative to sensor's longitudinal axis
        'guide_plate_asym'                   : (.7,), # asymmetry that offsets capillary tube over sensor
        'guide_plate_dimensions'             : (x-0.2, 0.5*INCH2MM-.5*capillary_diam, 0.0625*INCH2MM),
        'guide_thru_hole_diam'               : 0.0890*INCH2MM,
        'guide_tap_hole_diam'                : 0.0641*INCH2MM,
        'guide_hole_offset'                  : 0.10*INCH2MM,
        'guide_plate_cutout_y'               : (.0,), # cutout region to allow more light to hit the sensor
        'guide_plate_cutout_x'               : 50,
        'capillary_diam'                     : capillary_diam,
        'capillary_length'                   : 5*INCH2MM,
        'sensor_hole_offset'                 : 0.685,
        'sensor_mount_hole_diam'             : 0.11*INCH2MM, 
        'sensor_mount_hole_pos'              : 57.40, 
        'plunger_thru_hole_diam'             : 5,

        # LED PCB parameters
        'led_pcb_dimensions'                 : (61.0, 7*25.4, 1.7),
        'led_cable_hole_size'                : (6.0,4.0),
        'led_cable_hole_y_offset'            : 10.,
        'led_pcb_tap_hole_diam'              : 0.0641*INCH2MM,
        'led_pcb_hole_offset_x'              : 0.1*INCH2MM,
        'led_pcb_hole_offset_y'              : 0.1*INCH2MM,

        # Sensor PCB parameters,
        'sensor_pcb_dimensions'              : (61.0, 7.*INCH2MM, 1.7),
        'sensor_pcb_overhang_x'              : 8.5, #accounts for wall thickness
        'sensor_pcb_hole_offset_y'           : 0.1*INCH2MM,
        'sensor_pcb_hole_offset_x'           : 0.1*INCH2MM,
        'sensor_pcb_hole_pos_y'              : (44.575,95.25,146.05), #from end of pcb

        # Maple uController parameters
        'maple_y_offset'                     : 32., #from end of pcb
        'maple_width'                        : 0.72*INCH2MM,
        'maple_length'                       : 2.02*INCH2MM,
        'usb_hole_size'                      : (7.8,4.4,.2),
        'usb_pos'                            : 15.3,
        'power_y_offset'                     : 13.,
        'power_width'                        : 8.,
        'power_plug_offset'                  : 1.3, #relative to the power connector position
        'power_head_dia'                     : 10.6,
        'power_length'                       : 9.2,
        'power_height'                       : 5.6,

        # Diffuser parameters
        'diffuser_standoff_height'           : (7./32.0)*INCH2MM,
        'diffuser_standoff_diam'             : (3./16.0)*INCH2MM,
        'diffuser_dimensions'                : (61.0 ,5.5*25.4, 1.5),
        'diffuser_thru_hole_diam'            : 0.0890*INCH2MM,

        # Plunger strip parameters
        'plunger_strip_dimensions'           : (11.,5.*INCH2MM,3.),
        'plunger_strip_tap_hole_diam'        : 0.0641*INCH2MM,
        'plunger_strip_thru_hole_diam'       : 0.0890*INCH2MM,
        'plunger_strip_etched_hole_diam'     : 8,

        #'vial_diam'                        : 10.5,
        #'vial_length'                      : 42,
        }

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    
    enclosure = Expresso_Enclosure(params)
    enclosure.make()

    create_dxf=True
    
    part_assembly = enclosure.get_assembly(
            show_top=True,
            show_led_pcb=True,
            show_diffuser_standoffs=True,
            show_diffuser=True,
            show_front=True,
            show_back=True,
            show_left=True,
            show_right=True,
            show_standoffs=True,
            show_bottom=True, 
            show_guide_bottom=True,
            show_guide_top=True,
            show_capillary=True,
            show_sensor=True,
            show_sensor_pcb=True,
            show_plunger_strip=True,
            explode=(0,0,4),
            )

    # Write assembly scad file
    prog_assembly = SCAD_Prog()
    prog_assembly.fn = 50
    prog_assembly.add(part_assembly)
    prog_assembly.write('scad/enclosure_assembly.scad')

    # Write projection scad file
    projection_parts = []
    box_projection = enclosure.get_box_projection()
    diffuser_projection = enclosure.get_diffuser_projection()
    top_guide_projection = enclosure.get_top_guide_projection()
    side_guide_projection = enclosure.get_side_guide_projection()
    plunger_strip_projection = enclosure.get_plunger_strip_projection()

    projection_parts.extend(box_projection)
    projection_parts.extend(diffuser_projection)
    projection_parts.extend(top_guide_projection)
    projection_parts.extend(side_guide_projection)
    projection_parts.extend(plunger_strip_projection)
    
    # Write assembly scad file
    prog_assembly = SCAD_Prog()
    prog_assembly.fn = 50
    prog_assembly.add(projection_parts)
    prog_assembly.write('scad/enclosure_projection.scad')
        
    # Write scad file for projections
    scad_projection_files = []

    parts_names = [
                    'top',
                    'bottom',
                    'left_wall',
                    'right_wall',
                    'front',
                    'back',
                    'ref_cube',
                    'diffuser',
                    'guide_top',
                    'guide_side_pos_A',
                    'guide_side_neg_A',
                    'plunger_strip'
                  ]

    n = len(parts_names)
    i = 0
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
