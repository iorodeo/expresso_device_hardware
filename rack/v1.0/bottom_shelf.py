from py2scad import *
import sys
sys.path.append('/home/cisco/repos/iorodeo/capillary_sensor_enclosure')
from arrayed_enclosure import Arrayed_Enclosure

cart_floor_dimensions = (1.5*INCH2MM,3*INCH2MM,.125*INCH2MM) 
slot_sx = .25*INCH2MM
slot_sy = 3
rail_sx = .12*INCH2MM
rail_sy = 1.75*INCH2MM
cart_floor_slot_pos  = [( .5*INCH2MM,-.125*INCH2MM-.5*.125*INCH2MM),#right rail
                        (-.5*INCH2MM,-.125*INCH2MM-.5*.125*INCH2MM),#left rail
                        ( .45*INCH2MM, 1.5*INCH2MM),#right front
                        (-.45*INCH2MM, 1.5*INCH2MM),#left front
                        ( .45*INCH2MM, 1.0*INCH2MM-.5*.125*INCH2MM),#right rear
                        (-.45*INCH2MM, 1.0*INCH2MM-.5*.125*INCH2MM)]#left rear
cart_floor_slot_size = [(rail_sx,rail_sy), #for #4 screws
                        (rail_sx,rail_sy),
                        (slot_sx,2*slot_sy), 
                        (slot_sx,2*slot_sy),
                        (slot_sx,slot_sy),
                        (slot_sx,slot_sy)]
cart_backwall_dimensions = (1.5*INCH2MM,1.5*INCH2MM,.125*INCH2MM)
cart_backwall_tabdata = [( .8,.25*INCH2MM,3,'+'),
                         ( .2,.25*INCH2MM,3,'+')]
cart_backwall_hole_list = [(0,0,10)] #vial hole (back)
cart_frontwall_hole_list = [(0,0,14.1)] #vial hole (front)

params = {
          'corner_radius' : 1.5,
          'cart_floor_dimensions' : cart_floor_dimensions,
          'cart_floor_slot_pos'    : cart_floor_slot_pos, 
          'cart_floor_slot_size'   : cart_floor_slot_size,
          'cart_backwall_dimensions' : cart_backwall_dimensions,
          'cart_backwall_tabdata'    : cart_backwall_tabdata, 
          'cart_backwall_hole_list'    : cart_backwall_hole_list, 
          'cart_frontwall_dimensions' : cart_backwall_dimensions,
          'cart_frontwall_tabdata' : cart_backwall_tabdata,
          'cart_frontwall_hole_list' : cart_backwall_hole_list,
         }

class Upper_Shelf(object):
    def __init__(self):
        from make_enclosure import params
        x,y,z = params['inner_dimensions']
        thickness = params['wall_thickness']
        # cf. line 82 in arrayed_enclosure.py
        # reposition the plate along (0,0,0)
        self.assembly_bottom_offset = -0.5*z - 0.5*thickness
        params['number_of_sensors'] = 5
        params['sensor_spacing'] = INCH2MM*2.0
        params['array_bottom_overhang'] = 1.0*INCH2MM
        params['bottom_mount_hole_diam'] = 0.2010*INCH2MM
        params['bottom_mount_hole_spacing'] = INCH2MM
        params['bottom_mount_hole_inset'] = 0.5*INCH2MM
        enclosure = Arrayed_Enclosure(params)
        enclosure.make()
        self.enclosure = enclosure

