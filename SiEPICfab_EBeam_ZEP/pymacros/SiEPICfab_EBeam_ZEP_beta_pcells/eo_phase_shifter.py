import pya
from pya import *


class eo_phase_shifter(pya.PCellDeclarationHelper):
    """
    The PCell declaration for the electro-optic phase shifter
     - single etch silicon
     - 
    
    Authors: Lukas Chrostowski
    """

    def __init__(self):

        # Important: initialize the super class
        super(eo_phase_shifter, self).__init__()
        from SiEPIC.utils import get_technology_by_name, load_Waveguides_by_Tech
        self.technology_name = 'SiEPICfab_EBeam_ZEP'
        TECHNOLOGY = get_technology_by_name(self.technology_name)
        # Load all waveguides
        self.waveguide_types = load_Waveguides_by_Tech(self.technology_name)   

        from SiEPIC._globals import KLAYOUT_VERSION
        if KLAYOUT_VERSION >= 28:
            # Button to launch separate window
            self.param("documentation", self.TypeCallback, "Open documentation in web browser")
            self.param("simulation", self.TypeCallback, "Open simulation in web browser")


        # different configurations
        p = self.param("waveguide_type", self.TypeList, "Waveguide Type", default = self.waveguide_types[0]['name'])
        for wa in self.waveguide_types:
            p.add_choice(wa['name'],wa['name'])
        self.param("path", self.TypeShape, "Path", default = DPath([DPoint(0,0), DPoint(100,0)], 0.5))

        contact_types = ['on Silicon', 'on Glass']
        p = self.param("contact_type", self.TypeList, "Electrical Contact Type", default = contact_types[0])
        for p1 in contact_types:
            p.add_choice(p1,p1)

        # declare the geometry parameters
        self.param("Si_core_to_metal_distance", self.TypeDouble, "Si core to metal distance", default = 4)
        self.param("Si_core_to_SiContact_distance", self.TypeDouble, "Si core to SiContact distance", default = 2)
        self.param("length", self.TypeDouble, "Waveguide length", default = 100)
        self.param("electrode_width", self.TypeDouble, "Electrode Width", default = 4)
                
        self.param("mlayer", self.TypeLayer, "Metal Layer", default = TECHNOLOGY['M1'])
        self.param("pinrec", self.TypeLayer, "PinRec Layer", default = TECHNOLOGY['PinRec'])
        self.param("pinrecm", self.TypeLayer, "PinRecM Layer", default = TECHNOLOGY['PinRecM'])
        self.param("devrec", self.TypeLayer, "DevRec Layer", default = TECHNOLOGY['DevRec'])
        self.param("textl", self.TypeLayer, "Text Layer", default = TECHNOLOGY['Text'])

    def callback(self, layout, name, states):
        ''' Callback for PCell, to launch documentation viewer
                https://www.klayout.de/doc/code/class_PCellDeclaration.html#method9
        '''
        if name == 'documentation':
            url = 'https://docs.google.com/presentation/d/14pH7wLkqFSHueOX42MNu08P7If4OeQmAJQjnR8N_ZmY/preview?rm=minimal'
            import webbrowser
            webbrowser.open_new(url)
        if name == 'simulation':
            url = 'https://colab.research.google.com/drive/1sMWT8SfBujiodLdrMczOAPTm0CkK0qmp'
            import webbrowser
            webbrowser.open_new(url)

    def coerce_parameters_impl(self):
        # update the wavelength length
        self.path = DPath([DPoint(0,0), DPoint(self.length,0)], 0.5)

        
    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "eo_phase_shifter" # (R=" + ('%.3f' % self.r) + ",g=" + ('%g' % (1000*self.g)) + ")"

    def can_create_from_shape_impl(self):
        return False
        
    def produce_impl(self):
        # This is the main part of the implementation: create the layout

        # Make sure the technology name is associated with the layout
        #  PCells don't seem to know to whom they belong!
        if self.layout.technology_name == '':
                self.layout.technology_name = self.technology_name

        # Draw the waveguide geometry, new function in SiEPIC-Tools v0.3.90
        from SiEPIC.utils.layout import layout_waveguide4
        self.waveguide_length = layout_waveguide4(self.cell, self.path, self.waveguide_type)


        from math import pi, cos, sin
        from SiEPIC.utils import arc_wg, arc_wg_xy
        from SiEPIC._globals import PIN_LENGTH
        from SiEPIC.extend import to_itype

        # fetch the parameters
        dbu = self.layout.dbu
        ly = self.layout
        shapes = self.cell.shapes
        
        LayerM = ly.layer(self.mlayer)
        LayerPinRec = ly.layer(self.pinrec)
        LayerPinRecM = ly.layer(self.pinrecm)
        LayerDevRec = ly.layer(self.devrec)
        TextLayer = ly.layer(self.textl)

        # width of waveguide:
        wg_width = 0
        for wa in self.waveguide_types:
            if wa['name'] == self.waveguide_type:
                wg_width = float(wa['width'])
        print (wg_width)

        # draw the metals
        b = DBox(0, self.Si_core_to_metal_distance+wg_width/2, self.length, self.electrode_width+self.Si_core_to_metal_distance+wg_width/2)
        shapes(LayerM).insert(b)
        shapes(LayerM).insert(b.transformed(pya.Trans.M0))

        # Pins on the metals:    
        from SiEPIC.utils.layout import make_pin
        from SiEPIC.extend import to_itype
        make_pin(self.cell, "elec1a", [0,to_itype(self.electrode_width/2+self.Si_core_to_metal_distance+wg_width/2,dbu)], to_itype(self.electrode_width, dbu), LayerPinRecM, 180)
        make_pin(self.cell, "elec1b", [0,-to_itype(self.electrode_width/2+self.Si_core_to_metal_distance+wg_width/2,dbu)], to_itype(self.electrode_width, dbu), LayerPinRecM, 180)
        make_pin(self.cell, "elec2a", [to_itype(self.length, dbu),to_itype(self.electrode_width/2+self.Si_core_to_metal_distance+wg_width/2,dbu)], to_itype(self.electrode_width, dbu), LayerPinRecM, 0)
        make_pin(self.cell, "elec2b", [to_itype(self.length, dbu),-to_itype(self.electrode_width/2+self.Si_core_to_metal_distance+wg_width/2,dbu)], to_itype(self.electrode_width, dbu), LayerPinRecM, 0)
        
        t = Trans(Trans.R0, 0,0)
        text = Text ('Component=eo_phase_shifter', t)
        shape = shapes(LayerDevRec).insert(text)
