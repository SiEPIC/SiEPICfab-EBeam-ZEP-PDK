import pya
from pya import *

class strip_to_slot(pya.PCellDeclarationHelper):
    """
    The PCell declaration for the strip_to_slot.
    based on https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-21-16-19029&id=259920

    July 24, 2017 - Lukas Chrostowski
    March 17, 2021- Alexander Tofini
    June 13, 2022 - Jaspreet Jhoja
    June 14, 2022 - Lukas Chrostowski
      - reduce the curved waveguide section, increase straight section for lower loss
      - simulated using EME to give 99% efficiency for TE 1550 nm.

    """

    def __init__(self):       
        super(strip_to_slot, self).__init__()
        from SiEPIC.utils import get_technology_by_name
        TECHNOLOGY = get_technology_by_name('SiEPICfab_EBeam_ZEP')
        # declare the parameters
        self.param("silayer", self.TypeLayer, "Si Layer", default = TECHNOLOGY['Si_core'])
        self.param("clad", self.TypeLayer, "Cladding Layer", default = TECHNOLOGY['Si_clad'])
        self.param("r", self.TypeDouble, "Radius", default = 15)
        self.param("w", self.TypeDouble, "Waveguide Width", default = 0.5)
        self.param("rails", self.TypeDouble, "Rails", default=0.25) 
        self.param("slot", self.TypeDouble, "Slot", default=0.1)
        self.param("taper",self.TypeDouble,"Taper Length",default=15.0)   
        self.param("wt", self.TypeDouble, "Terminated Curved Width", default = 0.1)
        self.param("w_cladding", self.TypeDouble, "Cladding, from center", default = 2.25)
        self.param("offset", self.TypeDouble, "Ending Offset for Curved section", default = 1.0)
        self.param("pinrec", self.TypeLayer, "PinRec Layer", default = TECHNOLOGY['PinRec'])
        self.param("devrec", self.TypeLayer, "DevRec Layer", default = TECHNOLOGY['DevRec'])
        self.param("textl", self.TypeLayer, "Text Layer", default = TECHNOLOGY['Text'])
    
    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "strip_to_slot(rails=" + ('%.3f' % self.rails) + ",slot=" + ('%g' % ( self.slot)) + ")"

    def can_create_from_shape_impl(self):
        return False

    def produce_impl(self):
        # This is the main part of the implementation: create the layout
     
        from math import pi, cos, sin, acos, sqrt
        from SiEPIC.utils import arc
        from SiEPIC.utils import arc_xy
        from SiEPIC.extend import to_itype
        from SiEPIC.utils import arc_wg_xy
        from SiEPIC.utils.layout import make_pin
        
        # fetch the parameters
        dbu = self.layout.dbu
        ly = self.layout
        cell = self.cell
        shapes = self.cell.shapes

        LayerSi = self.silayer
        LayerSiN = ly.layer(LayerSi)
        LayerCladN = ly.layer(self.clad)
        LayerPinRecN = ly.layer(self.pinrec)
        LayerDevRecN = ly.layer(self.devrec)

        # Use to_itype() to prevent rounding errors
        w = to_itype(self.w, dbu)
        r = to_itype(self.r, dbu)
        slot = to_itype(self.slot, dbu)
        rails = to_itype(self.rails, dbu)
        taper = to_itype(self.taper,dbu)
        wt = to_itype(self.wt, dbu)
        offset = to_itype(self.offset, dbu)
        w_cladding = to_itype(self.w_cladding, dbu)

        # draw the quarter-circle
        x = 0
        y = r + rails/2 + w + slot
        
        t = Trans(Trans.R0, x, y)
        theta = acos((r-offset)/r)/2/pi*360
        arc_width = sqrt( r**2 - (r-offset)**2)
        self.cell.shapes(LayerSiN).insert(arc_wg_xy(x,y,r+rails/2-wt/2,wt,270,270+theta))
            
        pts = []     
        pts.append(Point.from_dpoint(DPoint(0, w)))
        pts.append(Point.from_dpoint(DPoint(0, 0)))
        pts.append(Point.from_dpoint(DPoint(-taper, w-rails )))
        pts.append(Point.from_dpoint(DPoint(-taper,w)))
        polygon = Polygon(pts)
        shapes(LayerSiN).insert(polygon)
        
        # Create the top left 1/2 waveguide
        wg1 = Polygon([
                Point.from_dpoint(DPoint(-taper, w+slot)),Point.from_dpoint(DPoint(-taper, w+slot+rails)),
                Point.from_dpoint(DPoint(0, w+slot+wt)),Point.from_dpoint(DPoint(0, w+slot))])
        shapes(LayerSiN).insert(wg1)
        
        # Create the waveguide
        wg1 = Box(0, 0, arc_width+wt , w )
        shapes(LayerSiN).insert(wg1)

        # Pin on the slot waveguide side:
        make_pin(self.cell, "opt1", [-taper,w+slot/2], 2*rails+slot,  LayerPinRecN, 180)
        # Pin on the strip waveguide side:
        make_pin(self.cell, "opt2", [int(arc_width+wt),w/2], w,  LayerPinRecN, 0)
        
        # Create the device recognition and cladding layers
        pts = []     
        pts.append(Point.from_dpoint(DPoint(-taper, w+slot/2-w_cladding)))
        pts.append(Point.from_dpoint(DPoint(-taper, w+slot/2+w_cladding)))
        pts.append(Point.from_dpoint(DPoint(arc_width+wt, w/2+w_cladding )))
        pts.append(Point.from_dpoint(DPoint(arc_width+wt, w/2-w_cladding )))
        polygon = Polygon(pts)
        shapes(LayerCladN).insert(polygon)
        shapes(LayerDevRecN).insert(polygon)

        
