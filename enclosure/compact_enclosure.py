from __future__ import division
import scipy
from py2scad import *
from subprocess import Popen,PIPE
import math, sys 

def generate_stl(part,filename):
    filename = 'stl/'+filename
    prog_assembly = SCAD_Prog()
    prog_assembly.fn = 100 # Raised to 100 or otherwise STL won't show
    for p in part:
        prog_assembly.add(p)
    prog_assembly.write('temp.scad')            
    Popen('openscad -s '+filename+'.stl'+' temp.scad',shell=True,stdout=PIPE).wait()
    Popen('rm temp.scad',shell=True,stdout=PIPE).wait()
    part_stl = Import_STL(filename+'.stl').cmd_str()


class Compact_Enclosure(Basic_Enclosure):

    def __init__(self,params):
        self.params = params
        self.add_sensor_cutout()
        self.add_capillary_holes()
        self.add_guide_tap_holes()
        self.add_maple_cutout()
        self.add_power_cutout()
        self.add_maple_holes()
        self.add_power_holes()
        self.add_led_holes()
        self.add_sensor_mounting_holes()
        self.add_led_cable_hole()
        super(Compact_Enclosure,self).__init__(self.params)

    def make(self):
        super(Compact_Enclosure,self).make()
        self.make_sensor()
        self.make_capillary()
        self.make_guide_plates()
        self.make_led_pcb()
        self.make_diffuser()
        self.make_diffuser_standoffs()
        #self.make_vial_holder_tap_holes()
        #self.make_vial_holder()
        #self.make_vial_holder_spacer()
        #self.make_vial()
        self.make_capillary_clamp_thru_holes()
        self.make_capillary_clamp()

    def get_assembly(self,**kwargs):
        """
        Get enclosure assembly
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
            show_vial = kwargs['show_vial']
        except KeyError:
            show_vial = True
        try:
            show_guide_plates = kwargs['show_guide_plates']
        except KeyError:
            show_guide_plates = True
        try:
            show_guide_top = kwargs['show_guide_top']
        except KeyError:
            show_guide_top = True
        try:
            show_led_pcb = kwargs['show_led_pcb']
        except KeyError:
            show_led_pcb = True
        try:
            show_diffuser = kwargs['show_diffuser']
        except KeyError:
            show_diffuser = True
        try:
            show_vial_holder = kwargs['show_vial_holder']
        except KeyError:
            show_vial_holder = True
        try:
            show_diffuser_standoffs = kwargs['show_diffuser_standoffs']
        except KeyError:
            show_diffuser_standoffs = True
        try:
            explode = kwargs['explode']
        except KeyError:
            explode = (0,0,0)
        try:
            gen_stl = kwargs['gen_stl']
        except KeyError:
            gen_stl = kwargs['false']
        try:
            show_clamp = kwargs['show_clamp']
        except KeyError:
            show_clamp = True

        explode_x, explode_y, explode_z = explode
        
        stl_list = []

        parts_list = super(Compact_Enclosure,self).get_assembly(**kwargs)
        x,y,z = self.params['inner_dimensions']
        wall_thickness = self.params['wall_thickness']

        # Add sensor
        sensor_x, sensor_y, sensor_z = self.params['sensor_dimensions']
        z_shift = -0.5*z-0.5*sensor_z - explode_z
        for y_pos in self.get_y_values():
            sensor = self.sensor
            sensor = Translate(sensor,v=(0,y_pos,z_shift))
            sensor = Color(sensor,rgba=(0.5,0.5,0.5))
            if show_sensor:
                parts_list.append(sensor)

        # Add capillary
        cap_offset_x = self.params['capillary_hole_offset']
        cap_hole_diam = self.params['capillary_diam']
        z_shift = -0.5*z + 0.5*cap_hole_diam  - explode_z
        for y_pos in self.get_y_values():
            capillary = self.capillary
            capillary = Translate(self.capillary,v=(0,y_pos-cap_offset_x,z_shift))
            if show_capillary:
                parts_list.append(capillary)
        
        # Add guide plate
        y_values = self.get_y_values()
        guide_x, guide_y, guide_z = self.params['guide_plate_dimensions']
        for y_pos in y_values:
            #y_shift = 0.5*guide_y + 0.5*self.params['capillary_diam'] + cap_offset_x 
            y_shift = y_pos + .5*guide_y - cap_offset_x + 0.5*self.params['capillary_diam']
            z_shift = -0.5*z + 0.5*guide_z
            guide_plate_pos = Translate(self.guide_plate_pos,v=[0,y_shift,z_shift])

            #y_shift = -0.5*guide_y - 0.5*self.params['capillary_diam'] + cap_offset_x
            y_shift = y_pos - .5*guide_y - .5*self.params['capillary_diam'] - cap_offset_x
            guide_plate_neg = Translate(self.guide_plate_neg,v=[0,y_shift,z_shift])

            #y_shift = cap_offset_x
            y_shift = y_pos - cap_offset_x
            z_shift = -0.5*z + 1.5*guide_z
            guide_plate_top = Translate(self.guide_plate_top,v=[0,y_shift,z_shift])
            if show_guide_plates:
               parts_list.extend([guide_plate_pos,guide_plate_neg])
            if show_guide_top:
               parts_list.extend([guide_plate_top])


        # Add led pcb
        pcb_x, pcb_y, pcb_z = self.params['led_pcb_dimensions']
        z_shift = 0.5*z - 0.5*pcb_z
        led_pcb = Translate(self.led_pcb,v=(0,0,z_shift))
        if show_led_pcb:
            parts_list.append(led_pcb)

        # Add diffuser
        bottom_x_overhang = self.params['bottom_x_overhang']
        diff_x, diff_y, diff_z = self.params['diffuser_dimensions']
        hole_offset_y = self.params['led_pcb_hole_offset_y']
        diff_y+=2*hole_offset_y
        diffuser_standoff_height = self.params['diffuser_standoff_height']
        z_shift = 0.5*z - pcb_z - 0.5*diff_z -  diffuser_standoff_height
        y_shift = self.params['diffuser_offset']
        diffuser = Translate(self.diffuser,v=(0,y_shift,z_shift))
        if show_diffuser:
            parts_list.append(diffuser)

        # Add diffuser standoffs
        led_hole_tuples = self.get_led_holes()
        z_shift = 0.5*z - pcb_z- 0.5*self.params['diffuser_standoff_height']
        for x_shift,y_shift, dummy in led_hole_tuples:
            if x_shift < 0:
                standoff = self.diffuser_standoff_neg
            else:
                standoff = self.diffuser_standoff_pos
            standoff = Translate(standoff,v=(x_shift,y_shift,z_shift))
            if show_diffuser_standoffs:
                parts_list.append(standoff)

        # Add capillary clamp
        clamp_x, clamp_y, clamp_z = self.clamp_size
        x_shift = -0.5*self.bottom_x + 0.5*bottom_x_overhang
        z_shift = -0.5*z + 0.5*wall_thickness + cap_hole_diam
        for y_pos in self.get_y_values():
            capillary_clamp = Translate(self.capillary_clamp,v=(x_shift,y_pos,z_shift))
            if show_clamp:
                parts_list.append(capillary_clamp)

        ## Add vials
        #holder_x, holder_y, holder_z = self.params['vial_holder_dimensions']
        #vial_wall_width,vial_wall_length = self.params['vial_holder_wall_size']
        #vial_hole_diam = self.params['vial_diam']
        ##vial_offset_x = self.params['capillary_clamp_hole_offset']
        #vial_offset_x = -.5*bottom_x_overhang
        #z_shift = -0.5*z + 0.5*cap_hole_diam - explode_z
        #x_shift = .5*x+bottom_x_overhang+wall_thickness+.4*self.params['vial_length']\
                  #+0.5*holder_x#-self.params['vial_holder_offset_x']
        #for y_pos in self.get_y_values():
            #vial = self.vial
            #vial = Translate(self.vial,v=(x_shift,y_pos-cap_offset_x,z_shift))
            #if show_vial:
                #parts_list.append(vial)
        
        ## Add vial holder
        #z_shift = -0.5*z  - explode_z - .5*holder_z - self.params['wall_thickness'] \
                  #- (vial_wall_length - vial_hole_diam) - 0.5*cap_hole_diam
        #y_shift = .5*(pcb_y - holder_y)
        #x_shift = .5*x+bottom_x_overhang+.5*holder_x+wall_thickness \
                  #- ( .5*holder_x + (-.2*holder_x-.5*self.params['vial_holder_rail_length']) ) \
                  #+ vial_offset_x - .5*self.params['capillary_clamp_thru_hole_diam']
        
        #vial_holder = Translate(self.vial_holder,v=(x_shift,y_shift,z_shift))
        #if show_vial_holder:
            #parts_list.append(vial_holder)

        ## Add vial holder spacers
        #bottom_x_overhang = self.params['bottom_x_overhang']
        #hole_diam = self.params['capillary_clamp_tap_hole_diam']
        #sensor_spacing = self.params['sensor_spacing']
        #rails_y_offset = self.params['rails_y_offset']

        #pos_x = 0.5*self.bottom_x - .5*bottom_x_overhang
        #y_shift = .5*(pcb_y - holder_y)
        #pos_y = (.5*holder_y - rails_y_offset + y_shift,-.5*holder_y+rails_y_offset + y_shift)
        #z_shift = -0.5*z - .5*self.params['vial_holder_spacer_length'] \
                  #-wall_thickness
        #for y_pos in pos_y:
            #spacer = self.vial_holder_spacer
            #spacer = Translate(spacer,v=(pos_x,y_pos,z_shift))
            #if show_vial_holder:
                #parts_list.append(spacer)

        if gen_stl:
            cnt = 0
            for part in parts_list:
               cnt+=1
               filename = str(cnt)
               generate_stl([part],filename)

        return parts_list

    def get_box_projection(self,show_ref_cube=True, spacing_factor=4):
        """
        Get 2D projected layout of parts for laser cutting.
        """
        parts_list = super(Compact_Enclosure,self).get_projection(show_ref_cube,spacing_factor)

        # Add capillary clamp
        thickness = self.params['wall_thickness']
        clamp_x, clamp_y, clamp_z = self.clamp_size
        x_shift = 0.5*self.bottom_x + 0.5*clamp_x + spacing_factor*thickness
        y_shift = 0.5*self.bottom_y + 0.5*clamp_y + spacing_factor*thickness
        clamp = Translate(self.capillary_clamp,v=(x_shift,y_shift,0))
        parts_list.append(Projection(clamp))
        return parts_list

    def get_vial_holder_projection(self,show_ref_cube=True, spacing_factor=4):
        """
        Get 2D projected layout of parts for laser cutting.
        """
        parts_list = []
        parts_list = Vial_Holder.get_projection(Vial_Holder(self.params),spacing_factor=4)
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

        # Add reference cube
        #ref_cube = Cube(size=(INCH2MM, INCH2MM, INCH2MM))   
        #x_shift = 0.5*guide_x + 0.5*INCH2MM + spacing_factor*thickness
        #ref_cube = Translate(ref_cube,v=(x_shift,0,0))
        #ref_cube = Projection(ref_cube)
        #if show_ref_cube:
            #parts_list.append(ref_cube)

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


    def add_capillary_holes(self):
        """
        Add holes for capillary positioning
        """
        hole_x, hole_y, hole_r = self.params['capillary_hole_size']
        hole_y = 2*hole_y
        capillary_diam = self.params['capillary_diam']
        cap_offset_x =  self.params['capillary_hole_offset']
        x,y,z = self.params['inner_dimensions']
        asym = self.params['guide_plate_asym'][0]

        panel_list= ('left', 'right')
        hole_list = [] 
        for y_pos in self.get_y_values():
            for panel in panel_list:
                pos_x = y_pos-cap_offset_x - asym #-.5*capillary_diam (offset accounts for this)!
                pos_y = -0.5*z 
                hole = {
                        'panel'    : panel,
                        'type'     : 'rounded_square',
                        'location' : (pos_x, pos_y),
                        'size'     : (hole_x, hole_y, hole_r),
                        }
                hole_list.append(hole)
        self.params['hole_list'].extend(hole_list)

    def add_maple_holes(self):
        """
        Add holes for connecting a mini-USB cable to the maple
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

    def add_power_holes(self):
        """
        Add holes for power connector
        """
        x,y,z = self.params['inner_dimensions']
        #x_pos,y_pos = self.params['power_pos']
        x_offset = self.params['inner_dimension_offset']
        power_width = self.params['power_width']
        connector_width = self.params['connector_width']
        power_height = self.params['power_height']
        power_length = self.params['power_length']
        led_x, led_y, led_z = self.params['led_pcb_dimensions']

        #y_pos = -.5*led_y + self.params['power_y_offset'] + .5*(power_width-connector_width)
        y_pos = -.5*led_y + self.params['power_y_offset'] + self.params['power_plug_offset']

        hole_list = [] 
        pos_x = y_pos
        pos_y = -.5*z
        hole = {
                'panel'    : 'left',
                'type'     : 'square',
                'location' : (pos_x, pos_y),
                'size'     : (1.4*power_width, power_height),
                }
        hole_list.append(hole)
        self.params['hole_list'].extend(hole_list)

    def add_sensor_cutout(self):
        """
        Add cutout for sensor
        """
        hole_list = [] 
        sensor_width = self.params['sensor_width']
        sensor_length = self.params['sensor_length']
        tol = self.params['sensor_padding']
        x_pos = 0
        for y_pos in self.get_y_values():
            hole = {
                        'panel'    : 'bottom', 
                        'type'     : 'square', 
                        'location' : (x_pos, y_pos),
                        'size'     : (sensor_length+tol, sensor_width+tol),
                        }
            hole_list.append(hole)
        self.params['hole_list'].extend(hole_list)

    def add_maple_cutout(self):
        """
        Add cutout for maple microcontroller
        """
        led_x, led_y, led_z = self.params['led_pcb_dimensions']
        maple_width = self.params['maple_width']
        maple_length = self.params['maple_length']
        tol = self.params['sensor_padding']
        y_pos = -.5*led_y + self.params['maple_y_offset']
        x_pos = -.5*(led_x - maple_length)
        hole_list = [] 
        hole = {
                    'panel'    : 'bottom', 
                    'type'     : 'square', 
                    'location' : (x_pos, y_pos),
                    'size'     : (maple_length+tol, maple_width+tol),
                    }
        hole_list.append(hole)
        self.params['hole_list'].extend(hole_list)

    def add_power_cutout(self):
        """
        Add cutout for power connector and plug
        """
        hole_list = [] 
        tol = self.params['sensor_padding']
        power_width = self.params['power_width']
        power_length = self.params['power_length']
        connector_length = self.params['connector_length']
        connector_width = self.params['connector_width']
        led_x, led_y, led_z = self.params['led_pcb_dimensions']
        y_pos = -.5*led_y + self.params['power_y_offset']
        x_pos = -.5*(led_x - power_length)
        connector_offset = self.params['power_plug_offset']
        thickness = self.params['wall_thickness']
        bottom_x_overhang = self.params['bottom_x_overhang']
        # Power connector cutout
        hole = {
                    'panel'    : 'bottom', 
                    'type'     : 'square', 
                    'location' : (x_pos, y_pos),
                    'size'     : (power_length+tol, power_width+tol),
                    }
        hole_list.append(hole)
        x_pos = -.5*led_x-thickness-.5*bottom_x_overhang-1
        y_pos += connector_offset
        # Plug head hole (overhang)
        hole = {
                    'panel'    : 'bottom', 
                    'type'     : 'square', 
                    #'location' : (-.5*x-self.params['bottom_x_overhang']-.5*thickness, y_pos),
                    'location' : (x_pos, y_pos),
                    'size'     : (bottom_x_overhang+2, 1.4*power_width),
                    }
        hole_list.append(hole)
        x_pos = -.5*led_x-.5*thickness
        # Plug connector hole
        hole = {
                    'panel'    : 'bottom', 
                    'type'     : 'square', 
                    #'location' : (-.5*x-self.params['bottom_x_overhang']-.5*thickness, y_pos),
                    'location' : (x_pos, y_pos),
                    'size'     : (thickness+2, connector_width),
                    }
        hole_list.append(hole)
        self.params['hole_list'].extend(hole_list)

    def make_sensor(self):
        sensor_x, sensor_y, sensor_z = self.params['sensor_dimensions']
        hole_offset = self.params['sensor_hole_offset']
        hole_diam = self.params['sensor_mount_hole_diam']
        hole_space = self.params['sensor_mount_hole_space']

        # Create hole list 
        hole_list = []
        for i in (-1,1):
            x_pos = i*0.5*hole_space
            y_pos = hole_offset
            hole = (x_pos, y_pos,hole_diam)
            hole_list.append(hole)

        # Create sensor
        sensor = plate_w_holes(sensor_x, sensor_y, sensor_z, hole_list)
        self.sensor = Translate(sensor,v=(0,0,0))

    def make_capillary(self):
        diameter = self.params['capillary_diam']
        length = self.params['capillary_length']
        r = 0.5*diameter
        capillary = Cylinder(h=length,r1=r,r2=r)
        capillary = Rotate(capillary, a=90, v=(0,1,0))
        self.capillary = capillary

    def make_vial_holder_spacer(self):
        diameter = self.params['vial_holder_spacer_diam']
        length = self.params['vial_holder_spacer_length']
        r = 0.5*diameter
        vial_holder_spacer = Cylinder(h=length,r1=r,r2=r)
        self.vial_holder_spacer = vial_holder_spacer

    def make_vial(self):
        diameter = self.params['vial_diam']
        length = self.params['vial_length']
        r = 0.5*diameter
        vial = Cylinder(h=length,r1=r,r2=r)
        vial = Rotate(vial, a=90, v=(0,1,0))
        cap = Cylinder(h=.14*length,r1=1.2*r,r2=1.2*r)
        cap = Rotate(cap, a=90, v=(0,1,0))
        cap = Translate(cap,v=(-.5*length+.07*length,0,0))
        vial = Union([vial]+[cap])
        self.vial = vial

    def make_guide_plates(self):
        guide_x, guide_y, guide_z = self.params['guide_plate_dimensions']
        hole_diam = self.params['guide_thru_hole_diam']
        hole_offset = self.params['guide_hole_offset']
        guide_plate_asym = self.params['guide_plate_asym']
        guide_plate_cutout_y = self.params['guide_plate_cutout_y']
        cut_x = self.params['guide_plate_cutout_x']

        # Create pos and neg guide plates
        hole_list_pos = []
        hole_list_neg = []
        self.guide_plate_pos = []
        self.guide_plate_neg = []
        for i in (-1,1):
            x_pos = i*(0.5*guide_x - hole_offset) 
            y_pos = 0.5*guide_y - hole_offset 
            hole_pos = (x_pos, y_pos, hole_diam)
            hole_neg = (x_pos, -y_pos, hole_diam)
            hole_list_pos.append(hole_pos)
            hole_list_neg.append(hole_neg)

        for cut_y in guide_plate_cutout_y:
            for asym in guide_plate_asym:
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

    def add_guide_tap_holes(self):
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

    def get_guide_plate_holes(self,hole_type='through'):
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
        guide_x, guide_y, guide_z = self.params['guide_plate_dimensions']
        top_x = guide_x
        top_y = 2*guide_y + .9*self.params['capillary_diam']
        top_z = guide_z
        return top_x, top_y, top_z

    def make_led_pcb(self):
        led_x, led_y, led_z = self.params['led_pcb_dimensions']
        hole_list = self.get_led_holes(hole_type='through')
        #print hole_list
        self.led_pcb = plate_w_holes(led_x, led_y, led_z, holes=hole_list)

    def make_diffuser(self):
        diff_x, diff_y, diff_z = self.params['diffuser_dimensions']
        diam = self.params['led_pcb_thru_hole_diam']
        hole_offset_x = self.params['led_pcb_hole_offset_x']
        hole_offset_y = self.params['led_pcb_hole_offset_y']
        diff_y+=2*hole_offset_y
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

    def make_vial_holder(self):
        self.params['y_values'] = self.get_y_values()
        vial_holder = Vial_Holder(self.params)
        self.vial_holder = vial_holder.get_assembly()

    def add_led_holes(self):
        y_shift = self.params['diffuser_offset']
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

    def add_sensor_mounting_holes(self):
        y_shift = self.params['diffuser_offset']
        hole_tuples = self.get_sensor_mounting_holes()
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

    def get_led_holes(self, hole_type='through'):
        led_x, led_y, led_z = self.params['led_pcb_dimensions']
        diff_x, diff_y, diff_z = self.params['diffuser_dimensions']
        hole_offset_x = self.params['led_pcb_hole_offset_x']
        hole_offset_y = self.params['led_pcb_hole_offset_y']
        diff_y+=2*hole_offset_y

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

    def get_sensor_mounting_holes(self, hole_type='through'):
        inner_x, inner_y, inner_z = self.params['inner_dimensions']
        led_x, led_y, led_z = self.params['led_pcb_dimensions']
        hole_offset_x = self.params['led_pcb_hole_offset_x']
        hole_offset_y = self.params['led_pcb_hole_offset_y']
        thickness = self.params['wall_thickness']
        pos = .5*inner_y
        hole_list = []

        for i in (-1,1):
            x_pos = i*(0.5*led_x - hole_offset_x)
            y_pos = .5*led_y - hole_offset_y
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

    def make_diffuser_standoffs(self):
        height = self.params['diffuser_standoff_height']
        diam = self.params['diffuser_standoff_diam']
        radius = 0.5*diam
        self.diffuser_standoff_pos = Cylinder(h=height,r1=radius,r2=radius)
        self.diffuser_standoff_neg = Cylinder(h=height,r1=radius,r2=radius)

    def add_led_cable_hole(self):
        hole_size_x, hole_size_y = self.params['led_cable_hole_size']
        led_x, led_y, led_z = self.params['led_pcb_dimensions']
        y_pos = -.5*led_y + self.params['led_cable_hole_y_offset']
        x_pos = 0
        #print hole_pos_x, hole_pos_y
        hole = {
                'panel'     : 'bottom',
                'type'      : 'square',
                'location'  : (x_pos,y_pos),
                'size'      : (hole_size_x,hole_size_y),
                }
        self.params['hole_list'].append(hole)

    def make_capillary_clamp_thru_holes(self):
        inner_x, inner_y, inner_z = self.params['inner_dimensions']
        wall_thickness = self.params['wall_thickness']
        bottom_x_overhang = self.params['bottom_x_overhang']
        hole_diam = self.params['capillary_clamp_thru_hole_diam']
        hole_offset_x = self.params['capillary_clamp_thru_hole_offset_x']
        hole_offset_y = self.params['capillary_clamp_thru_hole_offset_y']

        hole_list = []
        for y_pos in self.get_y_values():
            pos_x = -0.5*self.bottom_x+hole_offset_x
            pos_y = y_pos-hole_offset_y
            hole = {
                    'panel'    : 'bottom',
                    'type'     : 'round',
                    'location' : (pos_x, pos_y),
                    'size'     : hole_diam,
                    }
            hole_list.append(hole)

        self.params['hole_list'].extend(hole_list)
        self.add_holes(hole_list)

    def make_vial_holder_tap_holes(self):
        pcb_x, pcb_y, pcb_z = self.params['led_pcb_dimensions']
        x, y, z = self.params['diffuser_dimensions']
        holder_x, holder_y, holder_z = self.params['vial_holder_dimensions']
        cap_offset_x = self.params['capillary_hole_offset']
        bottom_x_overhang = self.params['bottom_x_overhang']
        y_shift = self.params['diffuser_offset']
        hole_diam = self.params['capillary_clamp_tap_hole_diam']
        sensor_spacing = self.params['sensor_spacing']


        rails_y_offset = self.params['rails_y_offset']
        y_shift = .5*(pcb_y - holder_y)


        hole_list = []
        pos_x = -(0.5*self.bottom_x - .5*bottom_x_overhang)
        pos_y = (.5*holder_y+y_shift-rails_y_offset,-.5*holder_y+y_shift+rails_y_offset)
        for y_pos in pos_y: 
            hole = {
                    'panel'    : 'bottom',
                    'type'     : 'round',
                    'location' : (-pos_x, y_pos),
                    'size'     : hole_diam,
                    }
            hole_list.append(hole)
        self.params['hole_list'].extend(hole_list)
        self.add_holes(hole_list)

    def make_capillary_clamp(self):
        wall_thickness = self.params['wall_thickness']
        clamp_length = self.params['capillary_clamp_length']
        clamp_width = self.params['capillary_clamp_width']
        clamp_radius = self.params['capillary_clamp_radius']
        hole_offset = self.params['capillary_clamp_tap_hole_offset_y']
        hole_diam = self.params['capillary_clamp_tap_hole_diam']

        clamp_x = clamp_width
        clamp_y = clamp_length
        clamp_z = wall_thickness 
        self.clamp_size = clamp_x, clamp_y, clamp_z

        hole_list = [(0,-hole_offset,hole_diam)]

        clamp = plate_w_holes(clamp_x,clamp_y,clamp_z,hole_list,radius=clamp_radius)
        self.capillary_clamp = clamp

    def get_y_values(self):
        """
        Returns the y_value of the center of the first sensor
        """
        number_of_sensors = self.params['number_of_sensors']
        sensor_spacing = self.params['sensor_spacing']
        array_length = sensor_spacing*number_of_sensors
        thickness =  (self.params['vial_holder_wall_thickness'])
        inner_x, inner_y, inner_z = self.params['inner_dimensions']
        sensor_ypos_offset = self.params['sensor_ypos_offset']
        pcb_x, pcb_y, pcb_z = self.params['led_pcb_dimensions']
        sensor_width = self.params['sensor_width']
        pos = .5*pcb_y - sensor_ypos_offset - .5*sensor_width 
        pos_values = [] 
        for n in range(number_of_sensors):
            pos_values.append(pos-n*self.params['sensor_spacing'])
        return pos_values