class Bottom_Shelf(object):
    def __init__(self, params):
        self.params = params

    def __make_floor(self):
        x,y,z = self.params['floor_dimensions']
        hole_list = self.params['floor_hole_list']
        corner_radius = self.params['corner_radius']
        self.floor = plate_w_holes(x,y,z,hole_list,radius=corner_radius)
        self.thickness = z

    def __make_cart_floor(self):
        x,y,z = self.params['cart_floor_dimensions']
        slot_list = []
        for pos,size in zip(self.params['cart_floor_slot_pos'],self.params['cart_floor_slot_size']):
            slot_list.append((pos,size))
        corner_radius = self.params['corner_radius']
        params = {
            'size'   : (x,y,z),    
            'radius' : corner_radius, 
            'slots'  : slot_list,  
            }
        cart_floor = Plate_W_Slots(params)
        self.cart_floor = cart_floor.make()

    def __make_cart_backwall(self):
        x,y,z = self.params['cart_backwall_dimensions']
        xz_neg = self.params['cart_backwall_tabdata'] 
        corner_radius = self.params['corner_radius']

        params = {
            'size' : (x,y,z),
            'radius' : corner_radius, 
            'xz+'  : [],
            'xz-'  : xz_neg,
            'yz+'  : [],
            'yz-'  : [],
            'hole_list' : self.params['cart_backwall_hole_list']
            }

        cart_backwall = Plate_W_Tabs(params)
        self.cart_backwall = cart_backwall.make()

    def __make_cart_frontwall(self):
        x,y,z = self.params['cart_frontwall_dimensions']
        xz_neg = self.params['cart_frontwall_tabdata'] 
        corner_radius = self.params['corner_radius']

        params = {
            'size' : (x,y,z),
            'radius' : corner_radius, 
            'xz+'  : [],
            'xz-'  : xz_neg,
            'yz+'  : [],
            'yz-'  : [],
            'hole_list' : self.params['cart_frontwall_hole_list']
            }

        cart_frontwall = Plate_W_Tabs(params)
        self.cart_frontwall = cart_frontwall.make()
        
    def make(self):
        self.__make_floor()
        self.__make_cart_floor()
        self.__make_cart_backwall()
        self.__make_cart_frontwall()

    def get_assembly(self,**kwargs):
        assembly_options= {
                'explode' : (0,0,0),
                }
        assembly_options.update(kwargs)
        explode = assembly_options['explode']
        explode_x, explode_y, explode_z = explode
        part_list = []
        
        # Shelf bottom (floor)
        floor_x,floor_y,floor_z = self.params['floor_dimensions']
        part_list.append(self.floor)
        cart_pos_y = self.params['cart_pos_y']
        for i in range(self.params['num_sensors']):
            shift_y = cart_pos_y[i]
            # Cart floor
            cart_floor_x,cart_floor_y,cart_floor_z = self.params['cart_floor_dimensions']
            shift_z = .5*floor_z+.5*cart_floor_z
            cart_floor = Rotate(self.cart_floor,a=-90,v=(0,0,1))
            cart_floor = Translate(cart_floor,v=(0,shift_y,shift_z))
            part_list.append(cart_floor)

            # Cart front wall
            cart_frontwall = Rotate(self.cart_frontwall,a=90,v=(0,0,1))
            cart_frontwall = Rotate(cart_frontwall,a=90,v=(0,1,0))
            x,y,z = self.params['cart_frontwall_dimensions']
            shift_x = .5*cart_floor_y-.5*.125*INCH2MM
            shift_z = .5*y+.5*cart_floor_z+shift_z
            cart_frontwall = Translate(cart_frontwall,v=(shift_x,shift_y,shift_z))
            part_list.append(cart_frontwall)

            # Cart back wall
            cart_backwall = Rotate(self.cart_backwall,a=90,v=(0,0,1))
            cart_backwall = Rotate(cart_backwall,a=90,v=(0,1,0))
            x,y,z = self.params['cart_backwall_dimensions']
            shift_x = .5*cart_floor_y-.5*.125*INCH2MM-.5*INCH2MM
            cart_backwall = Translate(cart_backwall,v=(shift_x,shift_y,shift_z))
            part_list.append(cart_backwall)

        return part_list

    def get_projection(self,spacing=(5,5)):
        spacing_x,spacing_y = spacing
        part_list = []
        
        # Shelf bottom (floor)
        floor_x,floor_y,floor_z = self.params['floor_dimensions']
        floor = Rotate(self.floor,a=90,v=(0,0,1))
        part_list.append(floor)
        cart_pos_y = self.params['cart_pos_y']
        tabdata = self.params['cart_frontwall_tabdata'] 
        tabdata = tabdata[0]
        pos,ext,size,d = tabdata

        for i in range(self.params['num_sensors']):
            shift_x = cart_pos_y[i]

            # Cart floor
            cart_x,cart_y,cart_z = self.params['cart_floor_dimensions']
            shift_y = .5*floor_x+.5*cart_y+spacing_y
            cart_floor = Translate(self.cart_floor,v=(shift_x,shift_y,0))
            part_list.append(cart_floor)

            # Cart front wall
            fw_x,fw_y,fw_z = self.params['cart_frontwall_dimensions']
            shift_y = shift_y+.5*cart_y+.5*fw_y+spacing_y
            cart_frontwall = Rotate(self.cart_frontwall,a=180,v=(0,0,1))
            cart_frontwall = Translate(cart_frontwall,v=(shift_x,shift_y,0))
            part_list.append(cart_frontwall)

            # Cart back wall
            bw_x,bw_y,bw_z = self.params['cart_backwall_dimensions']
            shift_y = shift_y+.5*fw_y+.5*bw_y+spacing_y+size
            cart_backwall = Rotate(self.cart_backwall,a=180,v=(0,0,1))
            cart_backwall = Translate(cart_backwall,v=(shift_x,shift_y,0))
            part_list.append(cart_backwall)

        return part_list

def main():
    enclosure = Upper_Shelf().enclosure
    floor_x, floor_y = enclosure.array_bottom_size
    floor_z = .25*INCH2MM
    sensor_pos_y = enclosure.get_array_y_values();
    num_sensors = enclosure.params['number_of_sensors']
    floor_hole_list = [( .5*INCH2MM,.5*floor_y-.5*INCH2MM,.2*INCH2MM), #bracket holes
                       (-.5*INCH2MM,.5*floor_y-.5*INCH2MM,.2*INCH2MM),
                       ( .5*INCH2MM,-.5*floor_y+.5*INCH2MM,.2*INCH2MM),
                       (-.5*INCH2MM,-.5*floor_y+.5*INCH2MM,.2*INCH2MM)]
    for i in range(num_sensors):
        shift_y = sensor_pos_y[i]
        floor_hole_list.append((.75*INCH2MM-.5*.152*INCH2MM-.5*.125*INCH2MM, .5*INCH2MM+shift_y,.15*INCH2MM)),#rail holes
        floor_hole_list.append((.75*INCH2MM-.5*.152*INCH2MM-.5*.125*INCH2MM,-.5*INCH2MM+shift_y,.15*INCH2MM))#.152 needed for inserts

    params['floor_dimensions'] = (floor_x,floor_y,floor_z)
    params['floor_hole_list'] = floor_hole_list 
    params['num_sensors'] = num_sensors
    params['cart_pos_y'] = sensor_pos_y

    floor = Bottom_Shelf(params)
    floor.make()
    part_assembly = floor.get_assembly(explode=(0,0,0))
    part_assembly = floor.get_projection()
    prog_assembly = SCAD_Prog()
    prog_assembly.fn = 100 # Raised to 100 or otherwise STL won't show
    prog_assembly.add(part_assembly)
    prog_assembly.write('bottom_shelf.scad')

if __name__ == "__main__":
    main()
