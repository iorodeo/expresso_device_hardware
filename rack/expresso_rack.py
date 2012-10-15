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
        hole_x_offset = .5*self.params['stability_rod_dia']
        for i in (-1,1):
            for j in (-1,1):
                hole_x = i*j*.5*x_w - j*hole_x_offset
                hole_y = 0
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
        self.holder = holder_maker.make()

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



        y_shift = self.shelf_y_offset - r*math.cos(theta)
        

        slot_maker = Cube(size = (2*shelf_x_overhang,1.5,2*thickness))
        slot_maker = Translate(slot_maker,v=(.5*x_s,-10,0))
        self.left_wall = Difference([self.left_wall,slot_maker])

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
        left_holder = Rotate(self.holder,a=90,v=(1,0,0))
        left_holder = Translate(left_holder,v=(0,y_shift,z_shift))
        right_holder = Rotate(self.holder,a=90,v=(1,0,0))
        right_holder = Translate(right_holder,v=(0,-y_shift,z_shift))
        if show_holders:
            part_list.append(left_holder)
            part_list.append(right_holder)

        ##
        # Add shelf to the assembly parts list.
        ##
        z_shift = 2*25.4-exp_z
        shelf = Translate(self.shelf,v=(0,0,z_shift))
        if show_shelf:
            part_list.append(shelf)
            #part_list.append(self.slot_maker)

        return part_list

    def get_projection(self):
        part_list = []
        return part_list

