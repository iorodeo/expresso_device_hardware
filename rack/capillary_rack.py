from __future__ import division
from subprocess import Popen,PIPE
from py2scad import *
import glob, os

def generate_stl(part,filename):
    """
    Creates the left and right side panels of the enclosure
    (plate w/ tabs).
    """
    filename = 'stl/'+filename
    prog_assembly = SCAD_Prog()
    prog_assembly.fn = 100 # Raised to 100 or otherwise STL won't show
    for p in part:
        prog_assembly.add(p)
    prog_assembly.write('temp.scad')        
    Popen('openscad -s '+filename+'.stl'+' temp.scad',shell=True,stdout=PIPE).wait()
    Popen('rm temp.scad',shell=True,stdout=PIPE).wait()
    part_stl = Import_STL(filename+'.stl').cmd_str()
    return part_stl

def generate_dxf(part,filename):
    """
    Creates the left and right side panels of the enclosure
    (plate w/ tabs).
    """
    filename = 'dxf/'+filename
    prog_assembly = SCAD_Prog()
    prog_assembly.fn = 100 # Raised to 100 or otherwise STL won't show
    for p in part:
        prog_assembly.add(Projection(p))
    prog_assembly.write('temp.scad')        
    Popen('openscad -x '+filename+'.dxf'+' temp.scad',shell=True,stdout=PIPE).wait()
    Popen('rm temp.scad',shell=True,stdout=PIPE).wait()

class Capillary_Deck(object):
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
        