class Vial_Holder(object):

    def __init__(self,params):
        self.params = params

    def __make_floor(self):
        holder_x, holder_y, holder_z = self.params['vial_holder_dimensions']
        corner_radius = self.params['lid_radius']
        slot_size =  (self.params['vial_holder_slot_width'],
                      self.params['vial_holder_slot_length']
                     )
        sensor_spacing = self.params['sensor_spacing']
        pcb_x, pcb_y, pcb_z = self.params['led_pcb_dimensions']

        # Add slots for vial holders
        slot_list = []
        shift_y = -(.5*pcb_y - .5*holder_y)
        for i in range(2):
            for y_pos in self.params['y_values']:
                pos_x = (0.4*holder_x)-i*.3*self.params['vial_length']
                pos_y = y_pos + shift_y
                slot = (
                        (pos_x, pos_y),
                        slot_size
                       )
                slot_list.append(slot)

        # Add rails
        rail_length = self.params['vial_holder_rail_length']
        rail_width = self.params['vial_holder_rail_width']
        slot_size =  (rail_length,
                      rail_width,
                     )
        rails_y_offset = self.params['rails_y_offset']
        pos_y = (.5*holder_y-rails_y_offset, -.5*holder_y+rails_y_offset)
        pos_x = -.2*holder_x
        for y_pos in pos_y: 
            slot = (
                    (pos_x, y_pos),
                    slot_size
                   )
            slot_list.append(slot)
        params = {
            'size'      : (holder_x,holder_y,holder_z),    # plate size
            'radius'    : corner_radius, # plate raduis if not given assumed to be none
            'slots'     : slot_list,  # list of hole data
            'hole_list' : [],
        }
        floor = Plate_W_Slots(params)
        floor = floor.make()
        self.floor = floor
        return floor

    def __make_vial_stands(self):
        x,y = self.params['vial_holder_wall_size']
        z = self.params['vial_holder_wall_thickness']
        hole_diam = self.params['vial_diam']

        # Create backplates
        hole_list = []
        x_pos = 0
        y_pos = 0
        hole = (x_pos, y_pos,hole_diam)
        hole_list.append(hole)
        yz_pos = [(.5,self.params['vial_holder_tab_length'],
                  self.params['vial_holder_wall_thickness'],'+')]
        corner_radius = self.params['lid_radius']

        params = {
            'size' : (x,y,z),
            'radius' : corner_radius, 
            'xz+'  : [],
            'xz-'  : [],
            'yz+'  : yz_pos,
            'yz-'  : [],
            'hole_list' : hole_list
            }

        backplate = Plate_W_Tabs(params)
        backplate = backplate.make()
        self.backplate = backplate

        # Create frontplates
        hole_list = []
        x_pos = -.25*x
        y_pos = 0
        hole = (x_pos, y_pos,hole_diam)
        hole_list.append(hole)
        params = {
            'size' : (.5*x,y,z),
            'radius' : corner_radius, 
            'xz+'  : [],
            'xz-'  : [],
            'yz+'  : yz_pos,
            'yz-'  : [],
            'hole_list' : hole_list
            }

        frontplate = Plate_W_Tabs(params)
        frontplate = frontplate.make()
        self.frontplate = frontplate

    def get_assembly(self):
        self.make()
        x,y = self.params['vial_holder_wall_size']
        z = self.params['vial_holder_wall_thickness']
        hole_diam = self.params['vial_diam']
        cap_offset_x = self.params['capillary_hole_offset']

        parts_list = []

        parts_list.append(self.floor)
        holder_x, holder_y, holder_z = self.params['vial_holder_dimensions']

        pcb_x, pcb_y, pcb_z = self.params['led_pcb_dimensions']
        shift_y = -(.5*pcb_y - .5*holder_y) - cap_offset_x

        for y_pos in self.params['y_values']:
            pos_x = (0.4*holder_x)-.3*self.params['vial_length']
            pos_y = y_pos + shift_y
            pos_z = .25*y+.5*self.params['vial_holder_wall_thickness']
            part = Rotate(self.frontplate,a=90,v=(0,1,0))
            part = Translate(part,v=(pos_x,pos_y,pos_z))
            parts_list.append(part)

        for y_pos in self.params['y_values']:
            pos_x = (0.4*holder_x)
            pos_y = y_pos + shift_y
            pos_z = .5*y+.5*self.params['vial_holder_wall_thickness']
            part = Rotate(self.backplate,a=90,v=(0,1,0))
            part = Translate(part,v=(pos_x,pos_y,pos_z))
            parts_list.append(part)

        return parts_list

    def get_projection(self,spacing_factor=4):
        fp_x,fp_y = self.params['vial_holder_wall_size']
        f_x,f_y,foo = self.params['vial_holder_dimensions']
        shift_fp_x = .5*f_x+.5*fp_x+spacing_factor
        shift_fp_y = 0
        shift_bp_x = shift_fp_x+fp_x+spacing_factor
        shift_bp_y = 0
        self.make()

        parts_list = []
        floor = Translate(self.floor,v=(0,0,0))
        frontplate = Rotate(self.frontplate,a=-90,v=(0,0,1))
        frontplate = Translate(frontplate,v=(shift_fp_x,shift_fp_y,0))
        backplate = Rotate(self.backplate,a=-90,v=(0,0,1))
        backplate = Translate(backplate,v=(shift_bp_x,shift_bp_y,0))
        parts_list.append(Projection(floor))
        parts_list.append(Projection(frontplate))
        parts_list.append(Projection(backplate))
        return parts_list

    def make(self):
        floor = self.__make_floor()
        vial_holders = self.__make_vial_stands()
