from __future__ import division
from subprocess import Popen,PIPE
from py2scad import *
import glob, os, math

class Expresso_Rack(object):
    DEG2RAD = math.pi/180
    RAD2DEG = 180/math.pi

    def __init__(self, params):
        self.params = params

    def make(self):
        self.__make_walls()
        self.__make_floor()
        self.__make_holders()
        self.__make_shelf()
        self.__make_shelf_bar()
        self.__make_bracket()
    
    #########################################
    # Rack Components
    #########################################
    def __make_walls(self):
        """
        Creates the left and right walls of the rack (plate w/ tabs).
        """
        x,y,z = self.params['inner_dimensions']
        thickness = self.params['wall_thickness']
        wall_x_overhang = self.params['x_r_overhang']
        d_tab = self.params['wall_tab_dist']
        tab_width = self.params['wall_tab_width']
        dia = self.params['wall_hole_dia_thru']
        dia_tap = self.params['wall_hole_dia_tap']
        wall_hole_y_offset = self.params['wall_hole_y_offset']
        tab_depth = thickness
        x_w = x + 2*wall_x_overhang
        y_w = z
        z_w = thickness
        y_h = self.params['holder_height']

        # Tab and hole (for l-brackets) data for stabilizing the walls
        xz_neg = []
        hole_list = []
        for i in range(0,2*self.params['num_devices'],2):
            # Create tab data for xz- face of walls
            tab_x = wall_x_overhang + (i+1)*d_tab
            tab_data = (tab_x/x_w, tab_width, tab_depth, '+')
            xz_neg.append(tab_data)

            # Create hole data for walls
            if i < 2*self.params['num_devices']-2:
                hole_x = (i+1)*d_tab - .5*x + d_tab
                hole_y = -.5*y_w + wall_hole_y_offset
                hole_data = (hole_x,hole_y,dia_tap)
                hole_list.append(hole_data)
            # Special case for a 1-device rack
            if self.params['num_devices'] == 1:
                hole_x = (i+1)*d_tab - .5*x
                hole_y = -.5*y_w + wall_hole_y_offset
                hole_data = (hole_x,hole_y,dia_tap)
                hole_list.append(hole_data)

        # End holes of the walls, for stability rods
        hole_x_offset = self.params['stability_rod_x_offset']
        for j in (-1,1):
            hole_x = j*.5*x_w - j*hole_x_offset
            hole_y = .5*y_h
            hole_data = (hole_x,hole_y,dia)
            hole_list.append(hole_data)

        holder_hole_offset = self.params['holder_hole_offset']

        # End holes for the holders
        for i in (-1,1):
            for j in (-1,1):
                hole_x = i*j*.5*x - j*d_tab
                for dy in holder_hole_offset:
                    hole_y = dy
                    hole_data = (hole_x,hole_y,dia)
                    hole_list.append(hole_data)

        # Special cases for a 5-device (or greater) rack, I
        # need to add an extra support hole in the middle
        if self.params['num_devices'] >= 5:
            for dy in holder_hole_offset:
                hole_data = (0,dy,dia)
                hole_list.append(hole_data)

        # Pack data into parameters structure
        params = {
                'size'      : (x_w, y_w, z_w),
                'radius'    : self.params['corner_radius'], 
                'xz+'       : [],
                'xz-'       : xz_neg,
                'yz+'       : [],
                'yz-'       : [],
                'hole_list' : hole_list,
        }  

        plate_maker = Plate_W_Tabs(params)
        self.left_wall = plate_maker.make()
        self.right_wall = plate_maker.make()

    def __make_floor(self):
        """
        Creates the floor of the enclosure (plate w/ slots).
        """
        x,y,z = self.params['inner_dimensions']
        thickness = self.params['wall_thickness']
        floor_x_overhang = self.params['x_r_overhang']
        floor_y_overhang = self.params['y_r_overhang']
        d_slot = self.params['wall_tab_dist']
        slot_width = self.params['wall_tab_width']
        tol = self.params['floor_slot_tol']
        dia = self.params['floor_hole_dia_tap']
        floor_hole_y_offset = self.params['floor_hole_y_offset']

        x_f = x + 2*floor_x_overhang
        y_f = y + 2*thickness + 2*floor_y_overhang
        z_f = thickness

        # Create slot data for rack floor
        slot_list = []
        hole_list = []
        size = (slot_width-tol[0], thickness-tol[1])
        for i in range(0,2*self.params['num_devices'],2):
            slot_x = (i+1)*d_slot-.5*x
            for j in (-1,1):
                pos = (slot_x,.5*j*(y+thickness))
                slot_list.append((pos,size))
                # Create hole data for walls
                if i < 2*self.params['num_devices']-2:
                    hole_x = slot_x + d_slot
                    hole_y = -.5*y_f + floor_hole_y_offset
                    hole_data = (hole_x,j*hole_y,dia)
                    hole_list.append(hole_data)
                # Special case for a 1-device rack
                if self.params['num_devices'] == 1:
                    hole_x = slot_x
                    hole_y = -.5*y_f + floor_hole_y_offset
                    hole_data = (hole_x,j*hole_y,dia)
                    hole_list.append(hole_data)

        # Pack data into parameters structure
        params = {
            'size'      : (x_f,y_f,z_f),    
            'radius'    : self.params['corner_radius'], 
            'slots'     : slot_list,  
            'hole_list' : hole_list
        }
        plate_maker = Plate_W_Slots(params)
        self.floor = plate_maker.make()

    def __make_holders(self):
        """
        Creates the left and right 1/4" holders into which the Expresso enclosures
        are placed (custom plate w/ slots)
        """
        x,y,z = self.params['inner_dimensions']
        x_h,foo,bar = self.params['inner_dimensions']
        thickness = self.params['wall_thickness']
        thickness_enc = self.params['wall_thickness_enc']
        holder_slot_size = self.params['holder_slot_size']
        d_slot = self.params['wall_tab_dist']
        dia = self.params['wall_hole_dia_tap']

        y_h = self.params['holder_height']
        z_h = thickness

        r = .5*holder_slot_size[1]
        r_t = .5*thickness_enc
        theta = self.params['tilt_angle']*self.DEG2RAD
        holder_slot_y_offset = .5*y_h + r_t*math.cos(theta) - r*math.cos(theta)
        
        self.shelf_y_offset = holder_slot_y_offset - r*math.cos(theta)

        slot_list = []
        hole_list = []
        for i in range(0,2*self.params['num_devices'],2):
            slot_x = (i+1)*d_slot-.5*x
            pos = (slot_x,holder_slot_y_offset)
            slot_list.append((pos,holder_slot_size))

        holder_hole_offset = self.params['holder_hole_offset']

        # End holes for the holders
        for i in (-1,1):
            for j in (-1,1):
                hole_x = i*j*.5*x_h - j*d_slot
                for dy in holder_hole_offset:
                    hole_y = dy
                    hole_data = (hole_x,hole_y,dia)
                    hole_list.append(hole_data)

        # Special cases for a 5-device (or greater) rack, I
        # need to add an extra support hole in the middle
        if self.params['num_devices'] >= 5:
            for dy in holder_hole_offset:
                hole_data = (0,dy,dia)
                hole_list.append(hole_data)

        params = {
            'size'       : (x_h,y_h,z_h),    
            'radius'     : self.params['corner_radius'], 
            'slots'      : slot_list,  
            'hole_list'  : hole_list,
            'tilt_angle' : self.params['tilt_angle']
            }

        holder_maker = Expresso_Holder(params)
        self.left_holder = holder_maker.make()
        self.right_holder = holder_maker.make()

    def __make_shelf_bar(self):
        shelf_x_overhang = self.params['x_r_overhang']
        radius = self.params['corner_radius']
        x,y,z = self.params['inner_dimensions']
        x_bar = self.params['x_r_overhang']
        y_bar = y+2*self.params['wall_thickness']
        z_bar = self.params['shelf_slot_thickness']
        hole_list = []
        for i in [-1,1]:
            y_shift = i*.25*y
            hole = (0,y_shift,self.params['wall_hole_dia_tap'])
            hole_list.append(hole)

        self.shelf_bar = plate_w_holes(x_bar, y_bar, z_bar, hole_list, '',radius)

    def __make_shelf(self):
        """
        Creates the shelf on which the vials rest (plate w/ tabs).
        """
        x,y,z = self.params['inner_dimensions']
        thickness = self.params['wall_thickness']
        shelf_x_overhang = self.params['x_r_overhang']
        tab_width = self.params['wall_tab_width']
        dia = self.params['wall_hole_dia_thru']
        dia_tap = self.params['wall_hole_dia_tap']
        wall_hole_y_offset = self.params['wall_hole_y_offset']
        shelf_slot_thickness = self.params['shelf_slot_thickness']
        tab_depth = 2*thickness
        x_s = x + 2*shelf_x_overhang
        y_s = y - 2*thickness
        z_s = shelf_slot_thickness

        xz = []
        hole_list = []
        # Create tab data for xz- face of walls
        tab_data = ((x_s-.5*shelf_x_overhang)/x_s, shelf_x_overhang, tab_depth, '+')
        xz.append(tab_data)
        tab_data = (.5*shelf_x_overhang/x_s, shelf_x_overhang, .5*tab_depth, '+')
        xz.append(tab_data)

        for i in [-1,1]:
            x_shift = -.5*x - .5*shelf_x_overhang
            y_shift = i*.25*y
            hole = (x_shift,y_shift,self.params['wall_hole_dia_thru'])
            hole_list.append(hole)

        # Pack data into parameters structure
        params = {
                'size'      : (x_s, y_s, z_s),
                'radius'    : self.params['corner_radius'], 
                'xz+'       : xz,
                'xz-'       : xz,
                'yz+'       : [],
                'yz-'       : [],
                'hole_list' : hole_list,
        }  
        x_shift = .5*x_s

        slot_thickness = self.params['shelf_slot_thickness']
        for i in range(self.params['shelf_slot_num']):
            y_shift = self.params['shelf_z_offset']-i*3*slot_thickness
            slot_maker = Cube(size = (2*shelf_x_overhang,slot_thickness,2*thickness))
            slot_maker = Translate(slot_maker,v=(.5*x_s,y_shift,0))
            self.left_wall = Difference([self.left_wall,slot_maker])
            self.right_wall = Difference([self.right_wall,slot_maker])
            slot_maker = Translate(slot_maker,v=(-x_s,-slot_thickness,0))
            self.left_wall = Difference([self.left_wall,slot_maker])
            self.right_wall = Difference([self.right_wall,slot_maker])

        plate_maker = Plate_W_Tabs(params)
        self.shelf = plate_maker.make()

    def __make_bracket(self):
        pass

    #########################################
    # Rack Assembly
    #########################################
    def get_assembly(self,**kwargs):
        """
        Get enclosure assembly. Shifts all the parts into position, and can explode the 
        generated assembly.
        """
        try:
            show_walls = kwargs['show_walls']
        except KeyError:
            show_walls = True
        try:
            show_floor = kwargs['show_floor']
        except KeyError:
            show_floor = True
        try:
            show_holders = kwargs['show_holders']
        except KeyError:
            show_holders = True
        try:
            show_shelf = kwargs['show_shelf']
        except KeyError:
            show_shelf = True
        try:
            explode = kwargs['explode']
        except KeyError:
            explode = (0,0,0)

        part_list = []
        
        ##
        # Add walls to the assembly parts list.
        ##
        x,y,z = self.params['inner_dimensions']
        thickness = self.params['wall_thickness']
        wall_x_overhang = self.params['x_r_overhang']
        exp_x,exp_y,exp_z = explode
        x_w = x + 2*wall_x_overhang
        y_w = z
        z_w = thickness

        y_shift = .5*y+.5*thickness + 2*exp_y
        z_shift = .5*z+.5*thickness + exp_z
        left_wall = Rotate(self.left_wall,a=90,v=(1,0,0))
        left_wall = Translate(left_wall,v=(0,y_shift,z_shift))
        right_wall = Rotate(self.right_wall,a=90,v=(1,0,0))
        right_wall = Translate(right_wall,v=(0,-y_shift,z_shift))
        if show_walls:
            part_list.append(left_wall)
            part_list.append(right_wall)

        ##
        # Add floor to the assembly parts list.
        ##
        z_shift = -exp_z
        floor = Translate(self.floor,v=(0,0,z_shift))
        if show_floor:
            part_list.append(floor)

        ##
        # Add holders to the assembly parts list.
        ##
        y_h = self.params['holder_height']
        y_shift =  .5*y - .5*thickness + exp_y
        z_shift = .5*thickness + .5*y_h + self.params['holder_z_offset'] + exp_z
        left_holder = Rotate(self.left_holder,a=90,v=(1,0,0))
        left_holder = Translate(left_holder,v=(0,y_shift,z_shift))
        right_holder = Rotate(self.right_holder,a=90,v=(1,0,0))
        right_holder = Translate(right_holder,v=(0,-y_shift,z_shift))
        if show_holders:
            part_list.append(left_holder)
            part_list.append(right_holder)

        ##
        # Add shelf to the assembly parts list.
        ##
        z_shift = .5*z + .5*thickness + self.params['shelf_z_offset']
        shelf = Translate(self.shelf,v=(0,0,z_shift))
        x_shift = .5*x+.5*self.params['x_r_overhang']
        shelf_bar = Translate(self.shelf_bar,v=(-x_shift,0,z_shift-self.params['shelf_slot_thickness']))
        if show_shelf:
            part_list.append(shelf)
            part_list.append(shelf_bar)

        return part_list

    def get_walls_projection(self):
        x,y,z = self.params['inner_dimensions']
        thickness = self.params['wall_thickness']
        floor_x_overhang = self.params['x_r_overhang']
        floor_y_overhang = self.params['y_r_overhang']
        x_shift = .5*z+thickness
        part_list = []

        #left_wall = Rotate(self.left_wall,a=90,v=(0,0,1))
        #left_wall = Translate(left_wall,v=(-x_shift,0,0))
        left_wall = Projection(self.left_wall)
        #right_wall = Rotate(self.right_wall,a=-90,v=(0,0,1))
        #right_wall = Translate(right_wall,v=(x_shift,0,0))
        right_wall = Projection(self.right_wall)
        
        part_list.append(left_wall) 
        part_list.append(right_wall) 

        return part_list

    def get_holders_projection(self):
        x,y,z = self.params['inner_dimensions']
        thickness = self.params['wall_thickness']
        floor_x_overhang = self.params['x_r_overhang']
        floor_y_overhang = self.params['y_r_overhang']
        x_shift = .5*z+thickness
        part_list = []

        #left_holder = Rotate(self.left_holder,a=90,v=(0,0,1))
        #left_holder = Translate(left_holder,v=(-x_shift,0,0))
        left_holder = Projection(self.left_holder)
        #right_holder = Rotate(self.right_holder,a=-90,v=(0,0,1))
        #right_holder = Translate(right_holder,v=(x_shift,0,0))
        right_holder = Projection(self.right_holder)
        
        part_list.append(left_holder) 
        part_list.append(right_holder) 

        return part_list

    def get_floor_projection(self):
        part_list = []
        floor = Projection (self.floor)
        part_list.append(floor)
        return part_list

    def get_shelf_projection(self):
        x,y,z = self.params['inner_dimensions']
        thickness = self.params['wall_thickness']
        floor_x_overhang = self.params['x_r_overhang']
        floor_y_overhang = self.params['y_r_overhang']

        part_list = []
        shelf = Projection (self.shelf)
        shelf_bar = Projection (self.shelf_bar)

        part_list.append(shelf)
        part_list.append(shelf_bar)

        return part_list