class Capillary_Rack(object):
    def __init__(self, params):
        self.params = params

    def __make_capillary_array(self):
        #upper_shelf = Arrayed_Enclosure(self.params['arrayed_enclosure_params'])
        #upper_shelf.make()
        #self.upper_shelf = upper_shelf
        return 0

    def __make_walls(self):
        """
        Creates the left and right side panels of the enclosure
        (plate w/ tabs).
        """
        inner_x, inner_y, inner_z = self.params['wall_dimensions']
        tab_width = self.params['wall_tab_width']
        try:
            depth_adjust = self.params['tab_depth_adjust']
        except KeyError:
            depth_adjust = 0.0

        # Only apply tab depth adjustment to positive tabs
        tab_depth_pos = inner_z + depth_adjust 

        # Create tab data for yz faces of side panels
        yz_pos = []
        for loc in self.params['wall_tabs']:
            tab_data = (loc, tab_width, tab_depth_pos, '+')
            yz_pos.append(tab_data)

        # Pack panel data into parameters structure
        params = {
                'size'      : (inner_x, inner_y, inner_z),
                'radius'    : self.params['corner_radius'], 
                'xz+'       : [],
                'xz-'       : [],
                'yz+'       : yz_pos,
                'yz-'       : [],
                'hole_list' : self.params['wall_holes'],
                }

        plate_maker = Plate_W_Tabs(params)
        self.left_wall = plate_maker.make()
        self.right_wall = plate_maker.make()

    def __make_floor(self):
        """
        Creates the floor of the enclosure (plate w/ slots).
        """
        floor_x, floor_y, floor_z = self.params['floor_dimensions']
        slot_list = []
        for pos,size in zip(self.params['floor_slot_pos'],self.params['floor_slot_size']):
            slot_list.append((pos,size))
        params = {
            'size'      : (floor_x,floor_y,floor_z),    
            'radius'    : self.params['corner_radius'], 
            'slots'     : slot_list,  
            'hole_list' : self.params['floor_hole_list']
            }
        plate_maker = Plate_W_Slots(params)
        self.floor = plate_maker.make()

    def __make_bracket(self):
        filename = self.params['bracket_filename']
        facet_list = stl_tools.read_stl(filename)
        shift_x,foo = stl_tools.get_max_min(facet_list,0)
        shift_y,foo = stl_tools.get_max_min(facet_list,1)
        shift_z,foo = stl_tools.get_max_min(facet_list,2)
        stl_tools.write_stl('stl/bracket.stl', facet_list)
        self.bracket = Translate(Import_STL('stl/bracket.stl').cmd_str(),\
                                 (-.5*shift_x,-shift_y+.5*.875*INCH2MM,\
                                  -.5*shift_z))
    
    def __make_decks(self):
        deck_x, deck_y, deck_z = self.params['deck_dimensions']
        slot_list = []
        for pos,size in zip(self.params['deck_slot_pos'],self.params['deck_slot_size']):
            slot_list.append((pos,size))
        params = {
            'size'       : (deck_x,deck_y,deck_z),    
            'radius'     : self.params['corner_radius'], 
            'slots'      : slot_list,  
            'hole_list'  : self.params['deck_hole_list'],
            'tilt_angle' : self.params['tilt_angle']
            }
        deck_maker = Capillary_Deck(params)
        self.deck = deck_maker.make()

    def make(self):
        self.__make_capillary_array() # Upper shelf
        self.__make_walls()
        self.__make_floor()
        self.__make_decks()
        self.__make_bracket()
    
    def get_projection(self):
        part_list = []
        spacing = self.params['projection_spacing']
        x,y,z = self.params['floor_dimensions']
        wall_x,wall_y,wall_z = self.params['wall_dimensions']
        left_shift_x = -.5*x-.5*wall_x-spacing
        right_shift_x = .5*x+.5*wall_x+spacing
        left_wall = Translate(self.left_wall,v=(left_shift_x,0,0))
        right_wall = Rotate(self.right_wall,v=(0,1,0),a=180)
        right_wall = Translate(right_wall,v=(right_shift_x,0,0))

        floor = self.floor
        
        deck_x,deck_y,deck_z = self.params['deck_dimensions']
        deck_shift_x = left_shift_x - spacing - .5*deck_x - .5*wall_x
        deck_shift_y = [-1./3.,-1./6.,0.,1./6.,1./3.]

        for i in range(5): 
            deck = Translate(self.deck,v=(deck_shift_x,deck_shift_y[i]*y,0))
            part_list.append(Projection(deck))
        for i in range(5): 
            deck = Rotate(self.deck,v=(0,0,1),a=180)
            deck = Rotate(self.deck,v=(0,1,0),a=180)
            deck = Translate(deck,v=(-deck_shift_x,deck_shift_y[i]*y,0))
            part_list.append(Projection(deck))
        part_list.append(Projection(left_wall))
        part_list.append(Projection(right_wall))
        part_list.append(Projection(floor))

        return part_list

    def get_assembly(self,**kwargs):
        """  
        Returns a list of the enclosure parts in assembled positions.
        """
        assembly_options= {
                'gen_walls' : False,
                'explode' : (0,0,0), 
                }    
        assembly_options.update(kwargs)
        explode = assembly_options['explode']
        explode_x, explode_y, explode_z = explode
        # Load bottom plate of capillary array (i.e., upper shelf of rack)
        #upper_shelf = self.upper_shelf
        #upper_shelf_assembly = upper_shelf.get_assembly(
                #show_top=False,
                #show_bottom=True, 
                #show_front=False,
                #show_back=False,
                #show_left=False,
                #show_right=False,
                #show_standoffs=False,
                #show_capillary=False,
                #show_sensor=False,
                #show_diffuser=False,
                #show_diffuser_standoffs=False,
                #show_led_pcb=False,
                #show_guide_plates=False,
                #show_guide_top=False,
                #show_clamp=False,
                #explode=(0,0,0),
            #)  
        part_list = []
        x,y,z = self.params['floor_dimensions']
        wall_x,wall_y,wall_z = self.params['wall_dimensions']
        deck_x,deck_y,deck_z = self.params['deck_dimensions']
        wall_overhang = self.params['wall_overhang']

        left_shift_x  =-.5*x+wall_overhang+.5*wall_z
        right_shift_x = .5*x-wall_overhang-.5*wall_z
        wall_shift_z  = wall_x*.5 + z*.5 + explode_z 
        left_wall = Rotate(self.left_wall,v=(0,1,0),a=90)
        left_wall = Translate(left_wall,v=(left_shift_x,0,wall_shift_z))
        right_wall = Rotate(self.right_wall,v=(0,1,0),a=90)
        right_wall = Translate(right_wall,v=(right_shift_x,0,wall_shift_z))

        floor = self.floor
        
        deck_shift_x = left_shift_x+.5*wall_z+explode_x
        deck_shift_y = [-1./3.,-1./6.,0.,1./6.,1./3.]
        deck_shift_z = wall_shift_z - .25*INCH2MM
        for i in range(5): 
            deck = Rotate(self.deck,v=(0,1,0),a=90)
            deck = Translate(deck,v=(deck_shift_x,deck_shift_y[i]*y,deck_shift_z))
            part_list.append(deck)
        for i in range(5): 
            deck = Rotate(self.deck,v=(0,0,1),a=180)
            deck = Rotate(self.deck,v=(0,1,0),a=90)
            deck = Translate(deck,v=(-deck_shift_x,deck_shift_y[i]*y,deck_shift_z))
            part_list.append(deck)

        bracket_shift_x = deck_shift_x + .5*self.params['bracket_width']
        bracket_shift_y = wall_y*.25
        bracket_shift_z = z*.5 + explode_z + .5*INCH2MM

        left_bracket_back = Rotate(self.bracket,v=(0,0,1),a=180)
        left_bracket_back = Translate(left_bracket_back,v=(bracket_shift_x,bracket_shift_y,bracket_shift_z))
        left_bracket_front = Rotate(self.bracket,v=(0,0,1),a=180)
        left_bracket_front = Translate(left_bracket_front,v=(bracket_shift_x,-bracket_shift_y,bracket_shift_z))
        right_bracket_back = Translate(self.bracket,v=(-bracket_shift_x,bracket_shift_y,bracket_shift_z))
        right_bracket_front = Translate(self.bracket,v=(-bracket_shift_x,-bracket_shift_y,bracket_shift_z))

        part_list.append(left_wall)
        part_list.append(right_wall)
        part_list.append(floor)
        if assembly_options['include_brackets']:
            part_list.append(left_bracket_front)
            part_list.append(left_bracket_back)
            part_list.append(right_bracket_front)
            part_list.append(right_bracket_back)

        slot_pos_z, foo = self.params['deck_slot_pos'][0]
        slot_shift_z = -slot_pos_z + .5*deck_z
        bs_shift_z = self.params['bs_shift_z']

        if assembly_options['include_enclosure']:
            shift_z = deck_shift_z + slot_shift_z + bs_shift_z
            enclosure_stl_path = self.params['enclosure_stl_path']
            for filename in glob.glob(os.path.join(enclosure_stl_path, "*.stl")):
                #print(filename)
                for i in range(3):
                    part_stl = Import_STL(filename).cmd_str()
                    part_stl = Rotate(part_stl,a=-90,v=(0,0,1))
                    part_stl = Rotate(part_stl,a=45,v=(1,0,0))
                    part_list.append(Translate(part_stl,v=(0,.3*INCH2MM+deck_shift_y[i]*y,shift_z)))
                for i in [-1,-2]:
                    part_stl = Import_STL(filename).cmd_str()
                    part_stl = Rotate(part_stl,a=-90,v=(0,0,1))
                    part_stl = Rotate(part_stl,a=45,v=(1,0,0))
                    part_list.append(Translate(part_stl,v=(0,.3*INCH2MM+deck_shift_y[i]*y,shift_z)))

        # Load left/right wall
        if assembly_options['gen_stl']:
            print "generating stls..."
            #generate_stl([left_wall],'left_wall')
            #generate_stl([right_wall],'right_wall')
            #generate_stl([floor],'floor')
            #generate_stl([left_bracket_front],'left_bracket_front')
            #generate_stl([right_bracket_front],'right_bracket_front')
            #generate_stl([left_bracket_back],'left_bracket_back')
            #generate_stl([right_bracket_back],'right_bracket_back')
            generate_stl([deck],'deck')
        return part_list