# Legacy --------------------------------------------------------------------

        #assembly_options= {
                #'gen_walls' : False,
                #'explode' : (0,0,0), 
                #}    
        #assembly_options.update(kwargs)
        #explode = assembly_options['explode']
        #explode_x, explode_y, explode_z = explode
        ## Load bottom plate of capillary array (i.e., upper shelf of rack)
        ##upper_shelf = self.upper_shelf
        ##upper_shelf_assembly = upper_shelf.get_assembly(
                ##show_top=False,
                ##show_bottom=True, 
                ##show_front=False,
                ##show_back=False,
                ##show_left=False,
                ##show_right=False,
                ##show_standoffs=False,
                ##show_capillary=False,
                ##show_sensor=False,
                ##show_diffuser=False,
                ##show_diffuser_standoffs=False,
                ##show_led_pcb=False,
                ##show_guide_plates=False,
                ##show_guide_top=False,
                ##show_clamp=False,
                ##explode=(0,0,0),
            ##)  
        #part_list = []
        #x,y,z = self.params['floor_dimensions']
        #wall_x,wall_y,wall_z = self.params['wall_dimensions']
        #deck_x,deck_y,deck_z = self.params['deck_dimensions']
        #wall_overhang = self.params['wall_overhang']

        #left_shift_x  =-.5*x+wall_overhang+.5*wall_z
        #right_shift_x = .5*x-wall_overhang-.5*wall_z
        #wall_shift_z  = wall_x*.5 + z*.5 + explode_z 
        #left_wall = Rotate(self.left_wall,v=(0,1,0),a=90)
        #left_wall = Translate(left_wall,v=(left_shift_x,0,wall_shift_z))
        #right_wall = Rotate(self.right_wall,v=(0,1,0),a=90)
        #right_wall = Translate(right_wall,v=(right_shift_x,0,wall_shift_z))

        #floor = self.floor
        
        #deck_shift_x = left_shift_x+.5*wall_z+explode_x
        #deck_shift_y = [-1./3.,-1./6.,0.,1./6.,1./3.]
        #deck_shift_z = wall_shift_z - .25*INCH2MM
        #for i in range(5): 
            #deck = Rotate(self.deck,v=(0,1,0),a=90)
            #deck = Translate(deck,v=(deck_shift_x,deck_shift_y[i]*y,deck_shift_z))
            #part_list.append(deck)
        #for i in range(5): 
            #deck = Rotate(self.deck,v=(0,0,1),a=180)
            #deck = Rotate(self.deck,v=(0,1,0),a=90)
            #deck = Translate(deck,v=(-deck_shift_x,deck_shift_y[i]*y,deck_shift_z))
            #part_list.append(deck)

        #bracket_shift_x = deck_shift_x + .5*self.params['bracket_width']
        #bracket_shift_y = wall_y*.25
        #bracket_shift_z = z*.5 + explode_z + .5*INCH2MM

        #left_bracket_back = Rotate(self.bracket,v=(0,0,1),a=180)
        #left_bracket_back = Translate(left_bracket_back,v=(bracket_shift_x,bracket_shift_y,bracket_shift_z))
        #left_bracket_front = Rotate(self.bracket,v=(0,0,1),a=180)
        #left_bracket_front = Translate(left_bracket_front,v=(bracket_shift_x,-bracket_shift_y,bracket_shift_z))
        #right_bracket_back = Translate(self.bracket,v=(-bracket_shift_x,bracket_shift_y,bracket_shift_z))
        #right_bracket_front = Translate(self.bracket,v=(-bracket_shift_x,-bracket_shift_y,bracket_shift_z))

        #part_list.append(left_wall)
        #part_list.append(right_wall)
        #part_list.append(floor)
        #if assembly_options['include_brackets']:
            #part_list.append(left_bracket_front)
            #part_list.append(left_bracket_back)
            #part_list.append(right_bracket_front)
            #part_list.append(right_bracket_back)

        #slot_pos_z, foo = self.params['deck_slot_pos'][0]
        #slot_shift_z = -slot_pos_z + .5*deck_z
        #bs_shift_z = self.params['bs_shift_z']

        #if assembly_options['include_enclosure']:
            #shift_z = deck_shift_z + slot_shift_z + bs_shift_z
            #enclosure_stl_path = self.params['enclosure_stl_path']
            #for filename in glob.glob(os.path.join(enclosure_stl_path, "*.stl")):
                ##print(filename)
                #for i in range(3):
                    #part_stl = Import_STL(filename).cmd_str()
                    #part_stl = Rotate(part_stl,a=-90,v=(0,0,1))
                    #part_stl = Rotate(part_stl,a=45,v=(1,0,0))
                    #part_list.append(Translate(part_stl,v=(0,.3*INCH2MM+deck_shift_y[i]*y,shift_z)))
                #for i in [-1,-2]:
                    #part_stl = Import_STL(filename).cmd_str()
                    #part_stl = Rotate(part_stl,a=-90,v=(0,0,1))
                    #part_stl = Rotate(part_stl,a=45,v=(1,0,0))
                    #part_list.append(Translate(part_stl,v=(0,.3*INCH2MM+deck_shift_y[i]*y,shift_z)))

        ## Load left/right wall
        #if assembly_options['gen_stl']:
            #print "generating stls..."
            ##generate_stl([left_wall],'left_wall')
            ##generate_stl([right_wall],'right_wall')
            ##generate_stl([floor],'floor')
            ##generate_stl([left_bracket_front],'left_bracket_front')
            ##generate_stl([right_bracket_front],'right_bracket_front')
            ##generate_stl([left_bracket_back],'left_bracket_back')
            ##generate_stl([right_bracket_back],'right_bracket_back')
            #generate_stl([deck],'deck')
        #return part_list
    #def __make_capillary_array(self):
        ##upper_shelf = Arrayed_Enclosure(self.params['arrayed_enclosure_params'])
        ##upper_shelf.make()
        ##self.upper_shelf = upper_shelf
        #return 0

    #def __make_bracket(self):
        #filename = self.params['bracket_filename']
        #facet_list = stl_tools.read_stl(filename)
        #shift_x,foo = stl_tools.get_max_min(facet_list,0)
        #shift_y,foo = stl_tools.get_max_min(facet_list,1)
        #shift_z,foo = stl_tools.get_max_min(facet_list,2)
        #stl_tools.write_stl('stl/bracket.stl', facet_list)
        #self.bracket = Translate(Import_STL('stl/bracket.stl').cmd_str(),\
                                 #(-.5*shift_x,-shift_y+.5*.875*INCH2MM,\
                                  #-.5*shift_z))

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
