"""
Creates a rack for an array of capillary sensors
"""
from __future__ import division
from py2scad import *
from subprocess import Popen,PIPE
import math, sys


sys.path.append('/home/cisco/repos/iorodeo/capillary_sensor_enclosure')
from arrayed_enclosure import Arrayed_Enclosure
from make_enclosure import params as arrayed_enclosure_params
from bottom_shelf import *

INCH2MM = 25.4
DEG2RAD = math.pi/180
RAD2DEG = 180/math.pi

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
    return part_stl

def generate_dxf(part,filename):
    filename = 'dxf/'+filename
    prog_assembly = SCAD_Prog()
    prog_assembly.fn = 100 # Raised to 100 or otherwise STL won't show
    for p in part:
        prog_assembly.add(Projection(p))
    prog_assembly.write('temp.scad')        
    Popen('openscad -x '+filename+'.dxf'+' temp.scad',shell=True,stdout=PIPE).wait()
    Popen('rm temp.scad',shell=True,stdout=PIPE).wait()

class Capillary_Rack(object):
    def __init__(self, params):
        self.params = params

    def __make_walls(self):
        x,y,z = self.params['wall_dimensions'] 
        self.wall_width, self.wall_length, self.wall_depth = x,y,z
        bottom_shelf_incl = self.params['bottom_shelf_incl'] 
        upper_shelf_incl = self.params['upper_shelf_incl'] 
        shelves_x_offset = self.params['shelves_x_offset']
        shelves_y_offset = self.params['shelves_y_offset']
        shelves_separation = self.params['shelves_separation']
        wallshelf_hole_spacing_x,wallshelf_hole_spacing_y = self.params['wallshelf_hole_spacing']
        wall_hole_radius = self.params['wall_hole_radius']
        self.wall_hole_radius = wall_hole_radius
        upper_shelf = self.upper_shelf
        floor_x, floor_y = upper_shelf.array_bottom_size
        wall_hole_list = []
        
        # Bottom & upper shelf positioning
        shelf_incl_arr = [bottom_shelf_incl,bottom_shelf_incl+180*DEG2RAD,
                          upper_shelf_incl,upper_shelf_incl+180*DEG2RAD]
        sign_arr = [-1,1]
        for i in range(4):
            ang = shelf_incl_arr[i]
            hole_x = .5*wallshelf_hole_spacing_x*math.cos(ang)
            hole_y = (.5*wallshelf_hole_spacing_x-.5*shelves_separation-.5*shelves_y_offset)*math.sin(ang)
            hole_x = hole_x+.5*shelves_separation*math.cos(ang)*sign_arr[int(i/2)]
            hole_y = hole_y+(shelves_separation+shelves_y_offset)*math.sin(ang)*(i>1)
            # 1/4-20 holes
            hole = (hole_x,hole_y,wall_hole_radius)
            wall_hole_list.append(hole)

        # Bracket wallfoot holes positioning (wall)
        wallfoot_hole_spacing_x,wallfoot_hole_spacing_y = self.params['wallfoot_hole_spacing']
        # x is the shorter dimension of the wall
        sign_arr = [1,-1]
        for i in range(4):
            wall_hole_list.append(( sign_arr[int(i/2)]*.25*x+sign_arr[i%2]*.5*wallfoot_hole_spacing_x,
                                    -.5*y+wallfoot_hole_spacing_y,wall_hole_radius))

        wall = plate_w_holes(x,y,z,wall_hole_list,radius=self.params['corner_radius'])
        diff_cube = Cube(size=(x,2*y,1*INCH2MM))
        diff_cube = Rotate(diff_cube,a=-45,v=(0,0,1))
        diff_cube = Translate(diff_cube,v=(-4*INCH2MM,5*INCH2MM,0))
        self.wall = Difference([wall,diff_cube])

        if self.params['create_wall_dxf']:
            print "Generating wall.dxf..."
            generate_dxf([self.wall],'wall')

    def __make_foot(self):
        x,y,z = self.params['foot_dimensions']
        self.foot_width,self.foot_length,self.foot_depth = x,y,z
        sign_arr = [1,-1]
        # Bracket holes - foot
        foot_hole_list = []
        wall_width, wall_depth = self.wall_width, self.wall_depth
        wall_hole_radius = self.wall_hole_radius
        wallfoot_hole_spacing_x,wallfoot_hole_spacing_y = self.params['wallfoot_hole_spacing']
        ## Rear half of the foot
        rear_bracket_x = -.25*self.wall_width
        rear_bracket_y = .5*y-wallfoot_hole_spacing_y
        front_bracket_y = .5*y-3*wallfoot_hole_spacing_y-wall_depth
        for i in range(4):
            foot_hole_list.append((rear_bracket_x+sign_arr[i%2]*wallfoot_hole_spacing_y,
                                   sign_arr[int(i/2)]*rear_bracket_y,wall_hole_radius))
            foot_hole_list.append((-rear_bracket_x+sign_arr[i%2]*wallfoot_hole_spacing_y,
                                    sign_arr[int(i/2)]*front_bracket_y,wall_hole_radius))
        # For the USB hub
        foot_hole_list.append((-rear_bracket_x+wallfoot_hole_spacing_y,wallfoot_hole_spacing_y,
                              wall_hole_radius))
        foot_hole_list.append((-rear_bracket_x+wallfoot_hole_spacing_y,-wallfoot_hole_spacing_y,
                              wall_hole_radius))

        self.foot = plate_w_holes(x,y,z,foot_hole_list,radius=self.params['corner_radius'])
        if self.params['create_foot_dxf']:
            print "Generating foot.dxf..."
            generate_dxf([self.foot],'foot')

    def __make_bracket(self):
        filename = self.params['bracket_filename']
        wallshelf_hole_spacing_x,wallshelf_hole_spacing_y = self.params['wallshelf_hole_spacing']
        facet_list = stl_tools.read_stl(filename)
        shift_x,foo = stl_tools.get_max_min(facet_list,0)
        shift_y,foo = stl_tools.get_max_min(facet_list,1)
        shift_z,foo = stl_tools.get_max_min(facet_list,2)
        stl_tools.write_stl('stl/bracket.stl', facet_list)
        self.bracket = Translate(Import_STL('stl/bracket.stl').cmd_str(),\
                                 (-.5*shift_x,-shift_y+wallshelf_hole_spacing_y,\
                                  -.5*shift_z))

    def __make_capillary_array(self):
        upper_shelf = Arrayed_Enclosure(self.params['arrayed_enclosure_params'])
        upper_shelf.make()
        self.upper_shelf = upper_shelf

        # Dimensions of walls and foot depend on floor size
        thickness = upper_shelf.params['wall_thickness']
        wallshelf_hole_spacing_x,wallshelf_hole_spacing_y = self.params['wallshelf_hole_spacing']
        # floor_x < floor_y
        floor_x, floor_y = upper_shelf.array_bottom_size
        wall_length = 10.5*INCH2MM
        wall_width = floor_x + 6*INCH2MM
        wall_depth = thickness

        foot_length = floor_y+2*(thickness+wallshelf_hole_spacing_x)

        self.params['shelves_separation']=self.params['shelves_separation']+floor_x
        self.params['wall_dimensions'] = (wall_width,wall_length,wall_depth)
        self.params['foot_dimensions'] = (wall_width,foot_length,thickness)

    def __make_bottom_shelf(self):
        # Setup the parameters to generate capillary array (only care about the bottom plate)
        from bottom_shelf import params
        upper_shelf = self.upper_shelf
        floor_x, floor_y = upper_shelf.array_bottom_size
        # 1/4" for threaded inserts
        floor_z = .25*INCH2MM
        params['floor_dimensions'] = (floor_x,floor_y,floor_z)

        sensor_pos_y = upper_shelf.get_array_y_values();
        num_sensors = upper_shelf.params['number_of_sensors']
        floor_hole_list = [( .5*INCH2MM,.5*floor_y-.5*INCH2MM,.2*INCH2MM), #bracket holes
                           (-.5*INCH2MM,.5*floor_y-.5*INCH2MM,.2*INCH2MM),
                           ( .5*INCH2MM,-.5*floor_y+.5*INCH2MM,.2*INCH2MM),
                           (-.5*INCH2MM,-.5*floor_y+.5*INCH2MM,.2*INCH2MM)]
        x = .75*INCH2MM-.5*.152*INCH2MM-.5*.125*INCH2MM
        for i in range(num_sensors):
            shift_y = sensor_pos_y[i]
            # Holes for 4-40 inserts, .152 recommended
            floor_hole_list.append((x, .5*INCH2MM+shift_y,.15*INCH2MM)),
            floor_hole_list.append((x,-.5*INCH2MM+shift_y,.15*INCH2MM))

        params['floor_hole_list'] = floor_hole_list 
        params['num_sensors'] = num_sensors
        params['cart_pos_y'] = sensor_pos_y

        bottom_shelf = Bottom_Shelf(params)
        bottom_shelf.make()
        self.bottom_shelf = bottom_shelf
        if self.params['create_shelf_dxf']:
            shelf = bottom_shelf.get_projection()
            #need to write a get projection
            print "Generating shelf.dxf..."
            generate_dxf([shelf],'shelf')

    def make(self):
        self.__make_capillary_array() # Upper shelf
        self.__make_bottom_shelf()
        self.__make_walls()
        self.__make_foot()
        self.__make_bracket()
    
    def get_projection(self):
        part_list = []
        return part_list

    def get_assembly(self,**kwargs):
        """  
        Returns a list of the enclosure parts in assembled positions.
        """
        assembly_options= {
                'gen_walls' : False,
                'gen_foot' : False,
                'gen_ca' : False,
                'gen_bs' : False,
                'explode' : (0,0,0), 
                }    
        assembly_options.update(kwargs)
        explode = assembly_options['explode']
        explode_x, explode_y, explode_z = explode

        # Load bottom plate of capillary array (i.e., upper shelf of rack)
        upper_shelf = self.upper_shelf
        upper_shelf_assembly = upper_shelf.get_assembly(
                show_top=False,
                show_bottom=True, 
                show_front=False,
                show_back=False,
                show_left=False,
                show_right=False,
                show_standoffs=False,
                show_capillary=False,
                show_sensor=False,
                show_diffuser=False,
                show_diffuser_standoffs=False,
                show_led_pcb=False,
                show_guide_plates=False,
                show_guide_top=False,
                show_clamp=False,
                explode=(0,0,0),
            )  
        upper_shelf_incl = self.params['upper_shelf_incl'] 
        bottom_shelf_incl = self.params['bottom_shelf_incl'] 
        shelves_x_offset = self.params['shelves_x_offset']
        shelves_y_offset = self.params['shelves_y_offset']
        shelves_separation = self.params['shelves_separation']
        wallshelf_hole_spacing_x, wallshelf_hole_spacing_y = self.params['wallshelf_hole_spacing']
        upper_shelf_assembly_offset = -self.params['upper_shelf_assembly_offset']

        # Position walls
        floor_x, floor_y = upper_shelf.array_bottom_size
        shift_y = .5*floor_y+.5*self.wall_depth+explode_y
        shift_z = .5*self.wall_length
        left_wall = Rotate(self.wall,a=90,v=(1,0,0))
        left_wall = Translate(left_wall,v=(0,-shift_y,shift_z))
        right_wall = Rotate(self.wall,a=90,v=(1,0,0))
        right_wall = Translate(right_wall,v=(0,shift_y,shift_z))
        
        # Position foot
        shift_z = .5*self.foot_depth
        foot = Translate(self.foot,v=(0,0,-shift_z))

        # Position upper shelf brackets
        shift_x = .5*shelves_separation*math.cos(upper_shelf_incl)
        # Using wallshelf_hole_spacing_y as the center of bracket aligns with center of wall (from a top view)
        shift_y = .5*floor_y-wallshelf_hole_spacing_y+explode_y
        shift_z = .5*self.wall_length+(.5*shelves_separation+.5*shelves_y_offset)*math.sin(upper_shelf_incl)+explode_z
        left_bracket_upper_shelf = Rotate(self.bracket,a=-upper_shelf_incl*RAD2DEG,v=(0,1,0))
        left_bracket_upper_shelf = Translate(left_bracket_upper_shelf,v=(shift_x,-shift_y,shift_z))
        right_bracket_upper_shelf = Rotate(self.bracket,a=180,v=(0,0,1))
        right_bracket_upper_shelf = Rotate(right_bracket_upper_shelf,a=-upper_shelf_incl*RAD2DEG,v=(0,1,0))
        right_bracket_upper_shelf = Translate(right_bracket_upper_shelf,v=(shift_x,shift_y,shift_z))

        # Position bottom shelf brackets
        shift_y = .5*floor_y-wallshelf_hole_spacing_y+explode_y
        shift_z = .5*self.wall_length-(.5*shelves_separation+.5*shelves_y_offset)*math.sin(upper_shelf_incl)+explode_z
        left_bracket_bottom_shelf = Rotate(self.bracket,a=-bottom_shelf_incl*RAD2DEG,v=(0,1,0))
        left_bracket_bottom_shelf = Translate(left_bracket_bottom_shelf,v=(-shift_x,-shift_y,shift_z))
        right_bracket_bottom_shelf = Rotate(self.bracket,a=180,v=(0,0,1))
        right_bracket_bottom_shelf = Rotate(right_bracket_bottom_shelf,a=-bottom_shelf_incl*RAD2DEG,v=(0,1,0))
        right_bracket_bottom_shelf = Translate(right_bracket_bottom_shelf,v=(-shift_x,shift_y,shift_z))

        # Position foot brackets
        shift_x = .25*self.wall_width
        shift_y = .5*floor_y-wallshelf_hole_spacing_y+explode_y
        shift_z = wallshelf_hole_spacing_y+explode_z
        left_bracket_front_foot = Translate(self.bracket,v=(shift_x,-shift_y,shift_z))
        right_bracket_front_foot = Rotate(self.bracket,a=180,v=(0,0,1))
        right_bracket_front_foot = Translate(right_bracket_front_foot,v=(shift_x,shift_y,shift_z))

        shift_x = -.25*self.wall_width
        shift_y = .5*floor_y+wallshelf_hole_spacing_y+self.wall_depth+explode_y
        left_bracket_back_foot = Translate(self.bracket,v=(shift_x,shift_y,shift_z))
        right_bracket_back_foot = Rotate(self.bracket,a=180,v=(0,0,1))
        right_bracket_back_foot = Translate(right_bracket_back_foot,v=(shift_x,-shift_y,shift_z))

        # Generate or load STL files, and load them into the part_list for rendering
        part_list = []
        # Load left/right wall
        if assembly_options['gen_walls']:
            left_wall = generate_stl([left_wall],'left_wall')
        else:
            left_wall = Import_STL('stl/left_wall.stl').cmd_str()
        if assembly_options['gen_walls']:
            right_wall = generate_stl([right_wall],'right_wall')
        else:
            right_wall = Import_STL('stl/right_wall.stl').cmd_str()
        # Load foot
        if assembly_options['gen_foot']:
            foot = generate_stl([foot],'foot')
        else:
            foot = Import_STL('stl/foot.stl').cmd_str()
        # Load bottom shelf 
        # NOTE: openscad fails at generating the STL for upper shelf (cap. array)
        #if assembly_options['gen_ca']: # openscad fails at generating the STL for this one
            #upper_shelf = generate_stl(upper_shelf,'upper_shelf')
        #else:
            #upper_shelf = Import_STL('stl/upper_shelf.stl').cmd_str()
        #part_list.append(upper_shelf)
        bottom_shelf = self.bottom_shelf
        bottom_shelf_thickness = bottom_shelf.thickness
        bottom_shelf = bottom_shelf.get_assembly(
                 explode=(0,0,0),
            )
        if assembly_options['gen_bs']:             
            bottom_shelf = generate_stl([bottom_shelf],'bottom_shelf')
        else:
            bottom_shelf = Import_STL('stl/bottom_shelf.stl').cmd_str()

        # Position bottom shelf
        shift_x = (.5*shelves_separation-wallshelf_hole_spacing_y-.5*bottom_shelf_thickness)*math.cos(bottom_shelf_incl)
        shift_z = .5*self.wall_length-(.5*shelves_separation+wallshelf_hole_spacing_y+.5*bottom_shelf_thickness+.5*shelves_y_offset)*math.sin(bottom_shelf_incl)+explode_z
        bottom_shelf = Rotate(bottom_shelf,a=-bottom_shelf_incl*RAD2DEG,v=(0,1,0))
        bottom_shelf = Translate(bottom_shelf,v=(-shift_x,0,shift_z))
        part_list.append(bottom_shelf)

        # Position capillary array (i.e., upper shelf)
        shift_x = (.5*shelves_separation+.5*bottom_shelf_thickness)*math.cos(upper_shelf_incl)
        shift_z = .5*self.wall_length+(.5*shelves_separation-.5*bottom_shelf_thickness+.5*shelves_y_offset)*math.sin(upper_shelf_incl)+explode_z
        for part in upper_shelf_assembly:
            part = Rotate(part,a=-upper_shelf_incl*RAD2DEG,v=(0,1,0))
            part = Translate(part,v=(shift_x,0,shift_z)) 
            part_list.append(part)

        part_list.append(left_wall)
        part_list.append(right_wall)
        part_list.append(foot)

        part_list.append(left_bracket_upper_shelf)
        part_list.append(right_bracket_upper_shelf)
        part_list.append(left_bracket_bottom_shelf)
        part_list.append(right_bracket_bottom_shelf)

        part_list.append(left_bracket_front_foot)
        part_list.append(right_bracket_front_foot)
        part_list.append(left_bracket_back_foot)
        part_list.append(right_bracket_back_foot)

        return part_list