#########################################
# Holder Class
#########################################
class Expresso_Holder(object):
    """
    A custom plate w/ slots that allows me to specify the tilt angle
    of the slots.
    """
    def __init__(self, params):
        self.params = params

    def __add_slots(self):

        hole_list = []

        for pos, size in self.params['slots']:
            x, y = size
            z = 2*self.params['size'][2]
            hole = Cube(size=(x, y, z))
            pos_x, pos_y = pos
            hole = Rotate(hole,v=(0,0,1),a=self.params['tilt_angle'])
            hole = Translate(hole,v=[pos_x, pos_y, 0])
            hole_list.append(hole)

        self.plate = Difference([self.plate] + hole_list)

    def __add_holes(self):

        try:
            holes = self.params['hole_list']
        except KeyError:
            holes = []
        plate_x, plate_y, plate_z = self.params['size']
        height = plate_z
        cylinders = []
        for x,y,r in holes:
            c = Cylinder(h=4*height,r1=0.5*r, r2=0.5*r)
            c = Translate(c,v=[x,y,0])
            cylinders.append(c)
        self.plate = Difference([self.plate] + cylinders)

    def make(self):
        try:
            radius = self.params['radius']
        except KeyError:
            radius = None

        if radius is None:
            self.plate = Cube(size=self.params['size'])
        else:
            x,y,z = self.params['size']
            self.plate = rounded_box(x, y, z, radius, round_z=False)

        self.__add_slots()
        self.__add_holes()
        return self.plate
