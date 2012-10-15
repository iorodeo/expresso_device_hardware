from __future__ import division
import scipy
from py2scad import *
from subprocess import Popen,PIPE
import math, sys 

class Expresso_Enclosure(Basic_Enclosure):

    def __init__(self,params):
        self.params = params
        # Additions to the Basic Enclosure
        self.add_sensor_cutouts()
        self.add_capillary_holes()
        self.add_guide_tap_holes()
        self.add_maple_cutout()
        self.add_power_cutout()
        self.add_power_holes()
        self.add_maple_holes()
        self.add_led_cable_hole()
        self.add_led_holes()
        self.add_sensor_holes()
        self.add_plunger_holes()
        super(Expresso_Enclosure,self).__init__(self.params)

    def make(self):
        super(Expresso_Enclosure,self).make()
        # Additional parts used in this enclosure
        self.make_guide_plates()
        self.make_capillary()
        self.make_sensor()
        self.make_diffuser()
        self.make_diffuser_standoffs()
        self.make_led_pcb()
        self.make_sensor_pcb()
        self.make_plunger_strip()

    #########################################
    # Additions to the Basic Enclosure
     #########################################
    def add_sensor_cutouts(self):
        """
        Add cutouts for TAOS Linear Array sensors on the bottom plate
        of the enclosure.
        """
        hole_list = [] 
        l,w,h = self.params['sensor_dimensions']
        # Position is centered about the midline so x = 0
        x_pos = 0
        for y_pos in self.get_y_values():
            hole = {
                        'panel'    : 'bottom', 
                        'type'     : 'square', 
                        'location' : (x_pos, y_pos),
                        'size'     : (l, w),
                        }
            hole_list.append(hole)
        self.params['hole_list'].extend(hole_list)

    def add_capillary_holes(self):
        """
        Add holes to the left/right walls through which the bottom guides and the capillary
        tube slide.
        """
        hole_x, hole_y, hole_r = self.params['capillary_hole_size']
        # Physical offset of sensor 'cells' relative to sensor's longitudinal axis
        cap_offset_x =  self.params['capillary_hole_offset']
        x,y,z = self.params['inner_dimensions']
        # Size asymmetry of the bottom_guides used to better position the tube over the sensor
        asym = self.params['guide_plate_asym'][0] # this parameter used to contain all asym. to be tested
        hole_list = [] 
        # Make the holes twice as 'tall' and center it at the bottom edge of the wall
        hole_y = 2*hole_y
        for y_pos in self.get_y_values():
            for panel in ['left','right']:
                pos_x = y_pos - cap_offset_x - .5*asym
                pos_y = -0.5*z 
                hole = {
                        'panel'    : panel,
                        'type'     : 'rounded_square',
                        'location' : (pos_x, pos_y),
                        'size'     : (hole_x, hole_y, hole_r),
                        }
                hole_list.append(hole)
        self.params['hole_list'].extend(hole_list)

    def add_guide_tap_holes(self):
        """
        Add holes to the bottom plate for screwing the guides.
        """
        hole_tuples = self.get_guide_plate_holes(hole_type='tap')
        hole_offset = self.params['capillary_hole_offset']
        hole_list = []
        for y_pos in self.get_y_values():
            for x,y,diam in hole_tuples:
                hole = {
                        'panel'    : 'bottom',
                        'type'     : 'round',
                        'location' : (x,y_pos+y-hole_offset),
                        'size'     : diam,
                        }
                hole_list.append(hole)
        self.params['hole_list'].extend(hole_list)

    def add_maple_cutout(self):
        """
        Add cutout to the bottom panel for the Maple microcontroller.
        """
        led_x, led_y, led_z = self.params['led_pcb_dimensions']
        maple_width = self.params['maple_width']
        maple_length = self.params['maple_length']
        y_pos = -.5*led_y + self.params['maple_y_offset']
        x_pos = -.5*(led_x - maple_length)
        hole_list = [] 
        hole = {
                    'panel'    : 'bottom', 
                    'type'     : 'square', 
                    'location' : (x_pos, y_pos),
                    'size'     : (maple_length, maple_width),
                    }
        hole_list.append(hole)
        self.params['hole_list'].extend(hole_list)

    def add_power_cutout(self):
        """
        Add cutouts to the bottom panel for power connector and plug.
        """
        hole_list = [] 
        power_width = self.params['power_width']
        power_length = self.params['power_length']
        pcb_overhang_x = self.params['sensor_pcb_overhang_x']
        x,y,z = self.params['inner_dimensions']
        # Using the LED PCB dimensions, which are similar to the sensor PCB 
        # dimensions sans the overhang in the 'x' (shorter) dimension
        led_x, led_y, led_z = self.params['led_pcb_dimensions']
        y_pos = -.5*led_y + self.params['power_y_offset']
        x_pos = -.5*(led_x - power_length) - pcb_overhang_x 
        connector_offset = self.params['power_plug_offset']
        thickness = self.params['wall_thickness']
        bottom_x_overhang = self.params['bottom_x_overhang']
        dx = bottom_x_overhang - pcb_overhang_x + thickness + .5*(x-led_x)
        # Power connector cutout
        hole = {
                    'panel'    : 'bottom', 
                    'type'     : 'square', 
                    'location' : (x_pos, y_pos),
                    'size'     : (power_length, power_width),
                    }
        hole_list.append(hole)
        x_pos = -.5*x-thickness-bottom_x_overhang
        y_pos += connector_offset
        # Plug head hole (overhang)
        hole = {
                    'panel'    : 'bottom', 
                    'type'     : 'square', 
                    'location' : (x_pos, y_pos),
                    'size'     : (2.1*dx, self.params['power_head_dia']),
                    }
        hole_list.append(hole)
        self.params['hole_list'].extend(hole_list)

    def add_power_holes(self):
        """
        Add hole to the left wall for the power connector.
        """
        x,y,z = self.params['inner_dimensions']
        power_width = self.params['power_width']
        power_height = self.params['power_height']
        power_length = self.params['power_length']
        led_x, led_y, led_z = self.params['led_pcb_dimensions']

        hole_list = [] 
        pos_x = -.5*led_y + self.params['power_y_offset']
        pos_y = -.5*z
        hole = {
                'panel'    : 'left',
                'type'     : 'square',
                'location' : (pos_x, pos_y),
                'size'     : (power_width, power_height),
                }
        hole_list.append(hole)
        self.params['hole_list'].extend(hole_list)

    def add_maple_holes(self):
        """
        Add holes for connecting a mini-USB cable to the Maple.
        """
        hole_x, hole_y, hole_r = self.params['usb_hole_size']
        x,y,z = self.params['inner_dimensions']

        led_x, led_y, led_z = self.params['led_pcb_dimensions']
        maple_width = self.params['maple_width']
        maple_length = self.params['maple_length']

        y_pos = -.5*led_y + self.params['maple_y_offset']

        z_pos = self.params['usb_pos']
        panel_list= ['left']
        thickness = self.params['wall_thickness']
        hole_list = [] 
        # Not using radius for now
        for panel in panel_list:
            pos_x = y_pos
            pos_y = -0.5*z-thickness+z_pos-.5*hole_y
            hole = {
                    'panel'    : panel,
                    'type'     : 'square',
                    'location' : (pos_x, pos_y),
                    'size'     : (hole_x, hole_y),
                    }
            hole_list.append(hole)
        self.params['hole_list'].extend(hole_list)

    def add_led_holes(self):
        """
        Add holes to the top plate for the stand-offs used by the LED PCB.
        """
        hole_tuples = self.get_led_holes()
        hole_list = []
        for x,y,diam in hole_tuples:
            hole = {
                    'panel'    : 'top',
                    'type'     : 'round',
                    'location' : (x,y),
                    'size'     : diam,
                    }
            hole_list.append(hole)
        self.params['hole_list'].extend(hole_list)

    def add_led_cable_hole(self):
        """
        Add hole to the bottom plate for the 2-pin terminal that connects to
        the LED PCB cable.
        """
        hole_size_x, hole_size_y = self.params['led_cable_hole_size']
        led_x, led_y, led_z = self.params['led_pcb_dimensions']
        y_pos = -.5*led_y + self.params['led_cable_hole_y_offset']
        x_pos = 0
        hole = {
                'panel'     : 'bottom',
                'type'      : 'square',
                'location'  : (x_pos,y_pos),
                'size'      : (hole_size_x,hole_size_y),
                }
        self.params['hole_list'].append(hole)

    def add_sensor_holes(self):
        """
        Add tap holes to the bottom plate for additional tightening of the sensor PCB.
        """
        hole_tuples = self.get_sensor_holes()
        hole_list = []
        for x,y,diam in hole_tuples:
            hole = {
                    'panel'    : 'bottom',
                    'type'     : 'round',
                    'location' : (x,y),
                    'size'     : diam,
                    }
            hole_list.append(hole)
        self.params['hole_list'].extend(hole_list)

    def add_plunger_holes(self):
        """
        Add thru holes to the bottom plate for the plunger.
        """
        # Physical offset of sensor 'cells' relative to sensor's longitudinal axis
        cap_offset_x =  self.params['capillary_hole_offset']
        diam =  self.params['plunger_thru_hole_diam']
        diam_tap = self.params['plunger_strip_tap_hole_diam']
        x,y,z = self.params['inner_dimensions']
        overhang_x = self.params['bottom_x_overhang']
        thickness = self.params['wall_thickness']
        pcb_x, pcb_y, pcb_z = self.params['sensor_pcb_dimensions']
        pcb_overhang_x = self.params['sensor_pcb_overhang_x']
        # Size asymmetry of the bottom_guides used to better position the tube over the sensor
        asym = self.params['guide_plate_asym'][0] # this parameter used to contain all asym. to be tested
        hole_list = [] 
        dx = 0.5*x + thickness + overhang_x - (.5*pcb_x + pcb_overhang_x)
        pos_x = 0.5*x + thickness + overhang_x - .5*dx
        cnt = 0
        for y_pos in self.get_y_values():
            pos_y = y_pos - cap_offset_x - .5*asym
            hole = {
                    'panel'    : 'bottom',
                    'type'     : 'round',
                    'location' : (pos_x,pos_y),
                    'size'     : diam,
                    }
            hole_list.append(hole)
            cnt+=1
            if cnt == 1:
                dy = -.25*INCH2MM
            elif (cnt == 2) or (cnt == 3):
                dy = .5*INCH2MM
            elif cnt == 5:
                dy = +.25*INCH2MM
            else:
                continue
            hole = {
                    'panel'    : 'bottom',
                    'type'     : 'round',
                    'location' : (pos_x,pos_y-dy),
                    'size'     : diam_tap,
                    }
            hole_list.append(hole)
        self.params['hole_list'].extend(hole_list)
    #########################################
    # Auxiliary functions
    #########################################
    def get_y_values(self):
        """
        Returns the y_value of the center of ALL the sensors
        """
        n = self.params['number_of_sensors']
        spacing = self.params['sensor_spacing']

        sensor_ypos_offset = self.params['sensor_ypos_offset']
        pcb_x, pcb_y, pcb_z = self.params['led_pcb_dimensions']
        l,w,h = self.params['sensor_dimensions']
        pos_0 = .5*pcb_y - sensor_ypos_offset - .5*w

        pos_lst = [] 
        for val in range(n):
            pos_lst.append(pos_0-val*spacing)
        return pos_lst

    def get_led_holes(self, hole_type='through'):
        """ 
        Returns the holes for the stand-offs of the LED PCB
        """
        led_x, led_y, led_z = self.params['led_pcb_dimensions']
        diff_x, diff_y, diff_z = self.params['diffuser_dimensions']
        hole_offset_x = self.params['led_pcb_hole_offset_x']
        hole_offset_y = self.params['led_pcb_hole_offset_y']

        hole_list = []

        for i in (-1,1):
            x_pos = i*(0.5*led_x - hole_offset_x)
            y_pos = .5*led_y - hole_offset_y
            diam = self.params['led_pcb_tap_hole_diam']
            hole = (x_pos, y_pos, diam)
            hole_list.append(hole)

        for i in (-1,1):
            x_pos = i*(0.5*led_x - hole_offset_x)
            y_pos = -.5*led_y + (led_y-diff_y) + hole_offset_y
            diam = self.params['led_pcb_tap_hole_diam']
            hole = (x_pos, y_pos, diam)
            hole_list.append(hole)

        for i in (-1,1):
            x_pos = i*(0.5*led_x - hole_offset_x)
            y_pos = -0.5*led_y + hole_offset_y
            diam = self.params['led_pcb_tap_hole_diam']
            hole = (x_pos, y_pos, diam)
            hole_list.append(hole)
        return hole_list

    def get_sensor_holes(self, hole_type='through'):
        """ 
        Returns the holes for the stand-offs of the LED PCB
        """
        sensor_x, sensor_y, sensor_z = self.params['sensor_pcb_dimensions']
        hole_offset_y = self.params['sensor_pcb_hole_offset_y']
        hole_offset_x = self.params['sensor_pcb_hole_offset_x']

        hole_list = []

        for i in (-1,1):
            x_pos = i*(0.5*sensor_x - hole_offset_x)
            y_pos = .5*sensor_y - hole_offset_y
            diam = self.params['led_pcb_tap_hole_diam']
            hole = (x_pos, y_pos, diam)
            hole_list.append(hole)

        for i in (-1,1):
            x_pos = i*(0.5*sensor_x - hole_offset_x)
            y_pos = -0.5*sensor_y + hole_offset_y
            diam = self.params['led_pcb_tap_hole_diam']
            hole = (x_pos, y_pos, diam)
            hole_list.append(hole)
        
        y_pos_list = self.params['sensor_pcb_hole_pos_y']
        overhang_x = self.params['sensor_pcb_overhang_x']
        for y_pos in y_pos_list:
            y_pos-= 0.5*sensor_y
            for i in (-1,1):
                x_pos = i*(0.5*sensor_x + overhang_x - hole_offset_x)
                diam = self.params['led_pcb_tap_hole_diam']
                hole = (x_pos, y_pos, diam)
                hole_list.append(hole)
        return hole_list

    def get_guide_plate_holes(self,hole_type='through'):
        """
        Auxiliary function that returns screw holes for placement of the guide plates.
        Useful for alignment of plates on the bottom face of the enclosure.
        """
        guide_x, guide_y, guide_z = self.params['guide_plate_dimensions']
        hole_offset = self.params['guide_hole_offset']
        if hole_type == 'through':
            hole_diam = self.params['guide_thru_hole_diam']
        else:
            hole_diam = self.params['guide_tap_hole_diam']
        hole_list = []
        top_x, top_y, top_z = self.get_guide_plate_top_dim()
        for i in (-1,1):
            for j in (-1,1):
                x_pos = i*(0.5*top_x - hole_offset)
                y_pos = j*(0.5*top_y - hole_offset)
                hole = (x_pos, y_pos, hole_diam)
                hole_list.append(hole)
        return hole_list

    def get_guide_plate_top_dim(self):
        """ 
        Returns the dimension of the top guide plate, we can change here its width
        so that the grip is tighter on the capillary tube.
        """
        guide_x, guide_y, guide_z = self.params['guide_plate_dimensions']
        top_x = guide_x
        top_y = 2*guide_y + .9*self.params['capillary_diam']
        top_z = guide_z
        return top_x, top_y, top_z

    #########################################
    # Additional parts used in this enclosure
    #########################################
    def make_guide_plates(self):
        guide_x, guide_y, guide_z = self.params['guide_plate_dimensions']
        hole_diam = self.params['guide_thru_hole_diam']
        # Distane from the edges of the guide to the center of the screw hole
        hole_offset = self.params['guide_hole_offset']
        guide_plate_asym = self.params['guide_plate_asym']
        # A list of cutout widths to be tried on the guide plates to allow more light 
        # to hit the sensor
        guide_plate_cutout_y = self.params['guide_plate_cutout_y']
        cut_x = self.params['guide_plate_cutout_x']

        # Create pos and neg guide plates
        hole_list_pos = []
        hole_list_neg = []
        self.guide_plate_pos = []
        self.guide_plate_neg = []
        # Create hole lists to be added to the pos and neg guide plates,
        # symmetric about the midline so can use (-1,1).
        for i in (-1,1):
            x_pos = i*(0.5*guide_x - hole_offset) 
            y_pos = 0.5*guide_y - hole_offset 
            hole_pos = (x_pos, y_pos, hole_diam)
            hole_neg = (x_pos, -y_pos, hole_diam)
            hole_list_pos.append(hole_pos)
            hole_list_neg.append(hole_neg)

        # Generate a pos/neg guideplates for each combination of asym and cutout
        # we want to try
        for cut_y in guide_plate_cutout_y:
            for asym in guide_plate_asym:
                # Using a cube to use difference for making the tabs on each end of the pos/neg
                # guide plates.
                diff_cube = Cube(size=(cut_x,4*cut_y,1))
                guide_plate_pos = plate_w_holes(guide_x, guide_y+asym, guide_z, holes=hole_list_pos)
                ext_plate_pos = plate_w_holes(guide_x+2*3+2*3, 4, guide_z, holes=[]);
                ext_plate_pos = Translate(ext_plate_pos,v=(0,-.5*(guide_y + asym)+.5*4,0))
                diff_cube = Translate(diff_cube,v=(0,-.5*(guide_y+asym),0))

                guide_plate_pos = Union([ext_plate_pos]+[guide_plate_pos])
                guide_plate_pos = Difference([guide_plate_pos]+[diff_cube])    

                guide_plate_neg = plate_w_holes(guide_x, guide_y-asym, guide_z, holes=hole_list_neg)
                ext_plate_neg = plate_w_holes(guide_x+2*3+2*3, 4, guide_z, holes=[]);
                ext_plate_neg = Translate(ext_plate_neg,v=(0,.5*(guide_y - asym)-.5*4,0))
                diff_cube = Translate(diff_cube,v=(0,guide_y,0))

                guide_plate_neg = Union([ext_plate_neg]+[guide_plate_neg])
                guide_plate_neg = Difference([guide_plate_neg]+[diff_cube])    
                
                self.guide_plate_pos.append(guide_plate_pos)
                self.guide_plate_neg.append(guide_plate_neg)

        # Create top guide plate
        top_x, top_y, top_z = self.get_guide_plate_top_dim()
        hole_list_top = self.get_guide_plate_holes(hole_type='through')
        self.guide_plate_top = plate_w_holes(top_x,top_y,top_z,holes=hole_list_top)

    def make_capillary(self):
        diam = self.params['capillary_diam']
        length = self.params['capillary_length']
        r = 0.5*diam
        capillary = Cylinder(h=length,r1=r,r2=r)
        capillary = Rotate(capillary, a=90, v=(0,1,0))
        self.capillary = capillary

    def make_sensor(self):
        sensor_x, sensor_y, sensor_z = self.params['sensor_dimensions']
        hole_offset = self.params['sensor_hole_offset']
        hole_diam = self.params['sensor_mount_hole_diam']
        hole_pos = self.params['sensor_mount_hole_pos']

        # Create hole list 
        hole_list = []
        for i in (-1,1):
            x_pos = i*0.5*hole_pos
            y_pos = hole_offset
            hole = (x_pos, y_pos,hole_diam)
            hole_list.append(hole)

        # Create sensor
        sensor = plate_w_holes(sensor_x, sensor_y, sensor_z, hole_list)
        self.sensor = Translate(sensor,v=(0,0,0))

    def make_diffuser(self):
        diff_x, diff_y, diff_z = self.params['diffuser_dimensions']
        diam = self.params['diffuser_thru_hole_diam']
        hole_offset_x = self.params['led_pcb_hole_offset_x']
        hole_offset_y = self.params['led_pcb_hole_offset_y']
        hole_list = []

        for i in (-1,1):
            x_pos = i*(0.5*diff_x - hole_offset_x)
            y_pos = 0.5*diff_y - hole_offset_y
            hole = (x_pos, y_pos, diam)
            hole_list.append(hole)

        for i in (-1,1):  
            x_pos = i*(0.5*diff_x - hole_offset_x)
            y_pos = -0.5*diff_y + hole_offset_y
            hole = (x_pos, y_pos, diam)
            hole_list.append(hole)

        self.diffuser = plate_w_holes(diff_x, diff_y, diff_z, holes=hole_list)

    def make_led_pcb(self):
        led_x, led_y, led_z = self.params['led_pcb_dimensions']
        hole_list = self.get_led_holes(hole_type='through')
        self.led_pcb = plate_w_holes(led_x, led_y, led_z, holes=hole_list)

    def make_sensor_pcb(self):
        sensor_x, sensor_y, sensor_z = self.params['sensor_pcb_dimensions']
        overhang_x = self.params['sensor_pcb_overhang_x']
        hole_list = self.get_sensor_holes(hole_type='through')
        self.sensor_pcb = plate_w_holes(sensor_x+2*overhang_x, sensor_y, sensor_z, holes=hole_list)

    def make_diffuser_standoffs(self):
        height = self.params['diffuser_standoff_height']
        diam = self.params['diffuser_standoff_diam']
        radius = 0.5*diam
        self.diffuser_standoff_pos = Cylinder(h=height,r1=radius,r2=radius)
        self.diffuser_standoff_neg = Cylinder(h=height,r1=radius,r2=radius)

    def make_plunger_strip(self):
        strip_x, strip_y, strip_z = self.params['plunger_strip_dimensions']
        diam = self.params['plunger_strip_etched_hole_diam']
        hole_list = []
        hole_x = 0
         
        # Mounting holes
        diam = self.params['plunger_strip_thru_hole_diam']
        for i in [1,8,12,19]:
            hole_y = -.5*strip_y+i*.25*INCH2MM
            hole_list.append((hole_x,hole_y,diam))
        self.plunger_strip = plate_w_holes(strip_x, strip_y, strip_z, holes=hole_list)

        # Plunger holes
        x,y,z = self.params['inner_dimensions']
        wall_thickness = self.params['wall_thickness']
        bottom_x_overhang = self.params['bottom_x_overhang']
        cap_offset_x = self.params['capillary_hole_offset']
        overhang_x = self.params['bottom_x_overhang']
        thickness = self.params['wall_thickness']
        pcb_x, pcb_y, pcb_z = self.params['sensor_pcb_dimensions']
        pcb_overhang_x = self.params['sensor_pcb_overhang_x']
        asym = self.params['guide_plate_asym'][0]
        rad = .5*self.params['plunger_strip_etched_hole_diam']

        pos_x_strip = 0.
        dx = 0.5*x + thickness + overhang_x - (.5*pcb_x + pcb_overhang_x)
        pos_x_bot = 0.5*x + thickness + overhang_x - .5*dx
        height = strip_z
        y_0 = self.get_y_values()[2]
        for y_pos in self.get_y_values():
            pos_y = y_pos - y_0
            cyl = Cylinder(r1=rad,r2=rad,h=height)
            strip_cyl = Translate(cyl,v=(pos_x_strip,pos_y,.5*strip_z))
            self.plunger_strip = Difference([self.plunger_strip,strip_cyl])

            y_shift = y_pos - cap_offset_x - .5*asym
            bot_cyl = Translate(cyl,v=(pos_x_bot,y_shift,-.5*wall_thickness))
            self.bottom = Difference([self.bottom,bot_cyl])

    #########################################
    # Enclosure Assembly
    #########################################
    def get_assembly(self,**kwargs):
        """
        Get enclosure assembly. Shifts all the parts into position, and can explode the 
        generated assembly.
        """
        try:
            show_sensor = kwargs['show_sensor']
        except KeyError:
            show_sensor = True
        try:
            show_capillary = kwargs['show_capillary']
        except KeyError:
            show_capillary = True
        try:
            show_guide_bottom = kwargs['show_guide_bottom']
        except KeyError:
            show_guide_bottom = True
        try:
            show_guide_top = kwargs['show_guide_top']
        except KeyError:
            show_guide_top = True
        try:
            show_led_pcb = kwargs['show_led_pcb']
        except KeyError:
            show_led_pcb = True
        try:
            show_sensor_pcb = kwargs['show_sensor_pcb']
        except KeyError:
            show_sensor_pcb = True
        try:
            show_plunger_strip = kwargs['show_plunger_strip']
        except KeyError:
            show_plunger_srtip = True
        try:
            show_diffuser = kwargs['show_diffuser']
        except KeyError:
            show_diffuser = True
        try:
            show_diffuser_standoffs = kwargs['show_diffuser_standoffs']
        except KeyError:
            show_diffuser_standoffs = True
        try:
            explode = kwargs['explode']
        except KeyError:
            explode = (0,0,0)

        # Assembly parameters
        explode_x, explode_y, explode_z = explode
        x,y,z = self.params['inner_dimensions']
        wall_thickness = self.params['wall_thickness']
        guide_x, guide_y, guide_z = self.params['guide_plate_dimensions']
        cap_offset_x = self.params['capillary_hole_offset']
        y_values = self.get_y_values()
        cap_hole_diam = self.params['capillary_diam']
        asym = self.params['guide_plate_asym'][0]

        # Get all the Basic Enclosure parts and add them to the assembly parts list.
        parts_list = super(Expresso_Enclosure,self).get_assembly(**kwargs)

        ##
        # Add bottom guide plates to the assembly parts list.
        ##
        for y_pos in y_values:
            # Shift positive guide plate
            y_shift = y_pos + .5*guide_y - cap_offset_x + 0.5*self.params['capillary_diam']
            z_shift = -0.5*z + 0.5*guide_z - .5*explode_z
            guide_plate_pos = Translate(self.guide_plate_pos,v=[0,y_shift,z_shift])
            # Shift negative guide plate
            y_shift = y_pos - .5*guide_y - cap_offset_x - .5*self.params['capillary_diam'] 
            guide_plate_neg = Translate(self.guide_plate_neg,v=[0,y_shift,z_shift])
            # Shift top guide plate
            y_shift = y_pos - cap_offset_x
            z_shift = -0.5*z + 1.5*guide_z - .5*explode_z
            guide_plate_top = Translate(self.guide_plate_top,v=[0,y_shift,z_shift])
            if show_guide_bottom:
               parts_list.extend([guide_plate_pos,guide_plate_neg])
            if show_guide_top:
               parts_list.extend([guide_plate_top])

        ##
        # Add capillary tube top the assembly parts list.
        ##
        z_shift = -0.5*z + 0.5*cap_hole_diam - explode_z
        for y_pos in y_values:
            capillary = self.capillary
            y_shift = y_pos - cap_offset_x - .5*asym
            capillary = Translate(self.capillary,v=(0,y_shift,z_shift))
            if show_capillary:
                parts_list.append(capillary)

        ##
        # Add sensor to the assembly parts list.
        ##
        sensor_x, sensor_y, sensor_z = self.params['sensor_dimensions']
        z_shift = -0.5*z-0.5*sensor_z - explode_z
        for y_pos in y_values:
            sensor = self.sensor
            sensor = Translate(sensor,v=(0,y_pos,z_shift))
            sensor = Color(sensor,rgba=(0.5,0.5,0.5))
            if show_sensor:
                parts_list.append(sensor)

        ##
        # Add diffuser to the assembly parts list.
        ##
        bottom_x_overhang = self.params['bottom_x_overhang']
        led_pcb_x, led_pcb_y, led_pcb_z = self.params['led_pcb_dimensions']
        diff_x, diff_y, diff_z = self.params['diffuser_dimensions']
        hole_offset_y = self.params['led_pcb_hole_offset_y']
        diffuser_standoff_height = self.params['diffuser_standoff_height']
        z_shift = 0.5*z - led_pcb_z - 0.5*diff_z - diffuser_standoff_height
        y_shift = .5*(led_pcb_y-diff_y)
        diffuser = Translate(self.diffuser,v=(0,y_shift,z_shift))
        if show_diffuser:
            parts_list.append(diffuser)

        ##
        # Add diffuser standoffs to the assembly parts list.
        ##
        led_hole_tuples = self.get_led_holes()
        z_shift = 0.5*z - led_pcb_z - 0.5*self.params['diffuser_standoff_height']
        for x_shift,y_shift, dummy in led_hole_tuples:
            if x_shift < 0:
                standoff = self.diffuser_standoff_neg
            else:
                standoff = self.diffuser_standoff_pos
            standoff = Translate(standoff,v=(x_shift,y_shift,z_shift))
            if show_diffuser_standoffs:
                parts_list.append(standoff)

        ##
        # Add led pcb to the assembly parts list.
        ##
        z_shift = 0.5*z - 0.5*led_pcb_z
        led_pcb = Translate(self.led_pcb,v=(0,0,z_shift))
        if show_led_pcb:
            parts_list.append(led_pcb)

        ##
        # Add sensor pcb to the assembly parts list.
        ##
        sensor_pcb_x, sensor_pcb_y, sensor_pcb_z = self.params['sensor_pcb_dimensions']
        z_shift = -0.5*z-sensor_z-explode_z-.5*sensor_pcb_z-wall_thickness
        sensor_pcb = Translate(self.sensor_pcb,v=(0,0,z_shift))
        if show_sensor_pcb:
            parts_list.append(sensor_pcb)

        ##
        # Add plunger strip to the assembly parts list.
        ##
        cap_offset_x =  self.params['capillary_hole_offset']
        # Size asymmetry of the bottom_guides used to better position the tube over the sensor
        asym = self.params['guide_plate_asym'][0] # this parameter used to contain all asym. to be tested
        y_shift = y_values[2] - cap_offset_x - .5*asym 
        strip_x, strip_y, strip_z = self.params['plunger_strip_dimensions']
        overhang_x = self.params['bottom_x_overhang']
        sensor_pcb_overhang_x = self.params['sensor_pcb_overhang_x']
        dx = 0.5*x + wall_thickness + overhang_x - (.5*sensor_pcb_x + sensor_pcb_overhang_x)
        x_shift = 0.5*x + wall_thickness + overhang_x - .5*dx
        z_shift = -0.5*z-sensor_z-explode_z-.5*strip_z-wall_thickness
        plunger_strip = Translate(self.plunger_strip,v=(x_shift,y_shift,z_shift))
        if show_plunger_strip:
            parts_list.append(plunger_strip)

        return parts_list

    ##########################################
    ## Enclosure Projections
    ##########################################

    def get_box_projection(self,show_ref_cube=True, spacing_factor=4):
        """
        Get 2D projected layout of the enclosure 'box' parts for laser cutting.
        """
        parts_list = super(Expresso_Enclosure,self).get_projection(show_ref_cube,spacing_factor)
        return parts_list

    def get_side_guide_projection(self,show_ref_cube=False,spacing_factor=2):
        """
        Get 2D projected layout of the two side guide plates for laser cutting.
        """
        parts_list = []
        x,y,z = self.params['inner_dimensions']
        guide_x, guide_y, guide_z = self.params['guide_plate_dimensions']
        thickness = self.params['wall_thickness']

        # Add the side guide plates
        i=0
        row_break = len(self.params['guide_plate_cutout_y'])
        for guide_plate_pos,guide_plate_neg in zip(self.guide_plate_pos,self.guide_plate_neg):
            x_shift = (math.floor(i/row_break)+1)*.5*guide_x + .5*x + self.params['bottom_x_overhang'] + (math.floor(i/row_break)+1)*thickness + \
                      (math.floor(i/row_break)+1)*2*15 + z
            y_shift = ((i%row_break)+1)*0.5*guide_y + 2*((i%row_break)+1)*spacing_factor*thickness

            i+=1

            guide_plate_pos = Translate(guide_plate_pos,v=(-x_shift,y_shift,0))
            guide_plate_pos = Projection(guide_plate_pos)
            parts_list.append(guide_plate_pos)

            guide_plate_neg = Translate(guide_plate_neg,v=(-x_shift,-y_shift,0))
            guide_plate_neg = Projection(guide_plate_neg)
            parts_list.append(guide_plate_neg)
        return parts_list


    def get_top_guide_projection(self,show_ref_cube=False,spacing_factor=2):
        """
        Get 2D projected layout of the top guide plate for laser cutting.
        """
        parts_list = []
        top_x, top_y, top_z = self.get_guide_plate_top_dim()
        x,y,z = self.params['inner_dimensions']
        guide_x, guide_y, guide_z = self.params['guide_plate_dimensions']
        thickness = self.params['wall_thickness']

        # Add top guide plate
        x_shift = .5*guide_x + .5*x + self.params['bottom_x_overhang'] + thickness + \
                  3*15 + z + top_x

        guide_plate_top = Translate(self.guide_plate_top,v=(-x_shift,0,0))
        guide_plate_top = Projection(guide_plate_top)
        parts_list.append(guide_plate_top)

        # Add reference cube
        ref_cube = Cube(size=(INCH2MM, INCH2MM, INCH2MM))   

        ref_cube = Translate(ref_cube,v=(x_shift,0,0))
        ref_cube = Projection(ref_cube)
        if show_ref_cube:
            parts_list.append(ref_cube)

        return parts_list
        

    def get_diffuser_projection(self,show_ref_cube=False,spacing_factor=2):
        """
        Get 2D projected layout of the diffuser for laser cutting.
        """
        parts_list = []
        diff_x, diff_y, diff_z = self.params['diffuser_dimensions']
        x,y,z = self.params['inner_dimensions']
        
        thickness = self.params['wall_thickness']
        
        # Add diffuser
        x_shift = .5*diff_x + .5*x + self.params['bottom_x_overhang'] + thickness + \
                  2*15 + z
        diffuser = Translate(self.diffuser,v=(x_shift,0,0))
        parts_list.append(Projection(diffuser))

        # Add reference cube
        ref_cube = Cube(size=(INCH2MM, INCH2MM, INCH2MM))   
        x_shift = 0.5*diff_x + 0.5*INCH2MM + spacing_factor*thickness
        ref_cube = Translate(ref_cube,v=(-x_shift,0,0))
        ref_cube = Projection(ref_cube)
        if show_ref_cube:
            parts_list.append(ref_cube)
        return parts_list

    def get_plunger_strip_projection(self,show_ref_cube=False,spacing_factor=2):
        """
        Get 2D projected layout of the plunger strip for laser cutting.
        """
        parts_list = []
        strip_x, strip_y, strip_z = self.params['plunger_strip_dimensions']
        diff_x, diff_y, diff_z = self.params['diffuser_dimensions']
        x,y,z = self.params['inner_dimensions']
        
        thickness = self.params['wall_thickness']
        
        # Add diffuser
        x_shift = diff_x + .5*x + self.params['bottom_x_overhang'] + thickness + \
                  3*15 + z + .5*strip_x
        strip = Translate(self.plunger_strip,v=(x_shift,0,0))
        parts_list.append(Projection(strip))

        # Add reference cube
        ref_cube = Cube(size=(INCH2MM, INCH2MM, INCH2MM))   
        x_shift = 0.5*diff_x + 0.5*INCH2MM + spacing_factor*thickness
        ref_cube = Translate(ref_cube,v=(-x_shift,0,0))
        ref_cube = Projection(ref_cube)
        if show_ref_cube:
            parts_list.append(ref_cube)
        return parts_list