def main():
    # Arrayed enclosure params
    x,y,z = arrayed_enclosure_params['inner_dimensions']
    thickness = arrayed_enclosure_params['wall_thickness']
    # cf. line 82 in arrayed_enclosure.py
    # reposition the plate along (0,0,0)
    upper_shelf_assembly_offset = -0.5*z - 0.5*thickness
    arrayed_enclosure_params['number_of_sensors'] = 5 
    arrayed_enclosure_params['sensor_spacing'] = 2.0*INCH2MM
    arrayed_enclosure_params['array_bottom_overhang'] = 1.0*INCH2MM
    arrayed_enclosure_params['bottom_mount_hole_diam'] = .2*INCH2MM 
    arrayed_enclosure_params['bottom_mount_hole_spacing'] = 1.0*INCH2MM 
    arrayed_enclosure_params['bottom_mount_hole_inset'] = .5*INCH2MM

    # Rack wall dimensions
    shelves_y_offset = .75*INCH2MM-.5*arrayed_enclosure_params['capillary_diam']-\
                       thickness
    upper_shelf_incl = 45*DEG2RAD

    params = {
            'bracket_filename'              :  'stl/8020-4113_fixed-ascii.STL',
            'wallshelf_hole_spacing'        : (1*INCH2MM,.5*INCH2MM),
            'wall_hole_radius'              : .2*INCH2MM,
            'wallfoot_hole_spacing'         : (1*INCH2MM,.5*INCH2MM),
            'upper_shelf_incl'              : upper_shelf_incl,
            'bottom_shelf_incl'             : upper_shelf_incl,
            'upper_shelf_assembly_offset'   : upper_shelf_assembly_offset,
            'arrayed_enclosure_params'      : arrayed_enclosure_params,
            'shelves_separation'            : 3*INCH2MM, #1.25 of capillary + .5 clearance + 1.25 of vial
            'shelves_x_offset'              : 0,
            'shelves_y_offset'              : shelves_y_offset,
            'corner_radius'                 : 1.5,
            'create_wall_dxf'               : True,
            'create_foot_dxf'               : True,
            'create_shelf_dxf'              : True
            }

    rack = Capillary_Rack(params)
    rack.make()
    part_assembly = rack.get_assembly(
            gen_walls=True,
            gen_foot=True,
            gen_ca=True,
            gen_bs=True,
            explode=(0,0,0)
        )
    prog_assembly = SCAD_Prog()
    prog_assembly.fn = 100 # Raised to 100 or otherwise STL won't show
    prog_assembly.add(part_assembly)
    prog_assembly.write('rack_assembly.scad')

    if 0:
        part_projection = rack.get_projection()
        prog_projection = SCAD_Prog()
        prog_projection.fn = 100 # Raised to 100 or otherwise STL won't show
        prog_projection.add(part_projection)
        prog_projection.write('rack_projection.scad')

if __name__ == "__main__":
    main()
